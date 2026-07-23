#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把景点卡片里的抖音/小红书链接改成「点开先唤起App，没装则1.2秒后回退网页」，接近高德体验。"""
import re, io

src = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
html = open(src, encoding='utf-8').read()

# 1) 抖音: https://www.douyin.com/search/<encoded>  ->  scheme snssdk1128://search?q=<encoded>
douyin_re = re.compile(
    r'<a class="ext" href="(https://www\.douyin\.com/search/[^"]+)" target="_blank" rel="noopener">([\s\S]*?)</a>'
)
def douyin_sub(m):
    if 'openPlatform' in m.group(0):
        return m.group(0)
    web = m.group(1)
    enc = web.split('/search/', 1)[1]
    scheme = 'snssdk1128://search?q=' + enc
    return ('<a class="ext" href="%s" target="_blank" rel="noopener" '
            'onclick="openPlatform(\'%s\',\'%s\');return false;">%s</a>'
            % (web, scheme, web, m.group(2)))

# 2) 小红书: https://www.xiaohongshu.com/search_result?keyword=<encoded>  ->  scheme xhsdiscover://search/result?keyword=<encoded>
xhs_re = re.compile(
    r'<a class="ext" href="(https://www\.xiaohongshu\.com/search_result\?keyword=[^"]+)" target="_blank" rel="noopener">([\s\S]*?)</a>'
)
def xhs_sub(m):
    if 'openPlatform' in m.group(0):
        return m.group(0)
    web = m.group(1)
    enc = web.split('keyword=', 1)[1]
    scheme = 'xhsdiscover://search/result?keyword=' + enc
    return ('<a class="ext" href="%s" target="_blank" rel="noopener" '
            'onclick="openPlatform(\'%s\',\'%s\');return false;">%s</a>'
            % (web, scheme, web, m.group(2)))

html2 = douyin_re.sub(douyin_sub, html)
html2 = xhs_re.sub(xhs_sub, html2)

# 3) 注入 openPlatform JS（若没注入过）
js = ("""
<script>
function openPlatform(scheme, web){
  var opened = false;
  var timer = setTimeout(function(){
    if(!document.hidden && !opened){ window.location.href = web; }
  }, 1200);
  document.addEventListener('visibilitychange', function(){
    if(document.hidden){ opened = true; clearTimeout(timer); }
  });
  window.location.href = scheme;
}
</script>
""")
if 'function openPlatform' not in html2:
    html2 = html2.replace('</body>', js + '\n</body>', 1)

n_d = len(re.findall(r'snssdk1128://search', html2))
n_x = len(re.findall(r'xhsdiscover://search/result', html2))
open('result_check.txt','w',encoding='utf-8').write('douyin_scheme=%d xhs_scheme=%d\n' % (n_d, n_x))

open(src, 'w', encoding='utf-8').write(html2)
print('done. douyin schemes:', n_d, ' xhs schemes:', n_x)
