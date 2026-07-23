import io

html = open('cloud.html', encoding='utf-8').read()

# --- Simplified-Chinese row data (converted from shenyang_food_cp.html) ---
# (ep, item, price, scene, cp_key, badge_text, badge_class, review)
rows = [
 ("E1","大猪蹄双人餐","138元<br><small>人均69</small>","西塔韩餐","S","S","b-S","满桌＋无限续小菜，多人分摊最值"),
 ("E1","紫菜包饭(金枪鱼)","15元","西塔","B","B","b-B","方便单食，但米饭为主、蛋白低"),
 ("E1","米肠／血肠","7.5元","西塔","B","B","b-B","猪血糯米，微血回味，不爱血慎点"),
 ("E1","釜山鱼饼","10元","西塔","B","B","b-B","有嚼劲汤鲜，但偏咸"),
 ("E2","焦烤鸡架","7.5元<br><small>15两</small>","街边／西塔","S","S","b-S","外焦里嫩炭香，视频当日最爱"),
 ("E2","辣炒鸡架","16元","饭馆","A","A","b-A","甜辣下酒，配饭也行"),
 ("E2","拌鸡架","未标价","麻辣拌店","A","A","b-A","先熏再甜酸酱拌，沈阳人爱甜"),
 ("E2","肉末茄子","18元","鸡架店","B","B","b-B","下饭神器，单吃偏甜"),
 ("E3","包子","1.5元","早市","S","S","b-S","茴香／猪肉，馅少但香"),
 ("E3","豆腐脑","2.5元","早市","S","S","b-S","丝滑带焦香，比哈尔滨好"),
 ("E3","炸糕(红豆)","~2元","早市","S","S","b-S","红豆馅不甜、酥脆"),
 ("E3","鸡蛋汉堡","4元","早市","S","S","b-S","有肉馅，便宜版满福堡"),
 ("E3","牛肉烧麦(6个)","5元","早市","S","S","b-S","单颗＜1元，清蒸牛肉香"),
 ("E3","羊杂汤","6元<br><small>汤续</small>","早市","S","S","b-S","汤无限续，羊杂多，良心价"),
 ("E3","甜姑娘(半斤)","3元","早市收市","S","S","b-S","番茄＋奶香，没吃过必试"),
 ("E4","吊炉饼","1.3元","菜市场","S","S","b-S","外酥内嫩，层次丰富(全场最便宜)"),
 ("E4","包子","1.5元","菜市场","S","S","b-S","茴香鸡蛋／白菜肉"),
 ("E4","金家冷面","12元","菜市场","S","S","b-S","滑溜Q弹、酸甜，必吃"),
 ("E4","锅包肉(番茄+老式)","未标价","菜市场","S","S","b-S","老式超脆，视频说吊打上海"),
 ("E4","黏食盒(驴打滚+凉糕+切糕)","27.8元","菜市场","B","B","b-B","为冲金额买，糯到超载，买1种就够"),
 ("E4","八旗手工肠(肉枣)","18元/斤","菜市场","B","B","b-B","甜，像台式香肠"),
 ("E4","熏肉大饼","8元","菜市场","mine","⚠","b-mine","真材实料但烟熏味不足，差点意思"),
 ("E5","7元盒饭(实付8)","8元","路边","S","S","b-S","现炒现炸，热食王，性价比炸裂"),
 ("E5","15元自助餐","15元","自助","A","A","b-A","80菜＋水果＋冷气，选择王"),
 ("E5","锅包肉+杀猪菜(现做)","~70元/桌","必吃榜饭馆","love","★","b-love","现点现做，reviewer真·最爱(非比价档)"),
]

tbody = "\n".join(
  '        <tr data-cp="{cp}"><td class="ep-tag">{ep}</td><td><b>{item}</b></td>'
  '<td class="price">{price}</td><td>{scene}</td>'
  '<td><span class="badge {bc}">{bt}</span></td><td>{rev}</td></tr>'.format(
    cp=r[4], ep=r[0], item=r[1], price=r[2], scene=r[3], bc=r[6], bt=r[5], rev=r[7])
  for r in rows)

block = (
'    <h3>📊 沈阳美食 CP 值总表（视频实测，仅供参考）</h3>\n'
'    <div class="note">下面这张表来自 5 支沈阳美食视频的实吃测评，按「每元获得感」给 CP 评级：<b>S 顶值 / A 高值 / B 中 / ⚠ 地雷 / ★ 最爱</b>。价格为视频当时实测，可能变动，以大众点评实时为准。点上方按钮可按评级筛选。</div>\n'
'    <style>\n'
'      .sy-cp{margin-top:4px}\n'
'      .sy-cp .filters{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 14px}\n'
'      .sy-cp .filters button{border:1px solid var(--line);background:#fff;color:var(--ink);padding:6px 14px;border-radius:20px;cursor:pointer;font-size:13px;transition:.15s}\n'
'      .sy-cp .filters button:hover{border-color:#C2700F;color:#C2700F}\n'
'      .sy-cp .filters button.on{background:#C2700F;color:#fff;border-color:#C2700F}\n'
'      .sy-cp .badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:700;color:#fff;white-space:nowrap}\n'
'      .sy-cp .b-S{background:#2a9d8f} .sy-cp .b-A{background:#e9c46a;color:#5a4a00}\n'
'      .sy-cp .b-B{background:#8d99ae} .sy-cp .b-mine{background:#e63946} .sy-cp .b-love{background:#f4a261;color:#5a3000}\n'
'      .sy-cp .price{font-weight:700;color:#C2700F;white-space:nowrap}\n'
'      .sy-cp .price small{font-weight:400;color:var(--sub);font-size:11.5px}\n'
'      .sy-cp .ep-tag{font-size:11.5px;color:var(--sub);white-space:nowrap}\n'
'      .sy-cp .pill{display:inline-block;background:#fdf1e7;color:#C2700F;border:1px solid #f3d2b8;padding:2px 10px;border-radius:20px;font-size:12.5px;margin:2px 4px 2px 0}\n'
'    </style>\n'
'    <div class="sy-cp">\n'
'      <div class="filters">\n'
'        <button class="on" data-f="all">全部</button>\n'
'        <button data-f="S">S 顶值</button>\n'
'        <button data-f="A">A 高值</button>\n'
'        <button data-f="B">B 中</button>\n'
'        <button data-f="mine">⚠ 地雷</button>\n'
'        <button data-f="love">★ 最爱</button>\n'
'      </div>\n'
'      <div class="card">\n'
'        <table class="plan-table">\n'
'          <thead><tr><th>集</th><th>品项</th><th>价格</th><th>场景</th><th>CP</th><th>一句点评</th></tr></thead>\n'
'          <tbody id="syCpRows">\n'
) + tbody + (
'\n          </tbody>\n'
'        </table>\n'
'      </div>\n'
'      <div class="note">🏷️ 图例：<b>E1</b> 西塔韩食 · <b>E2</b> 鸡架之王 · <b>E3</b> 早市100元 · <b>E4</b> 菜市场100元 · <b>E5</b> 盒饭vs自助。<br>\n'
'      💡 结论：<span class="pill">S 顶值：早市小吃 / 焦烤鸡架 / 7元盒饭 / 吊炉饼 / 冷面</span><span class="pill">⚠ 地雷：熏肉大饼(味淡)</span><span class="pill">★ 最爱：现做锅包肉+杀猪菜</span></div>\n'
'      <script>\n'
'        (function(){\n'
'          var box=document.querySelector(".sy-cp"); if(!box) return;\n'
'          var btns=box.querySelectorAll(".filters button");\n'
'          var rows=box.querySelectorAll("#syCpRows tr");\n'
'          btns.forEach(function(b){\n'
'            b.addEventListener("click",function(){\n'
'              btns.forEach(function(x){x.classList.remove("on")});\n'
'              b.classList.add("on");\n'
'              var f=b.dataset.f;\n'
'              rows.forEach(function(r){ r.style.display=(f==="all"||r.dataset.cp===f)?"":"none"; });\n'
'            });\n'
'          });\n'
'        })();\n'
'      </script>\n'
'    </div>\n\n'
)

anchor = '    <h2 style="margin-top:28px">🍸 沈阳夜生活（可去可不去）</h2>'
assert anchor in html, "anchor not found"
assert html.count(anchor) == 1, "anchor not unique"
html = html.replace(anchor, block + anchor, 1)

open('cloud.html', 'w', encoding='utf-8').write(html)
print("inserted block; new size=", len(html))
print("rows inserted:", len(rows))
