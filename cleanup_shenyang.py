import re
from pathlib import Path

BASE = Path(r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy')

def cleanup(text: str) -> str:
    # 情况1：还能找到完整方案网格开头（含注释）
    m = re.search(r'<!-- 沈阳2日游方案（手账参考版） -->\s*<style>.*?</style>\s*<h2[^>]*>🗺️ 沈阳 2 日游方案.*?</h2>\s*<div class="note">.*?</div>\s*<div class="sy3-wrap">', text, flags=re.S)
    if m:
        start = m.start()
        # 从 sy3-wrap 开始按 div 深度找闭合
        scan = m.end()
        depth = 1
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
                            while end < len(text) and text[end] in ' \t\n':
                                end += 1
                            return text[:start] + '\n' + text[end:]
                    in_tag = False
                    tag_buf = []
            scan += 1
        return text

    # 情况2：只剩残留 sy3-item 块，从第一个 sy3-item 清理到核心景点标题前
    marker = '<h2 style="margin-top:28px">📍 沈阳 2 日方案 & 核心景点（Day5 / Day6）</h2>'
    marker_pos = text.find(marker)
    first_item = text.find('<div class="sy3-item">')
    if marker_pos != -1 and first_item != -1 and first_item < marker_pos:
        # 找 marker 之前的最后一个 </div>，即 sy3-wrap 的闭合
        # 从 marker_pos 往前跳过空白
        end = marker_pos
        while end > first_item and text[end-1] in ' \t\n':
            end -= 1
        # 现在 text[end-6:end] 应该是 </div>
        return text[:first_item] + '\n' + text[end:]

    return text

for name in ['cloud.html', 'index.html']:
    p = BASE / name
    text = p.read_text(encoding='utf-8')
    cleaned = cleanup(text)
    p.write_text(cleaned, encoding='utf-8')
    print(f'cleaned {p}')

print('done')
