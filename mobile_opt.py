import re
from pathlib import Path

BASE = Path(r'C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy')

EDIT_HELP_CSS = '''
  .edithelp{position:relative;margin:0;padding:0;}
  .edithelp > summary{list-style:none;cursor:pointer;font-size:16px;padding:6px 8px;border-radius:8px;background:rgba(255,255,255,.15);color:#fff;line-height:1;}
  .edithelp > summary::-webkit-details-marker{display:none;}
  .edithelp-body{position:absolute;bottom:calc(100% + 10px);right:0;width:min(320px,calc(100vw - 24px));background:#f0f9ff;border:1px solid #bae6fd;border-radius:12px;padding:12px 14px;font-size:13px;color:#0f172a;line-height:1.65;box-shadow:0 4px 16px rgba(2,132,199,.18);max-height:70vh;overflow:auto;z-index:1000;}
  .edithelp-body p{margin:6px 0;}
'''

EDIT_BAR_BLOCK_OLD = '''  <div id="editbar">
    <button id="editToggle" type="button">✏️ 编辑</button>
    <button id="editReset" type="button">↺ 还原</button>
    <span id="editStatus">🔒 只读模式（点「编辑」可改）</span>
  </div>
  <details class="edithelp" style="position:fixed;left:10px;right:10px;bottom:104px;z-index:998;margin:0;padding:10px 13px;background:#f0f9ff;border:1px solid #bae6fd;border-radius:12px;font-size:13px;color:#0f172a;line-height:1.65;max-height:64vh;overflow:auto;box-shadow:0 4px 16px rgba(2,132,199,.18);">
    <summary style="cursor:pointer;font-weight:700;color:#0369a1;">💡 怎么用「编辑 / 云端同步」？（点开看说明）</summary>
    <div style="margin-top:8px;">
      <p style="margin:6px 0;"><b>① 改内容：</b>点左下角「✏️ 编辑」，攻略里大部分文字（行程表、备注、卡片等）会变成可直接修改；改完点「🔒 完成」。</p>
      <p style="margin:6px 0;"><b>② 自动存云端：</b>点「完成」后，你改过的内容会自动保存到 Firebase 云端。</p>
      <p style="margin:6px 0;"><b>③ 家人同步：</b>直接把这个页面链接发给家人，他们打开链接就能看到最新版；不用再发什么分享码/链接。</p>
      <p style="margin:6px 0;color:#0f766e;background:#ccfbf1;padding:7px 9px;border-radius:8px;">☁️ 当前是<b>Firebase 云端模式</b>：编辑自动同步，换手机或清浏览器缓存也不会丢（只要打开同一链接就会从云端加载最新版）。</p>
    </div>
  </details>'''

EDIT_BAR_BLOCK_NEW = '''  <div id="editbar">
    <button id="editToggle" type="button">✏️ 编辑</button>
    <button id="editReset" type="button">↺ 还原</button>
    <span id="editStatus">🔒 只读模式（点「编辑」可改）</span>
    <details class="edithelp">
      <summary>💡</summary>
      <div class="edithelp-body">
        <p><b>① 改内容：</b>点左下角「✏️ 编辑」，攻略里大部分文字（行程表、备注、卡片等）会变成可直接修改；改完点「🔒 完成」。</p>
        <p><b>② 自动存云端：</b>点「完成」后，你改过的内容会自动保存到 Firebase 云端。</p>
        <p><b>③ 家人同步：</b>直接把这个页面链接发给家人，他们打开链接就能看到最新版；不用再发什么分享码/链接。</p>
        <p style="color:#0f766e;background:#ccfbf1;padding:7px 9px;border-radius:8px;">☁️ 当前是<b>Firebase 云端模式</b>：编辑自动同步，换手机或清浏览器缓存也不会丢（只要打开同一链接就会从云端加载最新版）。</p>
      </div>
    </details>
  </div>'''

TABLE_CARD_CSS = '''
  /* 手机端表格转卡片，避免左右滑动 */
  @media(max-width:680px){
    .plan-table, .plan-table thead, .plan-table tbody, .plan-table th, .plan-table td, .plan-table tr{display:block;}
    .plan-table thead tr{display:none;}
    .plan-table tr{margin-bottom:12px;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--card);}
    .plan-table td{border:none;border-bottom:1px solid var(--line);padding:10px 11px 10px 42%;position:relative;min-height:1.5em;line-height:1.6;}
    .plan-table td:last-child{border-bottom:none;}
    .plan-table td:before{content:attr(data-label);position:absolute;left:11px;top:10px;font-weight:600;color:var(--sea);font-size:12.5px;}
    .plan-table .links-row td{padding-left:11px;}
    .plan-table .links-row td:before{display:none;}
    .plan-table td.long-cell{padding-left:11px;padding-top:28px;}
    .plan-table td.long-cell:before{left:11px;top:8px;}
  }
'''

LABEL_TABLES_JS = '''  /* 自动给表格单元格加上列标题标签，用于手机端卡片显示 */
  function labelTables(){
    document.querySelectorAll('.plan-table').forEach(function(table){
      var headerRow=table.querySelector('tr');
      if(!headerRow) return;
      var headers=Array.prototype.slice.call(headerRow.querySelectorAll('th')).map(function(th){return th.textContent.trim();});
      if(!headers.length) return;
      var rows=table.querySelectorAll('tr');
      for(var i=0;i<rows.length;i++){
        var row=rows[i];
        if(row.querySelector('th')) continue;
        var cells=row.querySelectorAll('td');
        for(var j=0;j<cells.length;j++){
          if(headers[j]) cells[j].setAttribute('data-label', headers[j]);
          if(j===cells.length-1 && cells.length>2) cells[j].classList.add('long-cell');
        }
      }
    });
  }
'''

def patch(file_path: Path) -> str:
    text = file_path.read_text(encoding='utf-8')

    # 1. 改 edithelp（仅 cloud.html 有独立块）
    if EDIT_BAR_BLOCK_OLD in text:
        text = text.replace(EDIT_BAR_BLOCK_OLD, EDIT_BAR_BLOCK_NEW)

    # 2. 加 edithelp CSS
    if '.edithelp{' not in text:
        text = text.replace(
            '  #editbar{position:fixed;left:0;right:0;bottom:0;z-index:999;display:flex;gap:8px;align-items:center;\n    padding:9px 12px;background:rgba(18,28,46,.95);color:#fff;font-size:13px;\n    box-shadow:0 -3px 12px rgba(0,0,0,.3);}',
            '  #editbar{position:fixed;left:0;right:0;bottom:0;z-index:999;display:flex;gap:8px;align-items:center;\n    padding:9px 12px;background:rgba(18,28,46,.95);color:#fff;font-size:13px;\n    box-shadow:0 -3px 12px rgba(0,0,0,.3);}' + EDIT_HELP_CSS
        )

    # 3. 加手机端表格卡片 CSS
    if '手机端表格转卡片' not in text:
        text = text.replace(
            '  @media(max-width:680px){\n    #editbar{font-size:12px;padding:8px 9px;gap:6px;}',
            TABLE_CARD_CSS.strip() + '\n  @media(max-width:680px){\n    #editbar{font-size:12px;padding:8px 9px;gap:6px;}'
        )

    # 4. 加 labelTables JS
    # 先删掉之前错误插入的多余部分（如果有）
    text = re.sub(
        r'\s*else\s*\n\s*/\* 自动给表格单元格加上列标题标签[\s\S]*?labelTables\(\); init\(\);',
        '  else init();\n    labelTables();',
        text
    )
    if 'function labelTables' not in text:
        # 在 </script> 前插入函数定义
        text = text.replace(
            '  })();\n  </script>',
            '\n' + LABEL_TABLES_JS + '\n  })();\n  </script>'
        )
    if 'labelTables();' not in text:
        # 在 else init(); 后插入调用
        text = text.replace(
            '  else init();',
            '  else init();\n    labelTables();'
        )

    return text

for name in ['cloud.html', 'index.html']:
    p = BASE / name
    patched = patch(p)
    p.write_text(patched, encoding='utf-8')
    print(f'patched {p}')

print('done')
