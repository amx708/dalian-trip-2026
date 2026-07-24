import os
import re

src = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
out_dir = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\novpn-deploy'
out = os.path.join(out_dir, 'index.html')

s = open(src, encoding='utf-8').read()

# 0) 剥离腾讯地图实时组件（需要联网 + Key），保持免翻墙版零依赖、可离线
for tag in ('MAP_JS', 'MAP_TAB', 'MAP_PANEL'):
    s = re.sub(r'<!--%s_START-->.*?<!--%s_END-->\s*' % (tag, tag), '', s, flags=re.DOTALL)

# 1) 关掉 Firebase 后端（改回分享链接模式，无境外依赖）
s = s.replace(
    "var FB_URL='https://dalian-trip-ed4fd-default-rtdb.firebaseio.com';",
    "var FB_URL='';"
)

# 2) 说明框改为免翻墙 / 分享链接口径
s = s.replace(
    '💡 怎么用「编辑 / 云端同步」？（点开看说明）',
    '💡 怎么用「编辑 / 分享链接」？（点开看说明）'
)
s = s.replace(
    '自动存云端：</b>点「完成」后，你改过的内容会自动保存到 Firebase 云端。',
    '自动保存：</b>点「完成」后，你改过的内容自动存到本机（也会生成分享码）。'
)
s = s.replace(
    '家人同步：</b>直接把这个页面链接发给家人，他们打开链接就能看到最新版；不用再发什么分享码/链接。',
    '发给家人：</b>点「📤 复制分享链接」复制一条完整链接发微信，家人打开链接就自动载入你的版本。'
)
s = s.replace(
    '☁️ 当前是<b>Firebase 云端模式</b>：编辑自动同步，换手机或清浏览器缓存也不会丢（只要打开同一链接就会从云端加载最新版）。',
    '🇨🇳 本版本部署在国内，<b>免翻墙</b>可直接打开。同步靠「分享链接」：每次改动后点「复制分享链接」重发一次给家人即可（无需 VPN、无境外服务器）。'
)

os.makedirs(out_dir, exist_ok=True)
open(out, 'w', encoding='utf-8').write(s)
print('written:', out, 'len=', len(s))
print('FB_URL empty:', "var FB_URL='';" in s)
print('免翻墙 note present:', '免翻墙' in s)
