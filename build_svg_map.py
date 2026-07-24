import json

path = 'cloud.html'
s = open(path, encoding='utf-8').read()

# 1) 从 poi_data.json 重建 POIS
data = json.load(open('poi_data.json', encoding='utf-8'))
pois = [{'id': p['id'], 'name': p['name'], 'city': p['city'], 'day': p['day'],
         'order': p['order'], 'kind': p['kind'], 'lat': p['lat'], 'lng': p['lng']}
        for p in data]
pois_json = json.dumps(pois, ensure_ascii=False)

# 2) 新面板 HTML（离线 SVG 地图），带 sentinel 供离线版剥离
NEW_PANEL = r'''<!--MAP_PANEL_START-->
<section class="panel" id="map">
  <style>
    .map-toolbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0 12px}
    .map-city{border:1px solid var(--line);background:var(--card);border-radius:10px;padding:7px 16px;font-size:14px;cursor:pointer;color:var(--ink);transition:.15s}
    .map-city:hover{background:#f0f6fa}
    .map-city.on{background:var(--sea);color:#fff;border-color:var(--sea)}
    .map-legend{display:flex;gap:12px;flex-wrap:wrap;margin-left:auto;font-size:12.5px;color:var(--sub)}
    .lg-item{display:inline-flex;align-items:center;gap:5px}
    .lg-item i{width:12px;height:12px;border-radius:3px;display:inline-block}
    #mapSvg{width:100%;border-radius:16px;overflow:hidden;box-shadow:0 4px 18px rgba(20,136,201,.10);background:#eef3f7}
    .map-list{width:100%;max-height:240px;overflow:auto;border:1px solid var(--line);border-radius:12px;padding:8px;margin-top:12px;background:var(--card)}
    .ml-day{display:flex;align-items:center;gap:6px;font-weight:600;font-size:13px;margin:10px 6px 6px;color:var(--ink)}
    .ml-day i{width:10px;height:10px;border-radius:3px;display:inline-block}
    .ml-item{display:flex;align-items:center;gap:8px;padding:7px 8px;border-radius:8px;cursor:pointer;font-size:13px;color:var(--ink);transition:.12s}
    .ml-item:hover{background:#eef5fb}
    .ml-item.on{background:#dcecf7}
    .ml-dot{width:10px;height:10px;border-radius:50%;flex:0 0 auto}
    .ml-name{flex:1 1 auto;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .ml-tag{font-size:11px;color:var(--sub);background:#f0f4f8;border-radius:6px;padding:1px 6px;flex:0 0 auto}
    #mapInfo{display:none;margin-top:12px;padding:12px 14px;border-radius:12px;background:#eaf4fb;border:1px solid #cfe3f3;font-size:13px;line-height:1.8}
  </style>
  <h2>🗺️ 行程地图（离线示意图 · 按天分色）</h2>
  <div class="note">这是一张<b>离线手绘示意图</b>：按真实经纬度把景点画出来，按天用不同颜色连线，<b>不依赖任何地图服务、网络或 Key，永远能显示</b>。点地图上的彩色圆点，或下方名单里的名称，看当天安排并一键「🧭 高德 / 🗺️ 腾讯导航」。切换「🌊 大连 / 🏯 沈阳」看各自路线。</div>
  <div class="map-toolbar">
    <button type="button" class="map-city on" id="cityDl" onclick="switchCity('dl')">🌊 大连</button>
    <button type="button" class="map-city" id="citySy" onclick="switchCity('sy')">🏯 沈阳</button>
    <span class="map-legend" id="mapLegend"></span>
  </div>
  <div id="mapSvg"></div>
  <div id="mapInfo"></div>
  <div class="map-list" id="mapList"></div>
  <script>
  (function(){
    var POIS = __POIS__;
    var DAY_COLORS = {"1":"#1E88E5","2":"#E53935","3":"#43A047","4":"#8E24AA","5":"#FB8C00","6":"#00ACC1","7":"#6D4C41","T":"#9E9E9E"};
    var DAY_LABEL = {
      dl:{"1":"Day1 抵达·初体验","2":"Day2 老虎滩·棒棰岛","3":"Day3 东港·威尼斯","7":"Day7 俄街·中山广场"},
      sy:{"4":"Day4 抵达·太原街","5":"Day5 故宫·帅府·中街·西塔","6":"Day6 九一八·北陵"}
    };
    var curCity="dl", selectedId=null;
    function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
    function getDays(city){
      var pts=POIS.filter(function(p){return p.city===city;});
      var days=[];
      pts.forEach(function(p){ if(p.day!=="T"&&days.indexOf(p.day)<0) days.push(p.day); });
      days.sort();
      return days;
    }
    function proj(city){
      var pts=POIS.filter(function(p){return p.city===city;});
      var minLat=90,maxLat=-90,minLng=180,maxLng=-180;
      pts.forEach(function(p){ if(p.lat<minLat)minLat=p.lat; if(p.lat>maxLat)maxLat=p.lat; if(p.lng<minLng)minLng=p.lng; if(p.lng>maxLng)maxLng=p.lng; });
      var latPad=(maxLat-minLat)*0.15||0.05, lngPad=(maxLng-minLng)*0.15||0.05;
      return {minLat:minLat-latPad,maxLat:maxLat+latPad,minLng:minLng-lngPad,maxLng:maxLng+lngPad};
    }
    function renderSvg(city){
      var pts=POIS.filter(function(p){return p.city===city;});
      var b=proj(city), W=760,H=480,pad=20;
      function X(lng){ return pad+(lng-b.minLng)/(b.maxLng-b.minLng)*(W-2*pad); }
      function Y(lat){ return pad+(b.maxLat-lat)/(b.maxLat-b.minLat)*(H-2*pad); }
      var svg='<svg viewBox="0 0 '+W+' '+H+'" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block">';
      var days=getDays(city);
      days.forEach(function(d){
        var dp=pts.filter(function(p){return p.day===d;}).sort(function(a,bb){return a.order-bb.order;});
        if(dp.length>=2){
          var ps=dp.map(function(p){return X(p.lng).toFixed(1)+','+Y(p.lat).toFixed(1);}).join(' ');
          svg+='<polyline points="'+ps+'" fill="none" stroke="'+DAY_COLORS[d]+'" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>';
        }
      });
      pts.forEach(function(p){
        var x=X(p.lng),y=Y(p.lat),c=DAY_COLORS[p.day]||"#333";
        var r=(p.id===selectedId)?9:7;
        svg+='<g class="mk'+(p.id===selectedId?' sel':'')+'" data-id="'+p.id+'" style="cursor:pointer">';
        svg+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+r+'" fill="'+c+'" stroke="#fff" stroke-width="2"/>';
        svg+='<text x="'+x.toFixed(1)+'" y="'+(y+(selectedId===p.id?24:19)).toFixed(1)+'" font-size="10" fill="#2b3a45" text-anchor="middle" style="pointer-events:none">'+esc(p.name)+'</text>';
        svg+='</g>';
      });
      svg+='</svg>';
      var box=document.getElementById('mapSvg'); if(box) box.innerHTML=svg;
      var gs=document.querySelectorAll('#mapSvg .mk');
      for(var i=0;i<gs.length;i++){ gs[i].addEventListener('click',function(){ selectPoi(this.getAttribute('data-id')); }); }
    }
    function mlItem(p){
      var tag=p.kind==="hotel"?"住宿":p.kind==="transport"?"交通":p.kind==="food"?"美食":"景点";
      return '<div class="ml-item" id="ml-'+p.id+'" onclick="selectPoi(\''+p.id+'\')">'
        +'<span class="ml-dot" style="background:'+DAY_COLORS[p.day]+'"></span>'
        +'<span class="ml-name">'+esc(p.name)+'</span>'
        +'<span class="ml-tag">'+tag+'</span></div>';
    }
    function renderList(city){
      var pts=POIS.filter(function(p){return p.city===city;});
      var days=getDays(city), lh="";
      days.forEach(function(d){
        lh+='<div class="ml-day"><i style="background:'+DAY_COLORS[d]+'"></i>'+(DAY_LABEL[city][d]||("Day"+d))+'</div>';
        pts.filter(function(p){return p.day===d;}).sort(function(a,bb){return a.order-bb.order;}).forEach(function(p){ lh+=mlItem(p); });
      });
      var trans=pts.filter(function(p){return p.day==="T";});
      if(trans.length){
        lh+='<div class="ml-day"><i style="background:'+DAY_COLORS.T+'"></i>交通枢纽</div>';
        trans.forEach(function(p){ lh+=mlItem(p); });
      }
      var le=document.getElementById('mapList'); if(le) le.innerHTML=lh;
    }
    function renderLegend(city){
      var days=getDays(city), lg=document.getElementById('mapLegend'), html="";
      days.forEach(function(d){ html+='<span class="lg-item"><i style="background:'+DAY_COLORS[d]+'"></i>'+(DAY_LABEL[city][d]||("Day"+d))+'</span>'; });
      html+='<span class="lg-item"><i style="background:'+DAY_COLORS.T+'"></i>交通枢纽</span>';
      if(lg) lg.innerHTML=html;
    }
    function selectPoi(id){
      selectedId=id;
      var p=null; for(var i=0;i<POIS.length;i++){ if(POIS[i].id===id){p=POIS[i];break;} }
      if(!p) return;
      renderSvg(curCity);
      var items=document.querySelectorAll('.ml-item'); for(var k=0;k<items.length;k++){ items[k].classList.remove('on'); }
      var me=document.getElementById('ml-'+id); if(me) me.classList.add('on');
      var tag=p.kind==="hotel"?" · 住宿":p.kind==="transport"?" · 交通":p.kind==="food"?" · 美食":"";
      var cityName=p.city==="dl"?"大连":"沈阳";
      var amap='https://uri.amap.com/marker?position='+p.lng+','+p.lat+'&name='+encodeURIComponent(p.name)+'&src=dalian_trip&coordinate=gaode&callnative=1';
      var qq='https://apis.map.qq.com/uri/v1/marker?marker=coord:'+p.lat+','+p.lng+';title:'+encodeURIComponent(p.name)+';addr:'+encodeURIComponent(cityName)+'&referer=dalian_trip';
      var box=document.getElementById('mapInfo');
      box.innerHTML='<b>'+esc(p.name)+'</b><br>'+cityName+' · Day'+p.day+tag+'<br><a href="'+amap+'" target="_blank" style="color:#1E88E5;text-decoration:none;margin-right:12px">🧭 高德导航</a><a href="'+qq+'" target="_blank" style="color:#1E88E5;text-decoration:none">🗺️ 腾讯导航</a>';
      box.style.display='block';
    }
    window.switchCity=function(city){
      curCity=city; selectedId=null;
      document.getElementById('cityDl').classList.toggle('on',city==='dl');
      document.getElementById('citySy').classList.toggle('on',city==='sy');
      renderList(city); renderSvg(city); renderLegend(city);
      var info=document.getElementById('mapInfo'); if(info) info.style.display='none';
    };
    renderList('dl'); renderSvg('dl'); renderLegend('dl');
  })();
  </script>
</section>
<!--MAP_PANEL_END-->'''

NEW_PANEL = NEW_PANEL.replace('__POIS__', pois_json)

# 3) 插入 tab 按钮（在机场交通 tab 之后），带 sentinel
TAB = '\n    <!--MAP_TAB_START-->\n    <div class="tab" data-t="map">🗺️ 地图</div>\n    <!--MAP_TAB_END-->'
anchor_tab = '    <div class="tab" data-t="airport">机场交通</div>'
if anchor_tab in s:
    s = s.replace(anchor_tab, anchor_tab + TAB, 1)
else:
    print("WARN: airport tab anchor not found")

# 4) 插入面板（在 .foot 之前），带 sentinel
anchor_foot = '<div class="foot">'
if anchor_foot in s:
    s = s.replace(anchor_foot, NEW_PANEL + '\n\n' + anchor_foot, 1)
else:
    print("WARN: foot anchor not found")

open(path, 'w', encoding='utf-8').write(s)
print("written, size:", len(s))
print("has mapSvg:", 'id="mapSvg"' in s)
print("has map tab:", 'data-t="map"' in s)
print("has POIS embedded:", 'var POIS = [' in s)
