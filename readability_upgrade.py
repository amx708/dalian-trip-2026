import os

# 可读性升级：对照「正文>=16px / 行高1.5-1.7 / 清晰层级 / 留白节奏 / 移动端最小16px」准则
# 仅改 CSS 数值，不碰 HTML 结构与 JS（保留 contenteditable / labelTables / 搜索 / gotoDay）
REPL = [
    # 0) body 行高 1.6 -> 1.7
    (";line-height:1.6;-webkit-font-smoothing", ";line-height:1.7;-webkit-font-smoothing"),
    # 1) h2 加大、加顶部间距、左侧强调条加粗
    ("h2{font-size:19px;margin:6px 0 14px;padding-left:11px;border-left:4px solid var(--sea)}",
     "h2{font-size:21px;line-height:1.35;margin:26px 0 14px;padding-left:14px;border-left:5px solid var(--sea);color:var(--ink)}"),
    # 2) h3 加大、加间距
    ("h3{font-size:15.5px;margin:18px 0 8px;color:var(--sea2)}",
     "h3{font-size:17px;line-height:1.4;margin:20px 0 10px;color:var(--sea2)}"),
    # 3) 正文 14.5 -> 16
    ("p,li{font-size:14.5px;color:var(--ink)}",
     "p,li{font-size:16px;color:var(--ink)}"),
    # 4) 卡片圆角/内距/阴影
    (".card{background:var(--card);border:1px solid var(--line);border-radius:12px;",
     ".card{background:var(--card);border:1px solid var(--line);border-radius:14px;"),
    ("padding:16px;margin-bottom:14px;box-shadow:0 2px 10px rgba(31,45,61,.04)}",
     "padding:18px 18px;margin-bottom:16px;box-shadow:0 2px 12px rgba(31,45,61,.05)}"),
    # 5) 提示框字号/行高/内距
    ("padding:12px 14px;font-size:13.5px;color:#9a4a25;margin:10px 0}",
     "padding:14px 16px;font-size:14.5px;line-height:1.7;color:#9a4a25;margin:12px 0}"),
    # 6) 表格字号
    ("table{width:100%;border-collapse:collapse;font-size:13.5px;margin:6px 0 4px}",
     "table{width:100%;border-collapse:collapse;font-size:14.5px;margin:8px 0 4px}"),
    # 7) 表头/单元格内距
    ("th,td{border:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}",
     "th,td{border:1px solid var(--line);padding:11px 12px;text-align:left;vertical-align:top}"),
    # 8) 景点卡标题
    (".spot .hd b{font-size:15px;color:var(--sea)}",
     ".spot .hd b{font-size:16px;color:var(--sea)}"),
    # 9) 景点卡正文
    (".spot .bd{padding:11px 14px;font-size:13px;color:var(--sub)}",
     ".spot .bd{padding:13px 15px;font-size:14px;line-height:1.7;color:var(--sub)}"),
    # 10) 行程表单元格行高
    (".plan-table td{line-height:1.82;vertical-align:top}",
     ".plan-table td{line-height:1.85;vertical-align:top}"),
    # 11) 标签
    (".tag{display:inline-block;font-size:11.5px;padding:2px 9px;border-radius:20px;",
     ".tag{display:inline-block;font-size:12px;padding:3px 10px;border-radius:20px;"),
    # 12) 移动端 plan-table 字号 13.5 -> 14.5
    (".plan-table{font-size:13.5px;min-width:560px}",
     ".plan-table{font-size:14.5px;min-width:560px}"),
    # 13) 移动端正文 14 -> 16
    ("p,li{font-size:14px}", "p,li{font-size:16px}"),
    # 14) 移动端 h2 加大顶部间距
    ("h2{font-size:17px;margin:4px 0 10px}", "h2{font-size:18px;margin:18px 0 10px}"),
    # 15) 移动端 h3
    ("h3{font-size:14.5px}", "h3{font-size:15.5px}"),
    # 16) 移动端卡片内距收敛
    ("  .card{overflow-x:auto;-webkit-overflow-scrolling:touch}",
     "  .card{overflow-x:auto;-webkit-overflow-scrolling:touch;padding:14px}"),
    # 17) tips 列表字号/行高
    ("ul.tips li{padding:8px 0 8px 26px;position:relative;border-bottom:1px dashed var(--line);font-size:14px}",
     "ul.tips li{padding:9px 0 9px 26px;position:relative;border-bottom:1px dashed var(--line);font-size:15.5px;line-height:1.7}"),
    # 18) pack 字号
    (".pack{display:grid;grid-template-columns:repeat(2,1fr);gap:6px 18px;font-size:13.5px}",
     ".pack{display:grid;grid-template-columns:repeat(2,1fr);gap:8px 18px;font-size:14.5px}"),
    # 19) 页脚字号
    (".foot{font-size:12px;color:var(--sub);margin-top:26px;border-top:1px solid var(--line);padding-top:14px}",
     ".foot{font-size:13px;color:var(--sub);margin-top:26px;border-top:1px solid var(--line);padding-top:14px}"),
    # 20) KPI 数字/标签在移动端仍清晰（桌面保持，移动端已单列）
    (".kpi .v{font-size:20px;font-weight:700;color:var(--sea)}",
     ".kpi .v{font-size:22px;font-weight:700;color:var(--sea)}"),
    (".kpi .l{font-size:12px;color:var(--sub);margin-top:3px}",
     ".kpi .l{font-size:12.5px;color:var(--sub);margin-top:4px}"),
]

files = [
    r"C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html",
    r"C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\index.html",
]

for f in files:
    s = open(f, encoding="utf-8").read()
    for i, (old, new) in enumerate(REPL):
        c = s.count(old)
        if c != 1:
            raise SystemExit(f"[FAIL] {os.path.basename(f)} repl#{i} matched {c} times (expect 1): {old!r}")
        s = s.replace(old, new)
    open(f, "w", encoding="utf-8").write(s)
    print("ok:", os.path.basename(f), "len=", len(s))

print("ALL REPLACEMENTS APPLIED (each matched exactly once).")
