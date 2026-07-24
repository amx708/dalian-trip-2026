# -*- coding: utf-8 -*-
"""用腾讯地图 WebService 地理编码，把攻略里的景点/酒店/枢纽解析成真实坐标。
Key 用用户提供的正式 Key；若某点编码失败，回退到手写的近似坐标（知名地标，误差很小）。
输出 poi_data.js 供 cloud.html 的地图标签页使用。"""
import json, urllib.parse, urllib.request, time, sys

KEY = "IACBZ-D3BLJ-NMWFG-XVZOS-BYINK-GMFRD"

# 回退坐标（GCJ02，手写近似，知名地标）
FALLBACK = {
    "dalian_airport": (38.9592, 121.5393),
    "atu_hotel":     (38.9220, 121.6430),
    "binhai_road":   (38.8680, 121.5600),
    "lianhua_mt":    (38.8660, 121.5830),
    "yinshatan":     (38.8750, 121.5900),
    "xinghai_sq":    (38.8790, 121.6020),
    "laohutan":      (38.8830, 121.6320),
    "bangchuidao":   (38.8780, 121.6670),
    "yuren_matou":   (38.8860, 121.6450),
    "donggang":      (38.9250, 121.6550),
    "venice":        (38.9280, 121.6580),
    "russia_st":     (38.9160, 121.6220),
    "zhongshan_sq":  (38.9180, 121.6300),
    "qingniwa":      (38.9140, 121.6280),
    "dalian_nb":     (39.0090, 121.6860),
    "shenyang_st":   (41.7930, 123.4070),
    "taiyuan_st":    (41.7910, 123.4000),
    "gugong":        (41.7960, 123.4560),
    "shuaifu":       (41.7940, 123.4590),
    "zhongjie":      (41.7990, 123.4630),
    "xita":          (41.8000, 123.3850),
    "918":           (41.8390, 123.4620),
    "beiling":       (41.8490, 123.4280),
    "shenyang_nb":   (41.8170, 123.4400),
}

# (id, 显示名, 城市, 查询地址, region, day, order, kind)
POIS = [
    # ===== 大连 =====
    ("dalian_airport", "大连周水子机场", "dl", "大连周水子国际机场", "大连", "T", 0, "transport"),
    ("atu_hotel",     "亚朵酒店(港湾广场)", "dl", "大连港湾广场", "大连", "1", 1, "hotel"),
    ("binhai_road",   "滨海路·跨海大桥观景台", "dl", "滨海路 大连", "大连", "1", 2, "spot"),
    ("lianhua_mt",    "莲花山观景台", "dl", "莲花山观景台 大连", "大连", "1", 3, "spot"),
    ("yinshatan",     "银沙滩", "dl", "银沙滩 大连", "大连", "1", 4, "spot"),
    ("xinghai_sq",    "星海广场", "dl", "星海广场 大连", "大连", "1", 5, "spot"),
    ("laohutan",      "老虎滩海洋公园", "dl", "老虎滩海洋公园 大连", "大连", "2", 1, "spot"),
    ("bangchuidao",   "棒棰岛", "dl", "棒棰岛 大连", "大连", "2", 2, "spot"),
    ("yuren_matou",   "渔人码头·品海楼", "dl", "大连渔人码头", "大连", "2", 3, "food"),
    ("donggang",      "东港·中央大道", "dl", "大连东港", "大连", "3", 1, "spot"),
    ("venice",        "威尼斯水城", "dl", "大连威尼斯水城", "大连", "3", 2, "spot"),
    ("russia_st",     "俄罗斯风情街", "dl", "俄罗斯风情街 大连", "大连", "7", 1, "spot"),
    ("zhongshan_sq",  "中山广场", "dl", "大连中山广场", "大连", "7", 2, "spot"),
    ("qingniwa",      "汉庭(青泥洼)·青泥洼商圈", "dl", "青泥洼桥 大连", "大连", "7", 3, "hotel"),
    ("dalian_nb",     "大连北站(双城高铁)", "dl", "大连北站", "大连", "T", 0, "transport"),
    # ===== 沈阳 =====
    ("shenyang_st",   "沈阳站", "sy", "沈阳站", "沈阳", "4", 1, "transport"),
    ("taiyuan_st",    "parkinn丽柏(太原街)", "sy", "太原街 沈阳", "沈阳", "4", 2, "hotel"),
    ("gugong",        "沈阳故宫", "sy", "沈阳故宫", "沈阳", "5", 1, "spot"),
    ("shuaifu",       "张氏帅府", "sy", "张氏帅府 沈阳", "沈阳", "5", 2, "spot"),
    ("zhongjie",      "中街步行街", "sy", "中街 沈阳", "沈阳", "5", 3, "spot"),
    ("xita",          "西塔(韩餐夜市)", "sy", "西塔 沈阳", "沈阳", "5", 4, "food"),
    ("918",           "九一八历史博物馆", "sy", "九一八历史博物馆 沈阳", "沈阳", "6", 1, "spot"),
    ("beiling",       "北陵公园(清昭陵)", "sy", "北陵公园 沈阳", "沈阳", "6", 2, "spot"),
    ("shenyang_nb",   "沈阳北站(回大连高铁)", "sy", "沈阳北站", "沈阳", "T", 0, "transport"),
]

def geocode(q, region):
    url = "https://apis.map.qq.com/ws/geocoder/v1/?address=%s&region=%s&key=%s" % (
        urllib.parse.quote(q), urllib.parse.quote(region), KEY)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        if d.get("status") == 0:
            loc = d["result"]["location"]
            return loc["lat"], loc["lng"]
        return None, d.get("message", "err")
    except Exception as e:
        return None, str(e)

out = []
failed = []
for pid, name, city, q, region, day, order, kind in POIS:
    lat, lng = geocode(q, region)
    src = "ws"
    if lat is None:
        fb = FALLBACK.get(pid)
        if fb:
            lat, lng = fb
            src = "fallback"
            failed.append((pid, name, q, lng))  # lng holds message
        else:
            lat, lng = 0, 0
            src = "zero"
            failed.append((pid, name, q, "no-fallback"))
    out.append({"id": pid, "name": name, "city": city, "day": day,
                "order": order, "kind": kind, "lat": round(lat, 6), "lng": round(lng, 6), "src": src})
    print("%-22s %s %s  -> %s" % (name, city, day, src))
    time.sleep(0.25)

with open("poi_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("\n总数:", len(out), "| 回退/失败:", len(failed))
for x in failed:
    print("  FALLBACK:", x[1], "(", x[2], ")")
