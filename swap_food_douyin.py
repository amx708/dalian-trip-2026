#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""美食卡片里的抖音链接(无 class/rel/onclick、关键词为中文) 换成 B站。"""
import re, urllib.parse

src = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
html = open(src, encoding='utf-8').read()

food_re = re.compile(r'<a href="https://www\.douyin\.com/search/([^"]+)" target="_blank">([\s\S]*?)</a>')
def f(m):
    kw = m.group(1)
    enc = urllib.parse.quote(kw, safe='')
    web = 'https://search.bilibili.com/all?keyword=' + enc
    scheme = 'bilibili://search?keyword=' + enc
    return ('<a class="ext" href="%s" target="_blank" rel="noopener" '
            'onclick="openPlatform(\'%s\',\'%s\');return false;">📺 B站</a>' % (web, scheme, web))

before = len(food_re.findall(html))
html2 = food_re.sub(f, html)
open(src, 'w', encoding='utf-8').write(html2)
print('food douyin before:', before, '-> bilibili anchors now:', html2.count('search.bilibili.com/all?keyword='))
