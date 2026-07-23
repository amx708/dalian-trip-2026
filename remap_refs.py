# -*- coding: utf-8 -*-
import sys

path = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
s = open(path, encoding='utf-8').read()

# (find, replace, expected_count)
reps = [
    # --- 老虎滩 -> Day2 ---
    ('onclick="gotoDay(4)" title="点击直达 Day4 行程（可选替换）"><b>⭐⭐ 老虎滩海洋公园</b>',
     'onclick="gotoDay(2)" title="点击直达 Day2 行程（老虎滩日）"><b>⭐⭐ 老虎滩海洋公园</b>', 1),
    ('📅 <b>Day4 可选替换（与旅顺二选一）· 9:30–16:00</b>',
     '📅 <b>Day2 · 9:00–16:00（与旅顺二选一）</b>', 1),

    # --- 201路 -> Day3 ---
    ('onclick="gotoDay(4)" title="点击直达 Day4 行程"><b>⭐ 201路有轨电车</b>',
     'onclick="gotoDay(3)" title="点击直达 Day3 行程"><b>⭐ 201路有轨电车</b>', 1),
    ('📅 <b>Day4 · 14:00–15:00</b>', '📅 <b>Day3 · 14:00–15:00</b>', 1),

    # --- 中山广场/俄罗斯风情街 -> Day7 (发起人计划 Day7) ---
    ('onclick="gotoDay(4)" title="点击直达 Day4 行程"><b>⭐⭐ 中山广场 / 俄罗斯风情街</b>',
     'onclick="gotoDay(7)" title="点击直达 Day7 行程"><b>⭐⭐ 中山广场 / 俄罗斯风情街</b>', 1),
    ('📅 <b>Day4 · 10:00–12:30</b>', '📅 <b>Day7 · 9:30–12:00</b>', 1),

    # --- 旅顺 -> Day3 ---
    ('onclick="gotoDay(4)" title="点击直达 Day4 行程（旅顺为 Day4 可选替换）"><b>⭐ 旅顺（军港/日俄监狱/潜艇馆）</b>',
     'onclick="gotoDay(3)" title="点击直达 Day3 行程（旅顺为 Day3 可选替换）"><b>⭐ 旅顺（军港/日俄监狱/潜艇馆）</b>', 1),
    ('现为 Day4 可选替换，原 Day6 已挪给沈阳', '现为 Day3 可选替换，原 Day6 已挪给沈阳', 1),
    ('📅 <b>可选 Day4 替换 · 10:00–14:30</b>', '📅 <b>可选 Day3 替换 · 10:00–14:30</b>', 1),

    # --- 港东五街 -> Day3 (东港区) ---
    ('onclick="gotoDay(4)" title="点击直达 Day4 行程"><b>⭐ 港东五街 · 船舶穿城</b>',
     'onclick="gotoDay(3)" title="点击直达 Day3 行程"><b>⭐ 港东五街 · 船舶穿城</b>', 1),
    ('📅 <b>Day4 · 15:30–16:30</b>', '📅 <b>Day3 · 15:30–16:30</b>', 1),

    # --- 随意打卡点 表 ---
    ('📅 <b style="color:var(--sea)">Day4 替代</b>: 圣亚海洋世界 / 星海公园游乐场 → <a class="spot-link" onclick="gotoDay(4)" title="点击直达 Day4">点此跳到 Day4</a>',
     '📅 <b style="color:var(--sea)">Day3 替代</b>: 圣亚海洋世界 / 星海公园游乐场 → <a class="spot-link" onclick="gotoDay(3)" title="点击直达 Day3">点此跳到 Day3</a>', 1),
    ('<a class="spot-link" onclick="gotoDay(4)" title="点击直达 Day4"><b>青泥洼桥 / 西安路商圈</b></a>',
     '<a class="spot-link" onclick="gotoDay(3)" title="点击直达 Day3"><b>青泥洼桥 / 西安路商圈</b></a>', 1),
    ('📅 <b>Day4 · 全天</b> 城市复古骑行+商圈逛吃', '📅 <b>Day3 · 全天</b> 城市复古骑行+商圈逛吃', 1),

    # --- 顺路提示 ---
    ('<li><b>Day4</b> 西安路 / 青泥洼桥商圈 → 逛街顺带感受大连城市脉搏。</li>',
     '<li><b>Day3</b> 西安路 / 青泥洼桥商圈 → 逛街顺带感受大连城市脉搏。</li>', 1),

    # --- 放松 note ---
    ('大连 Day4 若去旅顺回来', '大连 Day3 若去旅顺', 1),
    ('沈阳 Day5/Day6 可选', '沈阳 Day4–6 可选', 1),

    # --- 美食地图 links ---
    ('行程 <a class="spot-link" onclick="gotoDay(1)">🔗 Day1</a> / <a class="spot-link" onclick="gotoDay(4)">🔗 Day4</a>',
     '行程 <a class="spot-link" onclick="gotoDay(2)">🔗 Day2</a>', 1),
    ('📍 推荐天津街/中原小吃街：中山区天津街（近火车站）· 行程 <a class="spot-link" onclick="gotoDay(4)">🔗 Day4</a>',
     '📍 推荐天津街/中原小吃街：中山区天津街（近火车站）· 行程 <a class="spot-link" onclick="gotoDay(3)">🔗 Day3</a>', 1),
    ('📍 推荐：日丰源饺子（小平岛店）甘井子区小平岛路 · 行程 <a class="spot-link" onclick="gotoDay(4)">🔗 Day4</a>',
     '📍 推荐：日丰源饺子（小平岛店）甘井子区小平岛路 · 行程 <a class="spot-link" onclick="gotoDay(3)">🔗 Day3</a>', 1),
    ('📍 推荐：老菜馆（青泥洼桥/西安路商圈）中山区友好广场附近 · 行程 <a class="spot-link" onclick="gotoDay(4)">🔗 Day4</a>',
     '📍 推荐：老菜馆（青泥洼桥/西安路商圈）中山区友好广场附近 · 行程 <a class="spot-link" onclick="gotoDay(3)">🔗 Day3</a>', 1),
    ('📍 推荐：新长兴市场 / 桃源市场 西岗区长春路200号 · 行程 <a class="spot-link" onclick="gotoDay(4)">🔗 Day4</a>',
     '📍 推荐：新长兴市场 / 桃源市场 西岗区长春路200号 · 行程 <a class="spot-link" onclick="gotoDay(3)">🔗 Day3</a>', 1),
    ('📍 推荐：老菜馆（西安路商圈）沙河口区西安路附近 · 行程 <a class="spot-link" onclick="gotoDay(4)">🔗 Day4</a>',
     '📍 推荐：老菜馆（西安路商圈）沙河口区西安路附近 · 行程 <a class="spot-link" onclick="gotoDay(3)">🔗 Day3</a>', 1),

    # --- 大菜市 / 小平岛 跳 Day4 (x2) ---
    ('onclick="gotoDay(4)">🔗 跳 Day4 行程</a>', 'onclick="gotoDay(3)">🔗 跳 Day3 行程</a>', 2),

    # --- 沈阳 板块标题 ---
    ('📍 沈阳 2 日方案 & 核心景点（Day5 / Day6）', '📍 沈阳 2 日方案 & 核心景点（Day4–6）', 1),

    # --- 住宿面板 ---
    ('本次双城住宿已定（大连4晚 + 沈阳2晚），详细已订信息见下表。表格格子可随手改。',
     '本次双城住宿已定：大连·亚朵(Day1–3) + 沈阳·parkinn(Day4–5) + 大连·汉庭(Day6，Day7飞广州不过夜)。房价以实际订单为准（不替你填价）。表格格子可随手改。', 1),
    ('<tr><td><b>大连·汉庭酒店（青泥洼商业街店）</b></td><td>Day1–4 共4晚（¥1576）· 青泥洼桥站旁，近大连商场/天津街，连锁干净安全、位置中心</td></tr>',
     '<tr><td><b>大连·汉庭酒店（青泥洼商业街店）</b></td><td>Day6 共1晚（8/2 入住 – 8/3 退房，Day7 飞广州不过夜，行李寄存前台）· 青泥洼桥站旁，近大连商场/天津街，连锁干净安全、位置中心</td></tr>', 1),
    ('<tr><td><b>沈阳·奉天尊享高层景观双床套房</b></td><td>Day5–6 共2晚（¥776×2=¥1552）· 沈阳站/中街附近，高层景观、双床套房，8人两间</td></tr>',
     '<tr><td><b>沈阳·parkinn 丽柏酒店（沈阳站太原街）</b></td><td>Day4–5 共2晚（7/31 入住 – 8/2 退房）· 沈阳站/太原街旁，连锁干净、位置中心，8人两间</td></tr>', 1),
    ('<tr><td><b>入住–退房</b></td><td>大连 7/28 入住 – 8/1 退房；沈阳 8/1 入住 – 8/3 退房（按订单核对）</td></tr>',
     '<tr><td><b>入住–退房</b></td><td>亚朵 7/28 入住–7/31 退房(3晚)；parkinn 7/31 入住–8/2 退房(2晚)；汉庭 8/2 入住–8/3 退房(1晚)。日期按订单核对</td></tr>', 1),
    ('<tr><td><b>Day7 大连</b></td><td>8/3 当天高铁回大连后直接飞广州（16:00航班），大连不过夜，行李寄存汉庭前台</td></tr>',
     '<tr><td><b>Day7 大连</b></td><td>8/3 上午俄街/中山广场，午餐后直飞广州（16:00航班），大连不过夜，行李已寄存汉庭前台</td></tr>', 1),
    ('<tr><td><b>提醒</b></td><td>汉庭提前把8人分房/连房需求说清；奉天尊享为高层景观套房，沈阳两晚固定不动；退房日带好证件。</td></tr>',
     '<tr><td><b>提醒</b></td><td>亚朵/parkinn/汉庭提前把8人分房/连房需求说清；parkinn 为沈阳站旁连锁，两晚固定不动；退房日带好证件。</td></tr>', 1),
    ('本次已订连锁酒店（汉庭 / 奉天尊享），求稳省心', '本次已订连锁酒店（亚朵 / parkinn / 汉庭），求稳省心', 1),

    # --- 节奏 note：去掉 Day4 上午加旅顺（旅顺已归 Day3）---
    ('，或 Day4 上午加（历史人文首选旅顺）', '', 1),

    # --- 租车细节：金石滩已移除，改为旅顺 ---
    ('去<b>金石滩</b>、<b>旅顺</b>的两天', '去<b>旅顺</b>的两天', 1),
]

bad = False
for i, (f, r, n) in enumerate(reps):
    c = s.count(f)
    if c != n:
        print(f'[MISSMATCH #{i}] expected {n}, found {c}: {f[:60]!r}')
        bad = True
    s = s.replace(f, r)

if bad:
    print('ABORT: count mismatches above. Not writing.')
    sys.exit(1)

open(path, 'w', encoding='utf-8').write(s)
print('OK wrote cloud.html, len=', len(s))
print('remaining gotoDay(4):', s.count('gotoDay(4)'))
print('remaining 奉天尊享:', s.count('奉天尊享'))
print('remaining 大连4晚:', s.count('大连4晚'))
print('沈阳 title Day4-6 present:', '沈阳 2 日方案 & 核心景点（Day4–6）' in s)
