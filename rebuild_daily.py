import os

f = r"C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html"
s = open(f, encoding="utf-8").read()

def replace_day(s, day_id, new_row):
    start = s.index('<tr id="%s">' % day_id)
    end = s.index('</tr>', start) + len('</tr>')
    return s[:start] + new_row + s[end:]

DAY1 = '''        <tr id="day1">
          <td>7/28 周二</td>
          <td>Day1</td>
          <td>抵达 · 大连初体验</td>
          <td>滨海路 / 莲花山 / 银沙滩 / 星海广场</td>
          <td>
            ✈️ 09:10→12:40 广州白云T2 → 大连周水子<br>
            🚌 机场→酒店：地铁2号线到港湾广场站，放行李 🏨 入住<b>亚朵（港湾广场人民路）</b>（每房含2位早餐）<br>
            🛣️ <b>下午 滨海路</b>观光：跨海大桥观景台、海达索道（跨山看海，如开放）、沿海慢走<br>
            &nbsp;&nbsp;🚌 打车/自驾沿滨海中路；8人建议2辆或商务车<br>
            🌄 <b>莲花山</b>小火车登顶看城景与跨海大桥全景<br>
            &nbsp;&nbsp;🎫 门票¥20（含小火车）| 夏季至19:00 | 🚌 打车约15分钟<br>
            🏖️ <b>银沙滩</b>（很多咖啡店+文创店，海边逛吃歇脚）<br>
            &nbsp;&nbsp;🎫 免费 | 全天开放<br>
            🎡 <b>傍晚 星海广场</b>：落日飞车 + 落日秋千，看音乐喷泉与灯光秀<br>
            &nbsp;&nbsp;🎫 广场免费 | ⛲ 音乐喷泉夏19:40（周五六加20:40场）| 🚌 地铁1号线"星海广场"站<br>
            🍽️ <b>晚餐 金鑫海鲜烧烤</b>（8人建议提前订大桌）<br>
            💡 首日不赶，亚朵含双早；航班若延误顺延。
          </td>
        </tr>'''

DAY2 = '''        <tr id="day2">
          <td>7/29 周三</td>
          <td>Day2</td>
          <td>老虎滩 · 棒棰岛 · 赶海</td>
          <td>老虎滩 / 棒棰岛 / 赶海 / 品海楼</td>
          <td>
            🍳 <b>酒店早餐</b>（亚朵每房含2位）<br>
            🐯 <b>9:00–12:00 老虎滩海洋公园</b>（极地馆/珊瑚馆/鸟语林，亲子友好）<br>
            &nbsp;&nbsp;🎫 联票约¥220/人（以官方为准）| 🚌 地铁5号线"老虎滩"站<br>
            🏝️ <b>13:00–15:30 棒棰岛</b>（果冻蓝海水！带泳衣可下水）<br>
            &nbsp;&nbsp;🚌 打车约25分钟 | 🎫 门票¥20/人<br>
            🦀 <b>16:00–18:00 傍晚退潮赶海</b>（查当日潮汐表！带小桶铲子）<br>
            &nbsp;&nbsp;🏖️ 棒棰岛/滨海浴场礁石区皆可；带娃注意安全<br>
            🦞 <b>18:30 晚餐 渔人码头品海楼</b>（⚠️ 需提前3天预订）<br>
            &nbsp;&nbsp;🚌 渔人码头，海鲜地道；8人建议订大桌<br>
            💡 老虎滩+棒棰岛一天较满，体力好可加滨海路骑行。
          </td>
        </tr>'''

DAY3 = '''        <tr id="day3">
          <td>7/30 周四</td>
          <td>Day3</td>
          <td>东港 · 喂海鸥 · 威尼斯水城</td>
          <td>东港 / 中央大道 / 美食街 / 喷泉</td>
          <td>
            🍳 <b>酒店早餐</b>（亚朵每房含2位）<br>
            🕊️ <b>上午–下午 东港 / 中央大道</b>喂海鸥🕊️、海边漫步<br>
            &nbsp;&nbsp;🎫 免费 | 海鸥季（冬春最多，夏季较少但仍有）<br>
            🍜 <b>美食街逛吃</b>：东港周边小吃/餐厅，8人分头排队<br>
            🏛️ <b>威尼斯水城</b>：欧式建筑+运河，拍照出片<br>
            &nbsp;&nbsp;🎫 免费 | 全天<br>
            ⛲ <b>傍晚 东港音乐喷泉</b>（夏19:40，周五六加20:40场）+ 水城夜景散步<br>
            &nbsp;&nbsp;🎫 喷泉免费<br>
            🍽️ <b>晚餐</b> → 东港/凯德和平附近（见美食地图）<br>
            💡 今天轻松，适合老人孩子；东港也是看跨海大桥夜景好位置。
          </td>
        </tr>'''

DAY4 = '''        <tr id="day4">
          <td>7/31 周五</td>
          <td>Day4</td>
          <td>大连 → 沈阳（高铁）</td>
          <td>高铁 / 跨城 / parkinn</td>
          <td>
            🍳 <b>酒店早餐</b>（亚朵每房含2位）<br>
            🧳 <b>退房</b> → 行李带走/寄存<br>
            🚄 <b>高铁 大连北/大连站 → 沈阳站/沈阳北</b>（约2.5–3.5h，二等座¥170–210/人）<br>
            &nbsp;&nbsp;⚠️ <b>8人务必提前购票</b>，尽量买连号座；城市中心对中心最省事<br>
            🍱 <b>午餐</b> → 高铁上或沈阳站附近（老边饺子/李连贵熏肉大饼）<br>
            🏨 <b>下午 入住 parkinn 丽柏酒店（沈阳站太原街）</b> → 放行李休息<br>
            🚶 <b>傍晚</b> 太原街/中街随便逛吃（沈阳站出来即太原街）<br>
            💡 沈阳比大连热2–3℃，注意补水。
          </td>
        </tr>'''

DAY5 = '''        <tr id="day5">
          <td>8/01 周六</td>
          <td>Day5</td>
          <td>沈阳 · 故宫 / 帅府 / 中街 / 西塔</td>
          <td>沈阳故宫 / 张氏帅府 / 中街 / 西塔</td>
          <td>
            🍳 <b>早餐</b>（酒店不含早，附近解决）<br>
            🏯 <b>9:00–11:30 沈阳故宫</b>（清入关前皇宫，世界文化遗产）<br>
            &nbsp;&nbsp;🎫 ¥50/人 | 🕐 8:30–17:00（周一闭馆，周六开放）
            <a class="ext" href="https://uri.amap.com/search?keyword=%E6%B2%88%E9%98%B3%E6%95%85%E5%AE%AB&city=%E6%B2%88%E9%98%B3" target="_blank" rel="noopener">🗺️ 高德</a>
            <a class="ext" href="https://www.douyin.com/search/%E6%B2%88%E9%98%B3%E6%95%85%E5%AE%AB" target="_blank" rel="noopener">📱 抖音</a>
            <a class="ext" href="https://www.xiaohongshu.com/search_result?keyword=%E6%B2%88%E9%98%B3%E6%95%85%E5%AE%AB" target="_blank" rel="noopener">📕 小红书</a><br>
            🏛️ <b>11:45–13:00 张氏帅府</b>（张作霖/张学良府邸，与故宫一墙之隔）<br>
            &nbsp;&nbsp;🎫 ¥48/人 | 🚌 步行5分钟
            <a class="ext" href="https://uri.amap.com/search?keyword=%E5%BC%A0%E6%B0%8F%E5%B8%85%E5%BA%9C&city=%E6%B2%88%E9%98%B3" target="_blank" rel="noopener">🗺️ 高德</a>
            <a class="ext" href="https://www.douyin.com/search/%E5%BC%A0%E6%B0%8F%E5%B8%85%E5%BA%9C" target="_blank" rel="noopener">📱 抖音</a>
            <a class="ext" href="https://www.xiaohongshu.com/search_result?keyword=%E5%BC%A0%E6%B0%8F%E5%B8%85%E5%BA%9C" target="_blank" rel="noopener">📕 小红书</a><br>
            🍱 <b>13:00 午餐</b> → 中街（老边饺子/中街大果）<br>
            🛍️ <b>14:30–17:00 中街</b>步行街逛吃（沈阳第一商圈）<br>
            🍜 <b>18:30 晚餐</b> → 西塔（韩餐、烤肉、烤冷面，霓虹夜市）
            <a class="ext" href="https://uri.amap.com/search?keyword=%E8%A5%BF%E5%A1%94%E6%9C%9D%E9%B2%9C%E6%97%8F%E9%A3%8E%E6%83%85%E8%A1%97&city=%E6%B2%88%E9%98%B3" target="_blank" rel="noopener">🗺️ 西塔</a><br>
            💡 故宫+帅府+中街一天经典；西塔夜生活见美食地图·夜生活。
          </td>
        </tr>'''

DAY6 = '''        <tr id="day6">
          <td>8/02 周日</td>
          <td>Day6</td>
          <td>沈阳深度 · 高铁回大连 · 收尾</td>
          <td>九一八 / 北陵 / 高铁 / 南山 / 东关街</td>
          <td>
            🍳 <b>早餐</b>（酒店不含早）<br>
            🕯️ <b>9:00–10:30 九一八历史博物馆</b>（国耻教育，免费需提前预约）<br>
            &nbsp;&nbsp;🎫 免费（公众号预约）| 🕐 9:00–16:30（周一闭馆）
            <a class="ext" href="https://uri.amap.com/search?keyword=%E4%B9%9D%E4%B8%80%E5%85%AB%E5%8E%86%E5%8F%B2%E5%8D%9A%E7%89%A9%E9%A6%86&city=%E6%B2%88%E9%98%B3" target="_blank" rel="noopener">🗺️ 高德</a>
            <a class="ext" href="https://www.douyin.com/search/%E4%B9%9D%E4%B8%80%E5%85%AB%E5%8E%86%E5%8F%B2%E5%8D%9A%E7%89%A9%E9%A6%86" target="_blank" rel="noopener">📱 抖音</a>
            <a class="ext" href="https://www.xiaohongshu.com/search_result?keyword=%E4%B9%9D%E4%B8%80%E5%85%AB%E5%8E%86%E5%8F%B2%E5%8D%9A%E7%89%A9%E9%A6%86" target="_blank" rel="noopener">📕 小红书</a><br>
            &nbsp;&nbsp;⚠️ 内容沉重，小学生以下可跳过<br>
            🌳 <b>11:00–12:30 北陵公园（清昭陵）</b>（世界遗产，林荫大氧吧）<br>
            &nbsp;&nbsp;🎫 公园免费，陵寝¥30/人 | 🚌 地铁2号线"北陵公园"站
            <a class="ext" href="https://uri.amap.com/search?keyword=%E5%8C%97%E9%99%B5%E5%85%AC%E5%9B%AD&city=%E6%B2%88%E9%98%B3" target="_blank" rel="noopener">🗺️ 高德</a><br>
            🚄 <b>13:30–17:00 高铁 沈阳 → 大连北</b>（早班次更从容，二等座¥170–210/人）<br>
            &nbsp;&nbsp;🚌 到大连北后地铁1号线→2号线直达市区<br>
            🏨 <b>17:30 入住 汉庭（青泥洼商业街店）</b> → 放行李<br>
            🛍️ <b>18:30–21:00 大商 / 南山风情街 / 东关街</b>逛吃收尾<br>
            &nbsp;&nbsp;🛍️ 大商（青泥洼商圈大商场）+ 南山风情街（老洋房文艺）+ 东关街（老街新改，小吃文创）<br>
            💡 沈阳跨区，上午打车衔接；回大连后轻松逛街区即可。
          </td>
        </tr>'''

DAY7 = '''        <tr id="day7">
          <td>8/03 周一</td>
          <td>Day7</td>
          <td>大连 · 俄罗斯风情街 / 中山广场 → 飞广州</td>
          <td>俄街 / 中山广场 / 午饭 / 直飞</td>
          <td>
            🍳 <b>早餐</b>（汉庭不含早，附近解决）<br>
            🏛️ <b>9:30–11:00 俄罗斯风情街</b>复古街景逛吃（特产慎买，拍照就好）<br>
            &nbsp;&nbsp;🎫 免费 | 🚌 地铁2号线"友谊街/人民广场"附近<br>
            🏛️ <b>11:00–12:00 中山广场</b>欧式建筑群拍照（大连地标）<br>
            &nbsp;&nbsp;🎫 免费 | 🚌 地铁2号线"友好广场"站步行<br>
            🍱 <b>12:00 午餐</b> → 青泥洼/天津街（焖子、海胆水饺，最后一顿大连味）<br>
            ✈️ <b>午餐后出发去机场 → 大连周水子飞广州</b>（航班16:00起飞→19:50到白云T2）<br>
            &nbsp;&nbsp;🚌 地铁2号线直达周水子机场（约35分钟）；提前2小时到最稳<br>
            &nbsp;&nbsp;⏰ 特产务必 Day6 前买好（大菜市干海鲜等）<br>
            📝 回家清单：特产/充电器/证件在手？
          </td>
        </tr>'''

for did, row in [("day1",DAY1),("day2",DAY2),("day3",DAY3),("day4",DAY4),("day5",DAY5),("day6",DAY6),("day7",DAY7)]:
    before = s.count('<tr id="%s">' % did)
    s = replace_day(s, did, row)
    after = s.count('<tr id="%s">' % did)
    assert before == 1 and after == 1, (did, before, after)

# 住宿已订 note
old_note = '''    <div class="note">🏨 <b>住宿已订：</b><br>
    📍 <b>大连·汉庭酒店（青泥洼商业街店）</b> — Day1/2/3/4（共4晚，¥1576）<br>
    📍 <b>沈阳·奉天尊享高层景观双床套房</b> — Day5/6（共2晚，¥776×2=¥1552）<br>
    💡 沈阳酒店比大连便宜；Day7 当天高铁回大连后直接飞广州（16:00航班），大连不过夜，行李可寄存汉庭。8人建议提前订大桌/大房。</div>'''
new_note = '''    <div class="note">🏨 <b>住宿已订（按发起人计划）：</b><br>
    📍 <b>大连·亚朵酒店（港湾广场人民路）</b> — Day1/2/3（共3晚，每房含2位早餐）<br>
    📍 <b>沈阳·parkinn 丽柏酒店（沈阳站太原街）</b> — Day4/5（共2晚）<br>
    📍 <b>大连·汉庭酒店（青泥洼商业街店）</b> — Day6/7（共2晚）<br>
    💡 房价以实际订单为准（本攻略不替你填价，可自行改）；Day4 高铁大连→沈阳、Day6 高铁沈阳→大连；8人建议提前订大桌/大房。</div>'''
assert s.count(old_note) == 1, s.count(old_note)
s = s.replace(old_note, new_note)

# 节奏 note
old_rhythm = '''    <div class="note">🕐 以上为"大连4天 + 沈阳2天 + 返程1天"舒适节奏。大连精华是 Day1+Day2+Day3；沈阳两天可互换；若时间紧优先保 Day1+Day2+Day3 + 沈阳故宫/帅府。原大连的<b>老虎滩/森林动物园</b>、<b>旅顺半日</b>因挪出两天去沈阳，改为可选：若想加，可在 Day4 后或 Day4 当天替换（亲子首选老虎滩，历史人文首选旅顺）。</div>'''
new_rhythm = '''    <div class="note">🕐 以上为"大连3天(首段) + 沈阳2天 + 大连收尾1天"节奏。大连首段精华 Day1+Day2+Day3；沈阳 Day4–6（Day4 下午到、Day5/6 玩、Day6 下午回大连）。若时间紧优先保 Day1+Day2 + 沈阳故宫/帅府。<b>老虎滩</b>已排 Day2；原大连的<b>旅顺半日</b>、<b>森林动物园</b>改为可选：想加可在 Day3 替换东港，或 Day4 上午加（历史人文首选旅顺）。</div>'''
assert s.count(old_rhythm) == 1, s.count(old_rhythm)
s = s.replace(old_rhythm, new_rhythm)

open(f, "w", encoding="utf-8").write(s)
print("daily table + notes rebuilt. len=", len(s))
