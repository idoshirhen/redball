from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')
marker='RED-BALL-ADMIN-TABS-V1'
if marker in s:
    print('Admin tabs already applied')
    raise SystemExit(0)

old_css='.adminPage{max-width:1000px;margin:auto}.adminGrid{display:grid;grid-template-columns:320px 1fr;gap:16px;align-items:start}.adminSide{position:sticky;top:12px}.adminGamesList{min-width:0}.adminGame{background:#171717;border:1px solid #333;border-radius:12px;padding:12px;margin-bottom:10px}.adminGameTitle{font-weight:700;margin-bottom:5px}.oddsEdit{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:8px 0}.adminActions{display:flex;gap:7px;flex-wrap:wrap}.adminActions .ghost{padding:7px 10px}'
new_css='''/* RED-BALL-ADMIN-TABS-V1 */\n.adminPage{max-width:1000px;margin:auto}.adminTabs{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-bottom:14px;padding:6px;background:rgba(10,10,10,.9);border:1px solid #353535;border-radius:14px}.adminTabBtn{background:#171717;color:#aaa;border:1px solid #333;border-radius:10px;padding:11px 8px;font-weight:700;cursor:pointer}.adminTabBtn.active{color:#fff;border-color:#ff4de1;background:linear-gradient(180deg,rgba(255,77,225,.28),rgba(110,216,255,.13))}.adminTabPane{display:none}.adminTabPane.active{display:block}.adminFormGrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.adminFormGrid .full{grid-column:1/-1}.adminGame{background:#171717;border:1px solid #333;border-radius:12px;padding:12px;margin-bottom:10px}.adminGameTitle{font-weight:700;margin-bottom:5px}.oddsEdit{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:8px 0}.adminActions{display:flex;gap:7px;flex-wrap:wrap}.adminActions .ghost{padding:7px 10px}.adminBet{background:#151515;border:1px solid #333;border-radius:12px;padding:13px;margin-bottom:10px}.adminBetTop{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.adminBetMeta{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:10px}.adminBetMeta div{background:#0d0d0d;border:1px solid #292929;border-radius:8px;padding:8px;text-align:center}.adminBetMeta b{display:block;margin-top:3px}.adminBetPicks{margin-top:9px;font-size:12px;color:#bbb;line-height:1.6}'''
if old_css not in s:
    raise SystemExit('admin CSS marker not found')
s=s.replace(old_css,new_css,1)

old_media='.adminGrid{grid-template-columns:1fr}.adminSide{position:static}.oddsEdit{grid-template-columns:1fr 1fr 1fr}.myBetTop{align-items:center}'
new_media='.adminTabs{grid-template-columns:1fr 1fr}.adminFormGrid{grid-template-columns:1fr}.adminFormGrid .full{grid-column:auto}.adminBetMeta{grid-template-columns:1fr 1fr}.oddsEdit{grid-template-columns:1fr 1fr 1fr}.myBetTop{align-items:center}'
if old_media not in s:
    raise SystemExit('admin mobile CSS marker not found')
s=s.replace(old_media,new_media,1)

old_html='''<section id="adminPage" class="page"><div class="pageTitle"><h1>ניהול ההימורים</h1><p>ניהול מחזורים, משחקים ויחסים</p><button id="adminLogoutBtn" class="ghost danger" type="button" style="margin-top:12px">🔒 יציאה מאובטחת</button></div><div class="adminPage"><div class="adminGrid"><aside class="panel adminSide"><h3 style="margin-top:0">פתיחה / נעילת מחזורים</h3><div id="adminRounds"></div><h3>הוספת משחק</h3><input id="home" placeholder="קבוצת בית"><input id="away" placeholder="קבוצת חוץ" style="margin-top:7px"><input id="start" type="datetime-local" step="60" style="margin-top:7px"><select id="round" style="margin-top:7px"><option value="2">מחזור 2</option><option value="3">מחזור 3</option><option value="4">מחזור 4</option><option value="5">מחזור 5</option><option value="6">מחזור 6</option><option value="7">מחזור 7</option><option value="8">מחזור 8</option></select><div class="oddsEdit"><input id="oh" type="number" step="0.01" min="1.01" placeholder="יחס 1"><input id="od" type="number" step="0.01" min="1.01" placeholder="יחס X"><input id="oa" type="number" step="0.01" min="1.01" placeholder="יחס 2"></div><button class="primary" id="addGame">+ הוסף משחק</button><p id="adminMsg" class="small"></p></aside><div class="panel adminGamesList"><h2 style="margin-top:0">משחקים קיימים</h2><div id="adminGames"><div class="muted">טוען...</div></div></div></div></div></section>'''
new_html='''<section id="adminPage" class="page"><div class="pageTitle"><h1>ניהול ההימורים</h1><p>ניהול מחזורים, משחקים וטפסים</p><button id="adminLogoutBtn" class="ghost danger" type="button" style="margin-top:12px">🔒 יציאה מאובטחת</button></div><div class="adminPage"><div class="adminTabs"><button class="adminTabBtn active" type="button" data-admin-tab="rounds">פתיחה/נעילת מחזורים</button><button class="adminTabBtn" type="button" data-admin-tab="add">הוספת משחק</button><button class="adminTabBtn" type="button" data-admin-tab="games">משחקים קיימים</button><button class="adminTabBtn" type="button" data-admin-tab="bets">כל ההימורים</button></div><section id="adminTabRounds" class="adminTabPane active panel"><h2 style="margin-top:0">פתיחה / נעילת מחזורים</h2><div id="adminRounds"><div class="muted">טוען...</div></div></section><section id="adminTabAdd" class="adminTabPane panel"><h2 style="margin-top:0">הוספת משחק</h2><div class="adminFormGrid"><input id="home" placeholder="קבוצת בית"><input id="away" placeholder="קבוצת חוץ"><input id="start" type="datetime-local" step="60"><select id="round"><option value="2">מחזור 2</option><option value="3">מחזור 3</option><option value="4">מחזור 4</option><option value="5">מחזור 5</option><option value="6">מחזור 6</option><option value="7">מחזור 7</option><option value="8">מחזור 8</option></select><div class="oddsEdit full"><input id="oh" type="number" step="0.01" min="1.20" max="2.00" placeholder="יחס 1"><input id="od" type="number" step="0.01" min="1.20" max="2.00" placeholder="יחס X"><input id="oa" type="number" step="0.01" min="1.20" max="2.00" placeholder="יחס 2"></div><button class="primary full" id="addGame">+ הוסף משחק</button><p id="adminMsg" class="small full"></p></div></section><section id="adminTabGames" class="adminTabPane panel"><h2 style="margin-top:0">משחקים קיימים</h2><div id="adminGames"><div class="muted">טוען...</div></div></section><section id="adminTabBets" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">כל ההימורים</h2><button id="refreshAdminBets" class="ghost" type="button">🔄 רענן</button></div><div id="adminBets" style="margin-top:12px"><div class="muted">טוען...</div></div></section></div></section>'''
if old_html not in s:
    raise SystemExit('admin HTML block not found')
s=s.replace(old_html,new_html,1)

old_open='function openAdmin(){if(adminToken){showPage("admin");adminRounds();adminGames()}else{' 
new_open='function openAdmin(){if(adminToken){showPage("admin");showAdminTab("rounds")}else{'
if old_open not in s:
    raise SystemExit('openAdmin marker not found')
s=s.replace(old_open,new_open,1)

old_login='showPage("admin");await Promise.all([adminRounds(),adminGames()])'
new_login='showPage("admin");await showAdminTab("rounds")'
if old_login not in s:
    raise SystemExit('admin login marker not found')
s=s.replace(old_login,new_login,1)

insert_before='$("#addGame").onclick=async()=>'
admin_tabs_js='''async function showAdminTab(name){document.querySelectorAll(".adminTabBtn").forEach(b=>b.classList.toggle("active",b.dataset.adminTab===name));document.querySelectorAll(".adminTabPane").forEach(p=>p.classList.remove("active"));const pane=$("#adminTab"+name.charAt(0).toUpperCase()+name.slice(1));if(pane)pane.classList.add("active");if(name==="rounds")await adminRounds();if(name==="games")await adminGames();if(name==="bets")await adminAllBets()}document.querySelectorAll(".adminTabBtn").forEach(b=>b.onclick=()=>showAdminTab(b.dataset.adminTab));\nasync function adminAllBets(){const box=$("#adminBets");box.innerHTML='<div class="muted">טוען...</div>';try{const d=await adminReq("list_bets"),rows=d.bets||[];box.innerHTML=rows.length?rows.map(b=>{const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[];return '<article class="adminBet"><div class="adminBetTop"><div><b class="betCode">'+esc(b.bet_code)+'</b><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div><span class="betStatus '+st[1]+'">'+st[0]+'</span></div><div class="adminBetMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס<b>'+Number(b.total_odd||0).toFixed(2)+'</b></div><div>זכייה<b>'+money(b.potential_win)+'</b></div><div>נלקח ע״י<b>'+(b.paid_by?esc(b.paid_by):'-')+'</b></div></div><div class="adminBetPicks">'+picks.map(p=>esc((p.g||'')+' • '+(p.l||''))).join('<br>')+'</div></article>'}).join(''):'<div class="muted">אין הימורים במאגר</div>'}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}}\n$("#refreshAdminBets").onclick=adminAllBets;\n'''
if insert_before not in s:
    raise SystemExit('JS insertion marker not found')
s=s.replace(insert_before,admin_tabs_js+insert_before,1)

p.write_text(s,encoding='utf-8')
print('Betting admin tabs applied')
