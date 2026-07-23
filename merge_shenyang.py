import re
from pathlib import Path

BASE = Path(r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy')

def count_div_opens(s: str) -> int:
    """统计字符串中未自闭合的 <div ...> 标签数量。"""
    return len(re.findall(r'<div\b(?![^>]*?/)', s, flags=re.I))

def remove_block(text: str, start_marker: str) -> str:
    """找到 start_marker 位置，向后按 div 嵌套深度找到闭合的 </div>，并删除整个块。"""
    idx = text.find(start_marker)
    if idx == -1:
        return text
    scan = idx
    depth = count_div_opens(start_marker)
    in_tag = False
    tag_buf = []
    while scan < len(text):
        ch = text[scan]
        if ch == '<':
            in_tag = True
            tag_buf = ['<']
        elif in_tag:
            tag_buf.append(ch)
            if ch == '>':
                tag = ''.join(tag_buf)
                if re.match(r'<div\b(?![^>]*?/)', tag, flags=re.I):
                    depth += 1
                elif tag.lower().startswith('</div>'):
                    depth -= 1
                    if depth == 0:
                        end = scan + 1
                        # 吞掉后面紧跟的空白/换行
                        while end < len(text) and text[end] in ' \t':
                            end += 1
                        if end < len(text) and text[end] == '\n':
                            end += 1
                        return text[:idx] + text[end:]
                in_tag = False
                tag_buf = []
        scan += 1
    return text

def merge(file_path: Path) -> str:
    text = file_path.read_text(encoding='utf-8')

    # 1. 删除沈阳2日游方案网格：从注释开始到 sy3-wrap 外层 div 结束
    start = text.find('<!-- 沈阳2日游方案（手账参考版） -->')
    if start != -1:
        # 把注释到 sy3-wrap 开头之间的内容（style/h2/note）先清掉
        wrap_start = text.find('<div class="sy3-wrap">', start)
        if wrap_start != -1:
            text = text[:start] + '\n' + text[wrap_start:]
        # 删除 sy3-wrap 块
        text = remove_block(text, '<div class="sy3-wrap">')
        # 清理可能残留的 <style> 块
        text = re.sub(r'\s*<style>\s*\.sy3-wrap\{[\s\S]*?</style>\s*', '\n', text)

    # 2. 替换核心景点标题与说明
    text = text.replace(
        '<h2 style="margin-top:28px">📍 沈阳核心景点（Day5 / Day6）</h2>\n    <div class="note">🏯 上面方案涉及的景点详情卡：门票、地铁、亲子提醒。多数场馆周一闭馆，以官方为准。</div>',
        '<h2 style="margin-top:28px">📍 沈阳 2 日方案 & 核心景点（Day5 / Day6）</h2>\n    <div class="note">📕 小红书手账 9 个项目压进沈阳 2 天，统一用卡片呈现。<b>Day5</b> 故宫 → 帅府 → 中街/西塔；<b>Day6</b> 九一八 → 工业博物馆 → 北陵 → 辽博 → 彩电塔夜市。多数场馆周一闭馆，门票/时间以官方为准；Day6 跨区较紧，建议打车衔接。</div>'
    )

    # 3. 在 grid 内插入中街、彩电塔夜市两张卡片
    zhongjie = '''      <div class="spot"><div class="hd"><a class="spot-link" onclick="gotoDay(5)" title="点击直达 Day5 行程"><b>⭐⭐ 中街步行街</b></a><div class="meta">免费 · 全天 · 沈河区 · 沈河区中街路(地铁1号线中街站)
  <div class="links">
    <a class="ext" href="https://www.douyin.com/search/%E4%B8%AD%E8%A1%97%E6%AD%A5%E8%A1%8C%E8%A1%97" target="_blank" rel="noopener">📱 抖音看环境</a>
            <a class="ext" href="https://www.xiaohongshu.com/search_result?keyword=%E4%B8%AD%E8%A1%97%E6%AD%A5%E8%A1%8C%E8%A1%97" target="_blank" rel="noopener">📕 小红书</a>
    <a class="ext" href="https://uri.amap.com/search?keyword=%E4%B8%AD%E8%A1%97%E6%AD%A5%E8%A1%8C%E8%A1%97&city=%E6%B2%88%E9%98%B3" target="_blank" rel="noopener">🗺️ 高德地图</a></div>
  </div></div>
        <div class="bd">沈阳最老商圈，老边饺子 / 李连贵熏肉大饼 / 中街大果 / 夜景逛吃一站式。<div class="hl">📅 <b>Day5 · 18:30–19:30</b> ⏱ 故宫帅府步行可达，晚餐前消食</div></div></div>
'''
    caidian = '''      <div class="spot"><div class="hd"><a class="spot-link" onclick="gotoDay(6)" title="点击直达 Day6 行程"><b>⭐⭐ 彩电塔夜市</b></a><div class="meta">免费 · 约17:00–深夜 · 和平区 · 和平区彩电塔下(地铁2号线工业展览馆站)
  <div class="links">
    <a class="ext" href="https://www.douyin.com/search/%E5%BD%A9%E7%94%B5%E5%A1%94%E5%A4%9C%E5%B8%82" target="_blank" rel="noopener">📱 抖音看环境</a>
            <a class="ext" href="https://www.xiaohongshu.com/search_result?keyword=%E5%BD%A9%E7%94%B5%E5%A1%94%E5%A4%9C%E5%B8%82" target="_blank" rel="noopener">📕 小红书</a>
    <a class="ext" href="https://uri.amap.com/search?keyword=%E5%BD%A9%E7%94%B5%E5%A1%94%E5%A4%9C%E5%B8%82&city=%E6%B2%88%E9%98%B3" target="_blank" rel="noopener">🗺️ 高德地图</a></div>
  </div></div>
        <div class="bd">和平区彩电塔下小吃集群，烤串/炸串/小吃扫街，沈阳夜宵首选。<div class="hl">📅 <b>Day6 · 19:00–22:00</b> ⏱ 辽博返程后地铁2号线直达</div></div></div>
'''

    xita_marker = '''        <div class="bd">沈阳朝鲜族聚集地，韩餐天花板：脊骨汤 / 部队锅 / 炸鸡 / 打糕，孩子爱吃。<div class="hl">📅 <b>Day5 晚 / Day6 午 用餐</b> ⏱ 韩餐首选，从早开到晚</div></div></div>
'''
    if '中街步行街</b>' not in text:
        text = text.replace(xita_marker, xita_marker + '\n' + zhongjie, 1)

    liaoning_marker = '''        <div class="bd">辽宁文物主馆，藏品多、空调足，带娃友好；可作为九一八的轻松替代。<div class="hl">📅 <b>Day6 · 16:30–18:30</b> ⏱ 免费需提前预约</div></div></div>
'''
    if '彩电塔夜市</b>' not in text:
        text = text.replace(liaoning_marker, liaoning_marker + '\n' + caidian, 1)

    return text

for name in ['cloud.html', 'index.html']:
    p = BASE / name
    merged = merge(p)
    p.write_text(merged, encoding='utf-8')
    print(f'updated {p}')

print('done')
