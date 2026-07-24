#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
geocode_pois.py — 用腾讯地图 WebService 批量重算全部 POI 的官方 GCJ02 坐标（一劳永逸）。

流程：
  1. 从 ~/.tencentmap/tempkey.json 读取刚申请的临时体验 Key（绕过 .env 中已耗尽的正式 Key）。
  2. 对每个 POI 调用 TmapClient.poi_search(keyword, region=城市) 取官方坐标（GCJ02）。
  3. 边界合理性校验（大连 / 沈阳 各自经纬度范围）。
  4. 打印 old -> new 对照表（含命中名称、距离偏移，便于人工目检）。
  5. --write 时：回写 poi_data.json，并用正则同步 cloud.html / map.html 内联 POIS 的 lat/lng。

用法：
  python geocode_pois.py            # 仅预览，不落盘
  python geocode_pois.py --write    # 预览 + 写回三个文件
  python geocode_pois.py --key XXX  # 显式指定 Key（覆盖 tempkey.json）
"""
import os
import re
import sys
import json
import math
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_SCRIPTS = os.path.join(os.path.expanduser("~"),
    ".workbuddy/skills/tencentmap-map-assistant/scripts")
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from tmap_client import TmapClient  # noqa: E402

POI_JSON = os.path.join(HERE, "poi_data.json")
CLOUD_HTML = os.path.join(HERE, "cloud.html")
MAP_HTML = os.path.join(HERE, "map.html")

# 城市中文名（poi_search 的 region 参数）
REGION = {"dl": "大连", "sy": "沈阳"}

# 搜索词：默认用 POI 名称，复杂名称单独覆盖为更稳的官方叫法
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

# 合理性边界（GCJ02）
BOUNDS = {
    "dl": (38.80, 39.12, 121.45, 121.85),   # lat_min, lat_max, lng_min, lng_max
    "sy": (41.68, 41.92, 123.28, 123.58),
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
    p1 = math.radians(a_lat); p2 = math.radians(b_lat)
    dp = math.radians(b_lat - a_lat); dl = math.radians(b_lng - a_lng)
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="写回 poi_data.json 与两个 HTML")
    ap.add_argument("--key", default=None, help="显式 Key，覆盖 tempkey.json")
    args = ap.parse_args()

    key = args.key or load_tempkey()
    if not key:
        print("❌ 未找到临时 Key：请先完成 send_code -> create_key -> save_config 流程")
        sys.exit(1)
    print("🔑 使用 Key 前缀:", key[:6] + "...")

    client = TmapClient(key=key)  # 显式传入，绕过 .env 中已耗尽的正式 Key

    pois = json.load(open(POI_JSON, "r", encoding="utf-8"))
    report = []
    for p in pois:
        pid = p["id"]; city = p["city"]
        kw = SEARCH.get(pid, p["name"])
        region = REGION.get(city, "大连")
        try:
            resp = client.poi_search(kw, region=region)
            data = resp.get("data") or []
            if not data:
                report.append((pid, p["name"], kw, p["lat"], p["lng"], None, None, "⚠️ 无结果", 0))
                continue
            top = data[0]
            loc = top.get("location", {})
            nlat = float(loc.get("lat")); nlng = float(loc.get("lng"))
            title = top.get("title", "")
            lat_min, lat_max, lng_min, lng_max = BOUNDS[city]
            in_bounds = (lat_min <= nlat <= lat_max) and (lng_min <= nlng <= lng_max)
            dist = haversine(p["lat"], p["lng"], nlat, nlng)
            flag = "✅" if in_bounds else "⚠️ 越界"
            report.append((pid, p["name"], kw, p["lat"], p["lng"], nlat, nlng, flag, dist))
            p["_new_lat"] = nlat; p["_new_lng"] = nlng; p["_title"] = title
        except Exception as e:
            report.append((pid, p["name"], kw, p["lat"], p["lng"], None, None, f"❌ {e}", 0))

    # 打印对照表
    print("\n%-16s %-22s %-10s %s" % ("id", "name", "flag", "offset(m)"))
    print("-" * 70)
    for pid, name, kw, olat, olng, nlat, nlng, flag, dist in report:
        if nlat is None:
            print("%-16s %-22s %s" % (pid, name, flag))
        else:
            print("%-16s %-22s %-8s %8.0f" % (pid, name, flag, dist))
    print()
    for pid, name, kw, olat, olng, nlat, nlng, flag, dist in report:
        if nlat is None:
            continue
        print("%-16s old=(%.6f,%.6f) new=(%.6f,%.6f) hit=%s" %
              (pid, olat, olng, nlat, nlng, pid in [r[0] for r in report] and "" or ""))

    if not args.write:
        print("\n（预览模式，未落盘。加 --write 写回 poi_data.json 与两个 HTML）")
        return

    # 写回 poi_data.json
    out = []
    for p in pois:
        if "_new_lat" in p:
            p["lat"] = round(p["_new_lat"], 6)
            p["lng"] = round(p["_new_lng"], 6)
            p["src"] = "tencent_poi"
            del p["_new_lat"]; del p["_new_lng"]
            if "_title" in p: del p["_title"]
        out.append(p)
    json.dump(out, open(POI_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("✅ 已写回 poi_data.json")

    # 同步两个 HTML 内联 POIS
    for html_path in (CLOUD_HTML, MAP_HTML):
        if not os.path.exists(html_path):
            print("⚠️ 跳过不存在:", html_path); continue
        s = open(html_path, "r", encoding="utf-8").read()
        for p in out:
            pat = re.compile(
                r'("id":"%s"[^}]*"lat":)\s*[-0-9.]+(\s*,\s*"lng":)\s*[-0-9.]+'
                % re.escape(p["id"]))
            repl = r'\g<1>%s\g<2>%s' % (repr(p["lat"]), repr(p["lng"]))
            s, n = pat.subn(repl, s)
            print("  %s <- %s 替换 %d 处" % (os.path.basename(html_path), p["id"], n))
        open(html_path, "w", encoding="utf-8").write(s)
    print("✅ 已同步 cloud.html / map.html")


if __name__ == "__main__":
    main()
