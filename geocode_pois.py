#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
geocode_pois.py — 用腾讯地图 WebService 批量重算全部 POI 的官方 GCJ02 坐标（一劳永逸）。

流程：
  1. 取 Key：优先 --key 参数，否则读 ~/.tencentmap/tempkey.json（临时体验 Key）。
     （注意：tmap_client 会先读 skill 包内 .env 的正式 Key，但那把已配额耗尽，故必须显式传入。）
  2. 对每个 POI 调 TmapClient.poi_search(keyword, region=城市) 取官方坐标（GCJ02）。
  3. 置信度过滤（与 osm_geocode.py 同款）：同城坐标重复=城市中心兜底 / 越界 / 偏移>5km /
     未命中 POI 特征词 → 一律保留旧值，绝不拿城市中心点覆盖真实景点。
  4. 打印 old -> new 对照表；--write 时回写 poi_data.json 并同步 cloud.html / map.html。

用法：
  python geocode_pois.py --key XXXX          # 预览（用显式 Key）
  python geocode_pois.py --key XXXX --write  # 预览 + 写回三文件
  python geocode_pois.py                      # 预览（用 tempkey.json 里的 Key）
"""
import os
import re
import sys
import json
import math
import time
import argparse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_SCRIPTS = os.path.join(os.path.expanduser("~"),
    ".workbuddy/skills/tencentmap-map-assistant/scripts")
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from tmap_client import TmapClient  # noqa: E402

POI_JSON = os.path.join(HERE, "poi_data.json")
CLOUD_HTML = os.path.join(HERE, "cloud.html")
MAP_HTML = os.path.join(HERE, "map.html")

REGION = {"dl": "大连", "sy": "沈阳"}

SEARCH = {
    "dalian_airport": "大连周水子国际机场",
    "atu_hotel": "亚朵酒店(港湾广场)",
    "binhai_road": "星海湾跨海大桥观景台",
    "lianhua_mt": "莲花山观景台",
    "yinshatan": "银沙滩公园",
    "xinghai_sq": "星海广场",
    "laohutan": "老虎滩海洋公园",
    "bangchuidao": "棒棰岛景区",
    "yuren_matou": "大连渔人码头",
    "donggang": "大连东港",
    "venice": "大连威尼斯水城",
    "russia_st": "俄罗斯风情街(大连)",
    "zhongshan_sq": "中山广场(大连)",
    "qingniwa": "青泥洼桥",
    "dalian_nb": "大连北站",
    "shenyang_st": "沈阳站",
    "taiyuan_st": "沈阳丽柏酒店太原街",
    "gugong": "沈阳故宫",
    "shuaifu": "张氏帅府博物馆",
    "zhongjie": "中街步行街",
    "xita": "西塔(沈阳)",
    "918": "九一八历史博物馆",
    "beiling": "北陵公园",
    "shenyang_nb": "沈阳北站",
}

# 每个 POI 的“特征词”：匹配结果的名称/地址里必须包含其中之一，才算真正命中该 POI。
CORE = {
    "dalian_airport": ["周水子", "机场"],
    "atu_hotel": ["港湾广场", "亚朵"],
    "binhai_road": ["星海湾", "跨海大桥"],
    "lianhua_mt": ["莲花山"],
    "yinshatan": ["银沙滩"],
    "xinghai_sq": ["星海广场"],
    "laohutan": ["老虎滩"],
    "bangchuidao": ["棒棰岛"],
    "yuren_matou": ["渔人码头"],
    "donggang": ["东港"],
    "venice": ["威尼斯", "东方水城"],
    "russia_st": ["俄罗斯风情街", "团结街"],
    "zhongshan_sq": ["中山广场"],
    "qingniwa": ["青泥洼"],
    "dalian_nb": ["大连北站", "北站"],
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


def load_tempkey():
    p = os.path.join(os.path.expanduser("~"), ".tencentmap", "tempkey.json")
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        entries = list(data.values())
    elif isinstance(data, list):
        entries = data
    else:
        return None
    for e in entries:
        if isinstance(e, dict) and e.get("key"):
            return e["key"]
    return None


def haversine(a_lat, a_lng, b_lat, b_lng):
    R = 6371000.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = math.radians(b_lat - a_lat), math.radians(b_lng - a_lng)
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="写回 poi_data.json 与两个 HTML")
    ap.add_argument("--key", default=None, help="显式 Key，覆盖 tempkey.json")
    args = ap.parse_args()

    key = args.key or load_tempkey()
    if not key:
        print("❌ 未找到可用 Key：请加 --key，或先完成 send_code -> create_key -> save_config 流程")
        sys.exit(1)
    print("🔑 使用 Key 前缀:", key[:6] + "...")

    client = TmapClient(key=key)  # 显式传入，绕过 .env 中已耗尽的正式 Key

    pois = json.load(open(POI_JSON, "r", encoding="utf-8"))

    # —— 第一遍：取候选坐标 ——
    cands = []
    for p in pois:
        pid, city = p["id"], p["city"]
        kw = SEARCH.get(pid, p["name"])
        region = REGION.get(city, "大连")
        try:
            resp = client.poi_search(kw, region=region)
            time.sleep(0.3)
            data = resp.get("data") or []
            if not data:
                cands.append((p, pid, city, kw, None, None, "NONE"))
                continue
            top = data[0]
            loc = top.get("location", {})
            nlat = float(loc.get("lat")); nlng = float(loc.get("lng"))
            title = top.get("title", "")
            addr = top.get("address", "")
            cands.append((p, pid, city, kw, nlat, nlng, title + " " + addr))
        except Exception as e:
            cands.append((p, pid, city, kw, None, None, "ERR:%s" % e))

    # —— 检测“城市中心兜底”：同城内坐标高度重复 ——
    seen = defaultdict(list)
    for p, pid, city, kw, nlat, nlng, disp in cands:
        if nlat is None:
            continue
        key2 = (city, round(nlat, 4), round(nlng, 4))
        seen[key2].append(pid)
    centroid_pids = set()
    for k, ids in seen.items():
        if len(ids) >= 2:
            centroid_pids.update(ids)

    # —— 第二遍：定稿 + 置信度 ——
    report = []
    decides = {}
    disp_map = {}
    for p, pid, city, kw, nlat, nlng, disp in cands:
        olat, olng = p["lat"], p["lng"]
        if nlat is None:
            report.append((pid, p["name"], kw, olat, olng, None, None, "⚠️无结果/异常", 0.0))
            decides[pid] = None
            continue
        dist = haversine(olat, olng, nlat, nlng)
        lat_min, lat_max, lng_min, lng_max = BOUNDS[city]
        in_bounds = (lat_min <= nlat <= lat_max) and (lng_min <= nlng <= lng_max)
        hit_city = any(tok in disp for tok in CITY_TOKENS[city])
        has_core = any(tok in disp for tok in CORE.get(pid, []))
        if pid in centroid_pids:
            flag = "🟡保留旧(命中城市中心)"
            decides[pid] = None
        elif not in_bounds:
            flag = "⚠️越界→保留旧"
            decides[pid] = None
        elif dist > 5000:
            flag = "🟡保留旧(偏移>5km)"
            decides[pid] = None
        elif in_bounds and has_core:
            flag = "✅高"
            decides[pid] = (nlat, nlng)
        else:
            flag = "🟡保留旧(未命中POI名)"
            decides[pid] = None
        report.append((pid, p["name"], kw, olat, olng, nlat, nlng, flag, dist))
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
        if nlat is None:
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
            p["src"] = "tencent_poi"
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
