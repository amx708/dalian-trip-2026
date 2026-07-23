# -*- coding: utf-8 -*-
path = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
s = open(path, encoding='utf-8').read()

# 1) 水月松间 Day4 -> Day3 (旅顺现在归 Day3；Day4 是高铁日)
old1 = 'Day4 可选旅顺回来顺路首选'
new1 = 'Day3 可选旅顺回来顺路首选'
c1 = s.count(old1)
assert c1 == 1, ('water-moon Day4 count', c1)
s = s.replace(old1, new1)

# 2) 删除金石滩 spot 卡（发起人计划已移除；不应再指向任何一天）
start = '      <div class="spot"><div class="hd"><a class="spot-link" onclick="gotoDay(3)" title="点击直达 Day3 行程"><b>⭐⭐⭐ 金石滩度假区</b>'
end = '观光环线20元不限次</div></div></div>'
i = s.find(start)
assert i != -1, 'jinshitan start not found'
j = s.find(end, i)
assert j != -1, 'jinshitan end not found'
j2 = j + len(end)
# 吞掉结尾换行，避免留空行
if s[j2:j2+1] == '\n':
    j2 += 1
s = s[:i] + s[j2:]

open(path, 'w', encoding='utf-8').write(s)
print('OK. 水月松间 Day4->Day3:', c1)
print('金石滩 card removed. remaining 金石滩:', s.count('金石滩'))
print('remaining gotoDay(4):', s.count('gotoDay(4)'))
