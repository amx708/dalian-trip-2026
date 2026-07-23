#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 🐝 马蜂窝(mafengwo) 按钮换成 🧳 携程(ctrip) 按钮。
携程官方唤起 App 深链: ctrip://wireless/h5?url=<base64(inner)>&type=1
inner = ticket/index.html#/dest/k-keyword-0/s-tickets?keyword=<ENC>
"""
import re, base64

src = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
html = open(src, encoding='utf-8').read()

mfw_re = re.compile(
    r'<a class="ext" href="https://www\.mafengwo\.cn/search/q\.php\?q=([^"]+)" target="_blank" rel="noopener" onclick="[^"]*">([\s\S]*?)</a>'
)
def repl(m):
    enc = m.group(1)                       # 已 URL 编码的中文关键词
    inner = 'ticket/index.html#/dest/k-keyword-0/s-tickets?keyword=' + enc
    b64 = base64.b64encode(inner.encode('utf-8')).decode().rstrip('=')
    scheme = 'ctrip://wireless/h5?url=' + b64 + '&type=1'
    web = 'https://m.ctrip.com/webapp/ticket/index.html#/dest/k-keyword-0/s-tickets?keyword=' + enc
    return ('<a class="ext" href="%s" target="_blank" rel="noopener" '
            'onclick="openPlatform(\'%s\',\'%s\');return false;">🧳 携程</a>' % (web, scheme, web))

before = len(mfw_re.findall(html))
html2 = mfw_re.sub(repl, html)
open(src, 'w', encoding='utf-8').write(html2)
print('mafengwo anchors before:', before)
print('ctrip scheme anchors now:', html2.count('ctrip://wireless/h5?url='))
print('🧳 携程 buttons:', html2.count('🧳 携程'))
print('mafengwo remaining:', html2.count('mafengwo.cn/search/q.php'))
