import urllib.request, time

urls = {
    "GitHub Pages (cloud.html)": "https://amx708.github.io/dalian-trip-2026/cloud.html",
    "CloudStudio (novpn)": "https://287d71a905cc43bba5be8b7d6bb03b9f.app.codebuddy.work",
}

markers = {
    "日期样式增强(.dl-date 13.5px)": lambda t: ('dl-date' in t and '13.5px' in t and 'border-radius:12px' in t),
    "旅顺自驾标记(自驾最划算>=2)": lambda t: t.count('自驾最划算') >= 2,
    "Day6行李寄存(退房+行李寄存)": lambda t: '退房+行李寄存' in t,
    "酒店前台寄存": lambda t: '酒店前台' in t and '行李' in t,
    "住宿Day轴表(每天对应酒店)": lambda t: '每天对应酒店与标题' in t,
    "沈阳CP总表(syCpRows)": lambda t: 'syCpRows' in t,
}

ts = int(time.time())
for name, base in urls.items():
    url = f"{base}?ts={ts}"
    ok = True
    detail = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "ignore")
        for m, fn in markers.items():
            res = fn(html)
            detail.append(f"  [{'OK' if res else 'MISS'}] {m}")
            if not res:
                ok = False
        print(f"== {name} == size={len(html)} -> {'ALL OK' if ok else 'HAS MISSING'}")
        print("\n".join(detail))
    except Exception as e:
        print(f"== {name} == FETCH ERROR: {e}")
    print()
