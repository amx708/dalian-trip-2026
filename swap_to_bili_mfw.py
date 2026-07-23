#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把景点卡片的 抖音/小红书 按钮 换成 哔哩哔哩(B站视频) + 马蜂窝(攻略)。
- B站: 用可靠协议 bilibili://search?keyword= 先唤起App，失败回退网页搜索
- 马蜂窝: 用网页搜索链接(安卓 App Links 可跳 App)
"""
import re

src = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
html = open(src, encoding='utf-8').read()

# 抖音 -> B站
douyin_re = re.compile(
    r'<a class="ext" href="https://www\.douyin\.com/search/([^"]+)" target="_blank" rel="noopener" onclick="[^"]*">([\s\S]*?)</a>'
)
def d(m):
    enc = m.group(1)
    web = 'https://search.bilibili.com/all?keyword=' + enc
    scheme = 'bilibili://search?keyword=' + enc
    return ('<a class="ext" href="%s" target="_blank" rel="noopener" '
            'onclick="openPlatform(\'%s\',\'%s\');return false;">📺 B站</a>' % (web, scheme, web))

# 小红书 -> 马蜂窝 (无可靠协议，纯网页，安卓可 App Link 跳 App)
xhs_re = re.compile(
    r'<a class="ext" href="https://www\.xiaohongshu\.com/search_result\?keyword=([^"]+)" target="_blank" rel="noopener" onclick="[^"]*">([\s\S]*?)</a>'
)
def x(m):
    enc = m.group(1)
    web = 'https://www.mafengwo.cn/search/q.php?q=' + enc
    return ('<a class="ext" href="%s" target="_blank" rel="noopener" '
            'onclick="openPlatform(\'\',\'%s\');return false;">🐝 马蜂窝</a>' % (web, web))

before_d = len(douyin_re.findall(html))
before_x = len(xhs_re.findall(html))
html2 = douyin_re.sub(d, html)
html2 = xhs_re.sub(x, html2)
after_bili = len(re.findall(r'search\.bilibili\.com/all\?keyword=', html2))
after_mfw = len(re.findall(r'mafengwo\.cn/search/q\.php\?q=', html2))

open(src, 'w', encoding='utf-8').write(html2)
print('douyin anchors before/after:', before_d, '-> bilibili:', after_bili)
print('xhs anchors before/after:', before_x, '-> mafengwo:', after_mfw)
