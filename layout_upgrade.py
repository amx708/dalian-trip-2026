# -*- coding: utf-8 -*-
"""排版第三次重做：大卡片 + 时间轴 + 新手引导 + 图标条目块（小孩/长者友好）。
只改 cloud.html（内容源）。保留 <tr id="dayN">、5 个 td、表头行、textContent，
确保 gotoDay / doSearch / labelTables 依赖不破。带幂等 guard，可重跑。
"""
import io, sys

SRC = "cloud.html"
with io.open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

changed = []

# ---------- 1) 注入 CSS（放在 </style> 之前） ----------
CSS = r'''
  /* ===== 小孩/长者友好：每日大卡片 + 城市色 ===== */
  .dl-city-dl{--cc:#185FA5}      /* 大连蓝 */
  .dl-city-sy{--cc:#C2700F}      /* 沈阳橙 */
  .dl-city-cross{--cc:#7a5cff}   /* 跨城高铁 */
  /* 顶部时间轴 */
  .dl-timeline{background:linear-gradient(135deg,#eef6fb,#f4fbfe);border:1px solid var(--line);border-radius:16px;padding:14px 14px 16px;margin:0 0 16px}
  .dl-tl-title{font-size:15px;font-weight:700;color:var(--sea);margin-bottom:10px}
  .dl-tl-track{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;-webkit-overflow-scrolling:touch}
  .dl-tl-day{flex:1 1 0;min-width:104px;border:none;cursor:pointer;background:#fff;border-radius:12px;padding:10px 8px;display:flex;flex-direction:column;gap:4px;align-items:center;text-align:center;box-shadow:0 2px 8px rgba(20,136,201,.10);border-top:5px solid var(--cc,#185FA5);transition:.15s}
  .dl-tl-day:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(20,136,201,.20)}
  .dl-tl-num{font-size:15px;font-weight:800;color:var(--cc,#185FA5)}
  .dl-tl-ico{font-size:24px;line-height:1}
  .dl-tl-city{font-size:11.5px;color:var(--sub)}
  .dl-tl-theme{font-size:12px;color:var(--ink);line-height:1.3}
  /* 新手引导 */
  .dl-guide{background:#fffdf5;border:1px solid #ffe6b0;border-left:6px solid var(--sun);border-radius:12px;padding:12px 16px;margin:0 0 16px}
  .dl-guide-h{font-size:16px;font-weight:800;color:#b9760b;margin-bottom:6px}
  .dl-guide ul{list-style:none}
  .dl-guide li{font-size:14.5px;line-height:1.75;padding:4px 0}
  /* 每日大卡片 */
  .plan-table tr[id^="day"]{border:1px solid var(--line);border-radius:16px;margin:0 0 18px;background:#fff;box-shadow:inset 6px 0 0 var(--cc,#185FA5),0 4px 18px rgba(20,136,201,.07);overflow:hidden}
  .plan-table tr[id^="day"].highlight{box-shadow:inset 6px 0 0 var(--cc,#185FA5),0 0 0 3px var(--sun)!important;background:#fff8e6!important}
  @media(min-width:681px){
    .plan-table tr[id^="day"]{display:grid;grid-template-columns:96px 1fr 1.4fr;grid-template-areas:"daynum theme kw" "detail detail detail";align-items:stretch}
    .plan-table tr[id^="day"] td{border:none;padding:0;background:transparent!important}
    .plan-table tr[id^="day"] td:nth-child(1){display:none}
    .plan-table tr[id^="day"] td:nth-child(2){grid-area:daynum;background:var(--cc,#185FA5);color:#fff;font-size:19px;font-weight:800;text-align:center;display:flex;flex-direction:column;justify-content:center;padding:16px 6px}
    .plan-table tr[id^="day"] td:nth-child(3){grid-area:theme;padding:16px 16px 8px;font-size:19px;font-weight:700;color:var(--ink);line-height:1.35}
    .plan-table tr[id^="day"] td:nth-child(4){grid-area:kw;padding:16px 16px 8px;text-align:right;color:var(--sub);font-size:13px;line-height:1.6}
    .plan-table tr[id^="day"] td:nth-child(5){grid-area:detail;padding:4px 18px 18px}
  }
  /* 详情条目块 */
  .dl-item{display:flex;gap:8px;align-items:flex-start;font-size:16.5px;line-height:1.7;padding:8px 11px;margin:7px 0;background:#fafcfe;border:1px solid var(--line);border-left:3px solid #cfe3f3;border-radius:10px}
  .dl-item .em{font-size:21px;line-height:1.35;flex:0 0 auto;width:26px;text-align:center}
  .dl-item .tx{flex:1;min-width:0;line-height:1.7}
  .dl-item.sub{margin-left:22px;background:#f3f8fc;font-size:14.5px;color:var(--sub);border-style:dashed;border-left-color:#bcd6ea}
  @media(max-width:680px){
    .dl-tl-track{flex-wrap:wrap}
    .dl-tl-day{flex:1 1 28%}
    .dl-tl-theme{font-size:11px}
    .dl-item{font-size:16px}
  }
'''
if '.plan-table tr[id^="day"]' not in html:
    # 主样式块是第一个 </style>（第二个是组件内嵌小样式，不碰）
    html = html.replace("</style>", CSS + "\n</style>", 1)
    changed.append("CSS")
else:
    print("[skip] CSS 已注入")

# ---------- 2) 给 7 个 day tr 加城市 class ----------
city_map = {1:"dl-city-dl",2:"dl-city-dl",3:"dl-city-dl",4:"dl-city-cross",
            5:"dl-city-sy",6:"dl-city-sy",7:"dl-city-dl"}
for n, cls in city_map.items():
    old = '<tr id="day%d">' % n
    if old in html:
        html = html.replace(old, '<tr id="day%d" class="%s">' % (n, cls), 1)
        changed.append("day%d class" % n)
    else:
        print("[skip] day%d tr 已是卡片(或结构变化)" % n)

# ---------- 3) 插入时间轴 + 新手引导（search-bar 之前） ----------
TIMELINE = '''
<div class="dl-timeline" role="list" aria-label="7天行程时间轴">
  <div class="dl-tl-title">🗓️ 7天一眼看懂（点任一天，直接跳到当天详细安排）</div>
  <div class="dl-tl-track">
    <button type="button" class="dl-tl-day dl-city-dl" onclick="gotoDay(1)"><span class="dl-tl-num">Day1</span><span class="dl-tl-ico">🌊</span><span class="dl-tl-city">大连</span><span class="dl-tl-theme">抵达·初体验</span></button>
    <button type="button" class="dl-tl-day dl-city-dl" onclick="gotoDay(2)"><span class="dl-tl-num">Day2</span><span class="dl-tl-ico">🐯</span><span class="dl-tl-city">大连</span><span class="dl-tl-theme">老虎滩·棒棰岛·赶海</span></button>
    <button type="button" class="dl-tl-day dl-city-dl" onclick="gotoDay(3)"><span class="dl-tl-num">Day3</span><span class="dl-tl-ico">🕊️</span><span class="dl-tl-city">大连</span><span class="dl-tl-theme">东港·威尼斯水城</span></button>
    <button type="button" class="dl-tl-day dl-city-cross" onclick="gotoDay(4)"><span class="dl-tl-num">Day4</span><span class="dl-tl-ico">🚄</span><span class="dl-tl-city">跨城</span><span class="dl-tl-theme">大连→沈阳(高铁)</span></button>
    <button type="button" class="dl-tl-day dl-city-sy" onclick="gotoDay(5)"><span class="dl-tl-num">Day5</span><span class="dl-tl-ico">🏯</span><span class="dl-tl-city">沈阳</span><span class="dl-tl-theme">故宫·帅府·中街·西塔</span></button>
    <button type="button" class="dl-tl-day dl-city-sy" onclick="gotoDay(6)"><span class="dl-tl-num">Day6</span><span class="dl-tl-ico">🕯️</span><span class="dl-tl-city">沈阳</span><span class="dl-tl-theme">九一八·北陵·回大连</span></button>
    <button type="button" class="dl-tl-day dl-city-dl" onclick="gotoDay(7)"><span class="dl-tl-num">Day7</span><span class="dl-tl-ico">🏛️</span><span class="dl-tl-city">大连</span><span class="dl-tl-theme">俄街·中山广场→飞广州</span></button>
  </div>
</div>
<div class="dl-guide">
  <div class="dl-guide-h">👀 第一次看这份攻略？（点一下就懂）</div>
  <ul>
    <li>🗺️ <b>先看上面「7天一眼看懂」</b>：7个色块就是7天——<span style="color:#185FA5;font-weight:700">蓝=大连</span>、<span style="color:#C2700F;font-weight:700">橙=沈阳</span>、紫=跨城高铁。点任意一个色块，直接跳到那天的安排。</li>
    <li>📅 <b>每天一张大卡片</b>：写着「这天去哪、玩什么、几点、多少钱」，从上往下看就行，不用左右翻。</li>
    <li>✏️ <b>随时能改</b>：点左下角「✏️编辑」就能改字（加景点、调时间），改完截图也能存；不想改就当阅读版。</li>
    <li>🔍 <b>找东西</b>：在搜索框输入关键字（如「棒棰岛」「地铁」），相关的天数会高亮提醒你。</li>
  </ul>
</div>
'''
marker = '    <div class="search-bar">'
if '<div class="dl-timeline"' not in html:
    assert html.count(marker) == 1, "search-bar marker 数量异常: %d" % html.count(marker)
    html = html.replace(marker, TIMELINE + "\n" + marker, 1)
    changed.append("timeline+guide")
else:
    print("[skip] 时间轴已插入")

# ---------- 4) 新增 formatDayDetails() 并调用 ----------
JS_FUNC = r'''
  /* 把每天详情 <br> 分段包成图标条目块（幂等：已格式化则跳过） */
  function leadingEmoji(s){
    var i=0, res='';
    while(i<s.length){
      var cp=s.codePointAt(i);
      var ok=(cp>=0x1F000&&cp<=0x1FAFF)||(cp>=0x2600&&cp<=0x27BF)||(cp>=0x2B00&&cp<=0x2BFF)||(cp>=0x2300&&cp<=0x23FF)||(cp>=0x2190&&cp<=0x21FF)||cp===0xFE0F||cp===0x200D;
      if(!ok) break;
      res+=String.fromCodePoint(cp);
      i+=(cp>0xFFFF?2:1);
    }
    return res;
  }
  function formatDayDetails(){
    document.querySelectorAll('#plan .plan-table tr[id^="day"]').forEach(function(tr){
      var cells = tr.querySelectorAll('td');
      var detail = cells[cells.length-1];
      if(!detail) return;
      if(detail.children.length && detail.children[0].className && detail.children[0].className.indexOf('dl-item')!==-1) return;
      var parts = detail.innerHTML.split(/<br\s*\/?>/i);
      var out = [];
      parts.forEach(function(seg){
        var lead = seg.match(/^\s*(&nbsp;)*/);
        var sub = !!(lead && lead[1] && lead[1].length>0);
        var clean = seg.replace(/^\s*(&nbsp;)*/,'');
        if(clean==='') return;
        var em = leadingEmoji(clean);
        var rest = em ? clean.slice(em.length).replace(/^\s+/,'') : clean;
        out.push('<div class="dl-item'+(sub?' sub':'')+'">'+(em?'<span class="em">'+em+'</span>':'')+'<span class="tx">'+rest+'</span></div>');
      });
      if(out.length) detail.innerHTML = out.join('');
    });
  }
'''
if 'function formatDayDetails' not in html:
    anchor = '  /* 自动给表格单元格加上列标题标签'
    assert html.count(anchor) == 1, "labelTables 注释 anchor 异常"
    html = html.replace(anchor, JS_FUNC.strip() + "\n" + anchor, 1)
    changed.append("JS formatDayDetails")
else:
    print("[skip] formatDayDetails 已存在")

if 'setTimeout(formatDayDetails' not in html:
    html = html.replace("    labelTables();\n",
                        "    labelTables();\n    formatDayDetails();\n    setTimeout(formatDayDetails,350);\n    setTimeout(formatDayDetails,900);\n", 1)
    changed.append("JS calls")
else:
    print("[skip] formatDayDetails 调用已存在")

# ---------- 5) 在 Day 徽章里补上日期（桌面端更清晰） ----------
CSS_DATE = r'''
  .dl-date{font-size:12px;font-weight:500;opacity:.85;margin-top:2px}
'''
if '.dl-date' not in html:
    html = html.replace("</style>", CSS_DATE + "</style>", 1)
    changed.append("CSS .dl-date")
else:
    print("[skip] .dl-date 已注入")

# 手机端 cell1(日期) 已显示，隐藏徽章里的重复日期
MOB_HIDE = '  @media(max-width:680px){.dl-date{display:none}} /* dl-date mobile hide */\n'
if 'dl-date mobile hide' not in html:
    html = html.replace("</style>", MOB_HIDE + "</style>", 1)
    changed.append("CSS .dl-date mobile hide")

import re as _re
for n in range(1, 8):
    m = _re.search(r'<tr id="day%d"[^>]*>(.*?)</tr>' % n, html, _re.S)
    if not m:
        continue
    row = m.group(1)
    d1 = _re.search(r'<td>([^<]+)</td>', row)
    date = d1.group(1).strip() if d1 else ''
    cell2_old = '<td>Day%d</td>' % n
    cell2_new = '<td>Day%d<br><span class="dl-date">%s</span></td>' % (n, date)
    if cell2_old in html:
        html = html.replace(cell2_old, cell2_new, 1)
        changed.append("day%d date badge" % n)

with io.open(SRC, "w", encoding="utf-8") as f:
    f.write(html)

print("changed:", changed if changed else "无改动（已是新版）")
