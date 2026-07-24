#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
osm_geocode.py — 无 Key 方案：用 OpenStreetMap(Photon) 批量地理编码全部 POI，
再把 WGS84 转 GCJ02，写回 poi_data.json + cloud.html + map.html。

- 不依赖任何 API Key / 配额，免费、即时。
- 已人工核验的 3 个点（银沙滩/大连北站/棒棰岛）直接保留原值。
- 置信度过滤：同城内坐标高度重复（城市中心兜底）、越界、或相对旧值偏移>5km 的，
  一律「保留旧值」，绝不拿城市中心点覆盖真实景点。

用法：
  python osm_geocode.py            # 预览，打印 old -> new 对照 + 置信度
  python osm_geocode.py --write    # 预览 + 写回三文件
"""
import os
import re
import sys
import json
import math
import time
import argparse
import urllib.request
import urllib.parse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
POI_JSON = os.path.join(HERE, "poi_data.json")
CLOUD_HTML = os.path.join(HERE, "cloud.html")
MAP_HTML = os.path.join(HERE, "map.html")

REGION = {"dl": "大连", "sy": "沈阳"}
# 已人工核验（腾讯官方）的点 —— 保留，不被 OSM 覆盖
KEEP_VERIFIED = {"yinshatan", "dalian_nb", "bangchuidao"}

SEARCH = {
    "dalian_airport": "大连周水子国际机场",
    "atu_hotel": "亚朵酒店 港湾广场",
    "binhai_road": "星海湾跨海大桥",
    "lianhua_mt": "莲花山观景台",
    "yinshatan": "银沙滩",
    "xinghai_sq": "星海广场",
    "laohutan": "老虎滩海洋公园",
    "bangchuidao": "棒棰岛景区",
    "yuren_matou": "渔人码头",
    "donggang": "东港",
    "venice": "威尼斯水城",
    "russia_st": "俄罗斯风情街",
    "zhongshan_sq": "中山广场",
    "qingniwa": "青泥洼桥",
    "dalian_nb": "大连北站",
    "shenyang_st": "沈阳站",
    "taiyuan_st": "丽柏酒店 太原街",
    "gugong": "沈阳故宫",
    "shuaifu": "张氏帅府",
    "zhongjie": "中街步行街",
    "xita": "西塔",
    "918": "九一八历史博物馆",
    "beiling": "北陵公园",
    "shenyang_nb": "沈阳北站",
}

# 每个 POI 的“特征词”：匹配结果的名称/地址里必须包含其中之一，才算真正命中该 POI。
# 用于剔除 Photon 把查询退化成“城市中心点”的兜底结果（如 青泥洼桥→大连）。
CORE = {
    "dalian_airport": ["周水子"],
    "atu_hotel": ["港湾广场", "亚朵"],
    "binhai_road": ["星海湾大桥", "跨海大桥"],
    "lianhua_mt": ["莲花山"],
    "xinghai_sq": ["星海广场"],
    "laohutan": ["老虎滩"],
    "yuren_matou": ["渔人码头"],
    "donggang": ["东港"],
    "venice": ["威尼斯"],
    "russia_st": ["俄罗斯风情街", "团结街"],
    "zhongshan_sq": ["中山广场"],
    "qingniwa": ["青泥洼"],
    "shenyang_st": ["沈阳站"],
    "taiyuan_st": ["太原街", "丽柏"],
    "gugong": ["故宫", "沈阳故宫"],
    "shuaifu": ["帅府", "张学良", "张氏"],
    "zhongjie": ["中街"],
    "xita": ["西塔"],
    "918": ["九一八"],
    "beiling": ["北陵"],
    "shenyang_nb": ["沈阳北站"],
}

BOUNDS = {
    "dl": (38.80, 39.12, 121.45, 121.85),
    "sy": (41.68, 41.92, 123.28, 123.58),
}
CITY_TOKENS = {
    "dl": ["大连", "Dalian", "辽宁", "Liaoning"],
    "sy": ["沈阳", "Shenyang", "辽宁", "Liaoning"],
}
UA = "DalianTripGeocode/1.0 (travel-planning script; contact: traveler@example.com)"


# ---------- WGS84 -> GCJ02 ----------
def _out_of_china(lat, lng):
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def _t_lat(x, y):
    r = (-100.0 + 2.0*x + 3.0*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x)))
    r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi)) * 2.0/3.0
    r += (20.0*math.sin(y*math.pi) + 40.0*math.sin(y/3.0*math.pi)) * 2.0/3.0
    r += (160.0*math.sin(y/12.0*math.pi) + 320.0*math.sin(y*math.pi/30.0)) * 2.0/3.0
    return r


def _t_lng(x, y):
    r = (300.0 + x + 2.0*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x)))
    r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi)) * 2.0/3.0
    r += (20.0*math.sin(x*math.pi) + 40.0*math.sin(x/3.0*math.pi)) * 2.0/3.0
    r += (150.0*math.sin(x/12.0*math.pi) + 300.0*math.sin(x/30.0*math.pi)) * 2.0/3.0
    return r


def wgs84_to_gcj02(lat, lng):
    if _out_of_china(lat, lng):
        return lat, lng
    dlat = _t_lat(lng - 105.0, lat - 35.0)
    dlng = _t_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - 0.00669342162296594323 * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((6378245.0 * (1 - 0.00669342162296594323)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (6378245.0 / sqrtmagic * math.cos(radlat) * math.pi)
    return lat + dlat, lng + dlng


def haversine(a_lat, a_lng, b_lat, b_lng):
    R = 6371000.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = math.radians(b_lat - a_lat), math.radians(b_lng - a_lng)
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))


def photon_geocode(query):
    # Photon(komoot) 是 OSM 的免费地理编码接口，无需 Key。
    # 注：nominatim.openstreetmap.org 在本环境不可达，改用 photon.komoot.io。
    # Photon 偶发空结果/超时，重试一次以降低抖动。
    url = "https://photon.komoot.io/api/?" + urllib.parse.urlencode({"q": query, "limit": "1"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for _ in range(2):
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                d = json.loads(resp.read().decode("utf-8"))
            feats = d.get("features") or []
            if feats:
                f = feats[0]
                lon, lat = f["geometry"]["coordinates"]
                props = f.get("properties", {})
                disp = " ".join(str(props.get(k, "")) for k in ("name", "city", "state", "country") if props.get(k))
                return lat, lon, disp
        except Exception:
            pass
        time.sleep(1.5)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    pois = json.load(open(POI_JSON, "r", encoding="utf-8"))

    # —— 第一遍：取候选坐标 ——
    cands = []
    for p in pois:
        pid, city = p["id"], p["city"]
        q = SEARCH.get(pid, p["name"]) + " " + REGION[city]
        if pid in KEEP_VERIFIED:
            cands.append((p, pid, city, q, None, None, "KEEP"))
            continue
        try:
            g = photon_geocode(q)
            time.sleep(1.0)
            if not g:
                cands.append((p, pid, city, q, None, None, "NONE"))
                continue
            wlat, wlng, disp = g
            glat, glng = wgs84_to_gcj02(wlat, wlng)
            cands.append((p, pid, city, q, glat, glng, disp))
        except Exception as e:
            cands.append((p, pid, city, q, None, None, "ERR:%s" % e))

    # —— 检测“城市中心兜底”：同城内坐标高度重复 ——
    seen = defaultdict(list)
    for p, pid, city, q, glat, glng, disp in cands:
        if glat is None:
            continue
        key = (city, round(glat, 4), round(glng, 4))
        seen[key].append(pid)
    centroid_pids = set()
    for key, ids in seen.items():
        if len(ids) >= 2:
            centroid_pids.update(ids)

    # —— 第二遍：定稿 + 置信度 ——
    report = []
    decides = {}      # pid -> (glat, glng) 采用新值；None = 保留旧值
    disp_map = {}
    for p, pid, city, q, glat, glng, disp in cands:
        olat, olng = p["lat"], p["lng"]
        if pid in KEEP_VERIFIED:
            report.append((pid, p["name"], "保留(已核验)", olat, olng, olat, olng, "✅保留", 0.0))
            decides[pid] = None
            continue
        if glat is None:
            report.append((pid, p["name"], q, olat, olng, None, None, "⚠️无结果/异常", 0.0))
            decides[pid] = None
            continue
        dist = haversine(olat, olng, glat, glng)
        lat_min, lat_max, lng_min, lng_max = BOUNDS[city]
        in_bounds = (lat_min <= glat <= lat_max) and (lng_min <= glng <= lng_max)
        hit_city = any(tok in disp for tok in CITY_TOKENS[city])
        has_core = any(tok in disp for tok in CORE.get(pid, []))
        if pid in centroid_pids:
            flag = "🟡保留旧(OSM命中城市中心)"
            decides[pid] = None
        elif not in_bounds:
            flag = "⚠️越界→保留旧"
            decides[pid] = None
        elif dist > 5000:
            flag = "🟡保留旧(偏移>5km)"
            decides[pid] = None
        elif in_bounds and hit_city and has_core:
            flag = "✅高"
            decides[pid] = (glat, glng)
        else:
            flag = "🟡保留旧(未命中POI名)"
            decides[pid] = None
        report.append((pid, p["name"], q, olat, olng, glat, glng, flag, dist))
        disp_map[pid] = disp

    # —— 打印 ——
    print("\n%-15s %-20s %-24s %9s" % ("id", "name", "conf", "Δ(m)"))
    print("-" * 80)
    for pid, name, q, olat, olng, nlat, nlng, flag, dist in report:
        if nlat is None:
            print("%-15s %-20s %s" % (pid, name, flag))
        else:
            print("%-15s %-20s %-24s %8.0f" % (pid, name, flag, dist))
    print()
    for pid, name, q, olat, olng, nlat, nlng, flag, dist in report:
        if nlat is None or pid in KEEP_VERIFIED:
            continue
        print("%-15s old=(%.6f,%.6f) new=(%.6f,%.6f)  %s" %
              (pid, olat, olng, nlat, nlng, flag))
        print("    q=%-36s match=%s" % (q[:36], disp_map.get(pid, "")))

    if not args.write:
        print("\n（预览模式，未落盘。加 --write 写回 poi_data.json 与两个 HTML）")
        return

    # —— 写回 ——
    out = []
    for p in pois:
        pid = p["id"]
        d = decides.get(pid)
        if d is not None:
            p["lat"] = round(d[0], 6)
            p["lng"] = round(d[1], 6)
            p["src"] = "osm_gcj02"
        out.append(p)
    json.dump(out, open(POI_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("✅ 已写回 poi_data.json")

    for html_path in (CLOUD_HTML, MAP_HTML):
        if not os.path.exists(html_path):
            print("⚠️ 跳过:", html_path); continue
        s = open(html_path, "r", encoding="utf-8").read()
        for p in out:
            pat = re.compile(r'("id":"%s"[^}]*"lat":)\s*[-0-9.]+(\s*,\s*"lng":)\s*[-0-9.]+' % re.escape(p["id"]))
            repl = r'\g<1>%s\g<2>%s' % (repr(p["lat"]), repr(p["lng"]))
            s, n = pat.subn(repl, s)
            print("  %s <- %s 替换 %d 处" % (os.path.basename(html_path), p["id"], n))
        open(html_path, "w", encoding="utf-8").write(s)
    print("✅ 已同步 cloud.html / map.html")


if __name__ == "__main__":
    main()
