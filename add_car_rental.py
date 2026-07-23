from pathlib import Path

BASE = Path(r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy')

NEW_BLOCK = '''    <h2 style="margin-top:28px">🚗 大连租车自驾方案（按需租）</h2>
    <div class="card">
      <table class="plan-table">
        <tr><th>方案</th><th>适合车型</th><th>预估费用</th><th>建议天数</th></tr>
        <tr><td><b>8人拆2辆轿车/SUV</b></td><td>日产轩逸/丰田卡罗拉/大众朗逸等5座，或哈弗H6/坦克300等SUV</td><td>¥250–400/辆·天（暑期旺季）+ 油费约¥80–150/天/辆 + 停车¥20–50/天</td><td>2天（金石滩1天+旅顺1天）</td></tr>
        <tr><td><b>1辆7座MPV+1辆轿车</b></td><td>别克GL8/传祺M8 + 1辆5座轿车</td><td>MPV ¥500–700/天 + 轿车¥250–350/天 + 油费/停车</td><td>2天（家庭舒适度最高）</td></tr>
      </table>
      <div class="note" style="margin-top:10px">
        <b>哪里租：</b>神州租车、一嗨租车、携程租车等在大连周水子机场、大连站、大连北站及市区均有网点，建议提前在 APP 下单锁价，机场/高铁门店略贵。<br>
        <b>租几天划算：</b>大连市区地铁+打车足够，<b>不必全程租车</b>；只在去<b>金石滩</b>（地铁3号线也能到，但自驾更灵活）和<b>旅顺</b>（偏远、景点分散）的两天租最划算。本次双城行程已安排高铁往返沈阳，异地还车（如沈阳还车）会加服务费，不推荐。<br>
        <b>提醒：</b>取车时 360° 拍照/录像验车；建议买齐保险（基础险+不计免赔）；滨海路旺季拥堵、景区停车位紧张，尽量早出发；油费按「满油取还」结算。
      </div>
    </div>
'''

def insert(file_path: Path) -> str:
    text = file_path.read_text(encoding='utf-8')
    marker = '    <div class="note">💡 <b>打车 vs 租车（8人同行）：</b>网约车/滴滴市内每段 ¥10–30/辆，8人拆 2 辆或临时打商务车最省心，地铁+高铁已覆盖主线，不用操心停车。租车除非有老司机且想跑旅顺/金石滩偏远线，否则不推荐——大连滨海路旺季易堵、景区停车难且贵；沈阳景点集中，地铁+打车足够；跨城还车还有异地费。</div>\n\n'
    if '大连租车自驾方案' in text:
        print(f'skip {file_path} (already has car rental)')
        return text
    if marker not in text:
        print(f'WARNING: marker not found in {file_path}')
        return text
    text = text.replace(marker, marker + NEW_BLOCK)
    return text

for name in ['cloud.html', 'index.html']:
    p = BASE / name
    text = insert(p)
    p.write_text(text, encoding='utf-8')
    print(f'updated {p}')

print('done')
