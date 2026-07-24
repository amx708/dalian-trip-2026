# -*- coding: utf-8 -*-
"""把腾讯地图标签页注入 cloud.html（仅主版本；免翻墙版由 make_novpn 剥离）。"""
import json

SRC = r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html'
KEY = "IACBZ-D3BLJ-NMWFG-XVZOS-BYINK-GMFRD"

# 精简 POI 数据
raw = json.load(open("poi_data.json", encoding="utf-8"))
pois = [{"id": p["id"], "name": p["name"], "city": p["city"], "day": p["day"],
         "order": p["order"], "kind": p["kind"], "lat": p["lat"], "lng": p["lng"]} for p in raw]
pois_js = json.dumps(pois, ensure_ascii=False, separators=(",", ":"))

# 1) head JSAPI 脚本
HEAD = ('<!--MAP_JS_START-->\n'
        '<script src="https://map.qq.com/api/gljs?v=1&key=%s"></script>\n'
        '<!--MAP_JS_END-->\n'
        '</head>') % KEY

# 2) 标签按钮
TAB = ('<!--MAP_TAB_START-->\n'
       '    <div class="tab" data-t="map">🗺️ 地图</div>\n'
       '<!--MAP_TAB_END-->\n')

# 3) 地图面板（含内联样式、坐标数据、初始化脚本）
PANEL = '''<!--MAP_PANEL_START-->
<section class="panel" id="map">
  <style>
    #tmap{height:540px;width:100%;border-radius:16px;overflow:hidden;box-shadow:0 4px 18px rgba(20,136,201,.10);background:#eef3f7}
    .map-toolbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0 12px}
    .map-city{border:1px solid var(--line);background:var(--card);border-radius:10px;padding:7px 16px;font-size:14px;cursor:pointer;color:var(--ink);transition:.15s}
    .map-city:hover{background:#f0f6fa}
    .map-city.on{background:var(--sea);color:#fff;border-color:var(--sea)}
    .map-legend{display:flex;gap:12px;flex-wrap:wrap;margin-left:auto;font-size:12.5px;color:var(--sub)}
    .lg-item{display:inline-flex;align-items:center;gap:5px}
    .lg-item i{width:12px;height:12px;border-radius:3px;display:inline-block}
    .map-err{padding:50px 20px;text-align:center;color:var(--sub);font-size:14px;line-height:1.7}
  </style>
  <h2>🗺️ 行程地图（腾讯地图 · 按天分色）</h2>
  <div class="note">点任意标点弹窗看当天安排；切换「🌊 大连 / 🏯 沈阳」看各自路线。<b>底图需联网</b>加载腾讯地图（免翻墙版不含此图，请用本主版本或手机系统浏览器打开）。</div>
  <div class="map-toolbar">
    <button type="button" class="map-city on" id="cityDl" onclick="switchCity('dl')">🌊 大连</button>
    <button type="button" class="map-city" id="citySy" onclick="switchCity('sy')">🏯 沈阳</button>
    <span class="map-legend" id="mapLegend"></span>
  </div>
  <div id="tmap"></div>
  <script>
  (function(){
    var POIS = __POIS__;
    var DAY_COLORS = {"1":"#1E88E5","2":"#E53935","3":"#43A047","4":"#8E24AA","5":"#FB8C00","6":"#00ACC1","7":"#6D4C41","T":"#9E9E9E"};
    var DAY_LABEL = {
      dl:{"1":"Day1 抵达·初体验","2":"Day2 老虎滩·棒棰岛","3":"Day3 东港·威尼斯","7":"Day7 俄街·中山广场"},
      sy:{"4":"Day4 抵达·太原街","5":"Day5 故宫·帅府·中街·西塔","6":"Day6 九一八·北陵"}
    };
    var CENTER = {dl:[38.90,121.62], sy:[41.80,123.43]};
    var map, mLayer, pLayer, info, inited=false, curCity="dl";

    function initMap(){
      if(inited) return; inited=true;
      var box=document.getElementById("tmap");
      if(typeof TMap==="undefined"){
        box.innerHTML='<div class="map-err">⚠️ 地图组件加载失败<br>请确认网络可访问腾讯地图（map.qq.com），或用手机系统浏览器打开本页面。</div>';
        return;
      }
      map=new TMap.Map("tmap",{center:new TMap.LatLng(CENTER.dl[0],CENTER.dl[1]),zoom:11});
      mLayer=new TMap.MultiMarker({map:map,geometries:[]});
      pLayer=new TMap.MultiPolyline({map:map,geometries:[]});
      info=new TMap.InfoWindow({map:map,visible:false});
      mLayer.on("click",function(e){
        var p=e.geometry.properties;
        var tag = p.kind==="hotel"?" · 住宿":p.kind==="transport"?" · 交通":p.kind==="food"?" · 美食":"";
        info.setPosition(e.geometry.position);
        info.setContent('<div style="padding:6px 10px;font-size:13px;line-height:1.5"><b>'+p.name+'</b><br>'+(p.city==="dl"?"大连":"沈阳")+" · Day"+p.day+tag+"</div>");
        info.setVisible(true);
      });
      renderCity("dl");
    }
    window.switchCity=function(city){
      curCity=city;
      document.getElementById("cityDl").classList.toggle("on",city==="dl");
      document.getElementById("citySy").classList.toggle("on",city==="sy");
      if(!inited){ initMap(); }
      if(inited){ renderCity(city); if(map){ map.resize(); } }
    };
    function renderCity(city){
      var pts=POIS.filter(function(p){return p.city===city;});
      var days=[];
      pts.forEach(function(p){ if(p.day!=="T"&&days.indexOf(p.day)<0) days.push(p.day); });
      days.sort();
      var styles={};
      var geos=pts.map(function(p){
        var c=DAY_COLORS[p.day]||"#333";
        styles["m"+p.day]={width:30,height:30,anchor:{x:15,y:30},
          content:'<div style="width:30px;height:30px;border-radius:50%;background:'+c+';color:#fff;border:2px solid #fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;box-shadow:0 1px 5px rgba(0,0,0,.35)">'+p.day+'</div>'};
        return {id:p.id,styleId:"m"+p.day,position:new TMap.LatLng(p.lat,p.lng),properties:p};
      });
      mLayer.setStyles(styles);
      mLayer.setGeometries(geos);
      var pstyles={},pgeos=[];
      days.forEach(function(d){
        var dp=pts.filter(function(p){return p.day===d;}).sort(function(a,b){return a.order-b.order;});
        if(dp.length>=2){
          pstyles["s"+d]={color:DAY_COLORS[d]||"#333",width:5,borderWidth:1,borderColor:"#ffffff",lineCap:"round",lineJoin:"round"};
          pgeos.push({id:"d"+d,styleId:"s"+d,paths:dp.map(function(p){return new TMap.LatLng(p.lat,p.lng);})});
        }
      });
      pLayer.setStyles(pstyles);
      pLayer.setGeometries(pgeos);
      var b=new TMap.LatLngBounds();
      pts.forEach(function(p){ b.extend(new TMap.LatLng(p.lat,p.lng)); });
      map.fitBounds(b,{padding:{top:50,bottom:50,left:50,right:50}});
      var lg=document.getElementById("mapLegend");
      var html=days.map(function(d){
        return '<span class="lg-item"><i style="background:'+DAY_COLORS[d]+'"></i>'+(DAY_LABEL[city][d]||("Day"+d))+'</span>';
      }).join("");
      html+='<span class="lg-item"><i style="background:'+DAY_COLORS.T+'"></i>交通枢纽</span>';
      lg.innerHTML=html;
    }
    window.__initTripMap=function(){ if(!inited){ initMap(); } };
    window.__tripMapResize=function(){ if(map){ setTimeout(function(){ map.resize(); },50); } };
  })();
  </script>
</section>
<!--MAP_PANEL_END-->'''

s = open(SRC, encoding="utf-8").read()

# 插入 head 脚本
if "<!--MAP_JS_START-->" not in s:
    assert "</head>" in s, "no </head>"
    s = s.replace("</head>", HEAD, 1)

# 插入 tab 按钮（在机场 tab 后）
if "<!--MAP_TAB_START-->" not in s:
    tab_anchor = '    <div class="tab" data-t="airport">机场交通</div>\n'
    assert tab_anchor in s, "tab anchor not found"
    s = s.replace(tab_anchor, tab_anchor + TAB, 1)

# 插入面板（在机场 section 结束 </section> 后、.foot 前）
if "<!--MAP_PANEL_START-->" not in s:
    panel_anchor = '  </section>\n\n  <div class="foot">'
    assert panel_anchor in s, "panel anchor not found"
    s = s.replace(panel_anchor, PANEL + "\n" + panel_anchor, 1)

# 修改 showPanel：地图 tab 打开时初始化/resize
if "window.__initTripMap" not in s:
    old_sp = "    if(panel)panel.classList.add('on');\n    return panel;"
    new_sp = ("    if(panel)panel.classList.add('on');\n"
              "    if(name==='map'){ if(window.__initTripMap)window.__initTripMap(); if(window.__tripMapResize)window.__tripMapResize(); }\n"
              "    return panel;")
    assert old_sp in s, "showPanel body not found"
    s = s.replace(old_sp, new_sp, 1)

s = s.replace("__POIS__", pois_js)

open(SRC, "w", encoding="utf-8").write(s)
print("OK injected. len=", len(s))
print("has MAP_JS:", "<!--MAP_JS_START-->" in s)
print("has MAP_TAB:", "<!--MAP_TAB_START-->" in s)
print("has MAP_PANEL:", "<!--MAP_PANEL_START-->" in s)
print("showPanel patched:", "window.__initTripMap" in s)
print("POIS embedded:", '"dalian_airport"' in s)
print("poi count:", s.count('"id":"'))
