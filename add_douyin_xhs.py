#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 📱抖音 / 📕小红书 作为纯网页链接补回每个 B站 按钮之后(走浏览器, 不试协议)。"""
import re

src = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
html = open(src, encoding='utf-8').read()

bili_re = re.compile(
    r'(<a class="ext" href="https://search\.bilibili\.com/all\?keyword=([^"]+)"[^>]*>[\s\S]*?</a>)'
)
def add(m):
    whole = m.group(1)
    enc = m.group(2)
    douyin = ('<a class="ext" href="https://www.douyin.com/search/%s" target="_blank" rel="noopener" '
              'onclick="openPlatform(\'\',\'https://www.douyin.com/search/%s\');return false;">📱 抖音</a>' % (enc, enc))
    xhs = ('<a class="ext" href="https://www.xiaohongshu.com/search_result?keyword=%s" target="_blank" rel="noopener" '
           'onclick="openPlatform(\'\',\'https://www.xiaohongshu.com/search_result?keyword=%s\');return false;">📕 小红书</a>' % (enc, enc))
    return whole + douyin + xhs

before_d = html.count('douyin.com/search/')
before_x = html.count('xiaohongshu.com/search_result?keyword=')
html2 = bili_re.sub(add, html)
open(src, 'w', encoding='utf-8').write(html2)
print('B站锚点数(应被处理):', len(bili_re.findall(html)))
print('douyin 链接数: %d -> %d' % (before_d, html2.count('douyin.com/search/')))
print('xiaohongshu 链接数: %d -> %d' % (before_x, html2.count('xiaohongshu.com/search_result?keyword=')))
