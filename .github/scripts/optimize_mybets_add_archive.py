from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

# 1) Admin tabs: add archive and make desktop grid 5 columns.
s=s.replace('.adminPage{max-width:1000px;margin:auto}.adminTabs{display:grid;grid-template-columns:repeat(4,1fr);',
            '.adminPage{max-width:1000px;margin:auto}.adminTabs{display:grid;grid-template-columns:repeat(5,1fr);',1)

old_tabs='''<button class="adminTabBtn" type="button" data-admin-tab="games">משחקים קיימים</button><button class="adminTabBtn" type="button" data-admin-tab="bets">כל ההימורים</button></div>'''
new_tabs='''<button class="adminTabBtn" type="button" data-admin-tab="games">משחקים קיימים</button><button class="adminTabBtn" type="button" data-admin-tab="bets">כל ההימורים</button><button class="adminTabBtn" type="button" data-admin-tab="archive">📦 ארכיון</button></div>'''
if old_tabs not in s: raise SystemExit('admin tabs anchor not found')
s=s.replace(old_tabs,new_tabs,1)

old_bets='''<section id="adminTabBets" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">כל ההימורים</h2><button id="refreshAdminBets" class="ghost" type="button">🔄 רענן</button></div><div id="adminBets" style="margin-top:12px"><div class="muted">טוען...</div></div></section>'''
new_bets=old_bets+'''<section id="adminTabArchive" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">📦 ארכיון טפסים</h2><button id="refreshArchive" class="ghost" type="button">🔄 רענן</button></div><div id="archiveFilters" class="adminActions" style="margin-top:12px"><button class="ghost activeState" type="button" data-archive-filter="all">הכול</button><button class="ghost" type="button" data-archive-filter="active">פעילים</button><button class="ghost" type="button" data-archive-filter="won">זכו</button><button class="ghost" type="button" data-archive-filter="lost">הפסידו</button><button class="ghost" type="button" data-archive-filter="cancelled">בוטלו / נמחקו</button></div><div id="archiveBets" style="margin-top:12px"><div class="muted">טוען...</div></div></section>'''
if old_bets not in s: raise SystemExit('bets section anchor not found')
s=s.replace(old_bets,new_bets,1)

# 2) Cancelled status has an explicit visual status.
old_status='''function betStatus(b){if(b.result_status==="won")return["🏆 זכה","stWon"];if(b.result_status==="lost")return["❌ הפסיד","stLost"];if(b.payment_status==="paid")return["🟢 פעיל","stActive"];return["🟠 ממתין לתשלום","stPending"]}'''
new_status='''function betStatus(b){if(b.result_status==="cancelled")return["🗑 בוטל / נמחק","stLost"];if(b.result_status==="won")return["🏆 זכה","stWon"];if(b.result_status==="lost")return["❌ הפסיד","stLost"];if(b.payment_status==="paid")return["🟢 פעיל","stActive"];return["🟠 ממתין לתשלום","stPending"]}'''
if old_status not in s: raise SystemExit('betStatus anchor not found')
s=s.replace(old_status,new_status,1)

# 3) My Bets: render own rows immediately, filter cancelled everywhere, then load imported codes in parallel.
old_load='''async function loadMyBets(){const box=$("#myBets");box.innerHTML='<div class="muted">טוען את ההימורים שלך...</div>';const {data,error}=await db.from("bets").select("id,bet_code,created_at,player_name,stake,total_odd,potential_win,picks,payment_status,result_status,paid_at,paid_by").order("created_at",{ascending:false}).limit(100);if(error){box.innerHTML='<div class="statusMsg error">לא ניתן לטעון את ההימורים: '+esc(error.message)+'</div>';return}const byId=new Map((data||[]).map(b=>[b.id,b]));for(const code of getSavedTicketCodes()){try{const b=await fetchImportedBet(code);if(b)byId.set(b.id,b)}catch(e){}}const rows=[...byId.values()].sort((a,b)=>new Date(b.created_at)-new Date(a.created_at));renderMyBets(rows)}'''
new_load='''async function loadMyBets(){const box=$("#myBets");box.innerHTML='<div class="muted">טוען את ההימורים שלך...</div>';const {data,error}=await db.from("bets").select("id,bet_code,created_at,player_name,stake,total_odd,potential_win,picks,payment_status,result_status,paid_at,paid_by").neq("result_status","cancelled").order("created_at",{ascending:false}).limit(100);if(error){box.innerHTML='<div class="statusMsg error">לא ניתן לטעון את ההימורים: '+esc(error.message)+'</div>';return}const byId=new Map((data||[]).filter(b=>b.result_status!=="cancelled").map(b=>[b.id,b]));const renderNow=()=>renderMyBets([...byId.values()].filter(b=>b.result_status!=="cancelled").sort((a,b)=>new Date(b.created_at)-new Date(a.created_at)));renderNow();const existingCodes=new Set([...byId.values()].map(b=>String(b.bet_code||'').toUpperCase()));const savedCodes=getSavedTicketCodes(),missingCodes=savedCodes.filter(code=>!existingCodes.has(String(code).toUpperCase()));if(!missingCodes.length)return;const results=await Promise.allSettled(missingCodes.map(code=>fetchImportedBet(code)));let changed=false;const hiddenCodes=new Set();results.forEach((r,i)=>{if(r.status!=="fulfilled"||!r.value)return;const b=r.value;if(b.result_status==="cancelled"){hiddenCodes.add(missingCodes[i]);return}byId.set(b.id,b);changed=true});if(hiddenCodes.size)localStorage.setItem("redball_saved_ticket_codes",JSON.stringify(savedCodes.filter(code=>!hiddenCodes.has(code))));if(changed)renderNow()}'''
if old_load not in s: raise SystemExit('loadMyBets anchor not found')
s=s.replace(old_load,new_load,1)

# Searching a cancelled ticket should not re-add it to My Bets.
old_search='''if(!bet){msg.textContent="לא נמצא טיקט עם הקוד הזה.";msg.className="statusMsg error searchMsg";return}saveTicketCode(bet.bet_code);'''
new_search='''if(!bet||bet.result_status==="cancelled"){msg.textContent="הטיקט בוטל / נמחק ואינו מוצג בהימורים שלי.";msg.className="statusMsg error searchMsg";return}saveTicketCode(bet.bet_code);'''
if old_search not in s: raise SystemExit('search ticket anchor not found')
s=s.replace(old_search,new_search,1)

# 4) Archive loader and filters.
old_show='''async function showAdminTab(name){document.querySelectorAll(".adminTabBtn").forEach(b=>b.classList.toggle("active",b.dataset.adminTab===name));document.querySelectorAll(".adminTabPane").forEach(p=>p.classList.remove("active"));const pane=$("#adminTab"+name.charAt(0).toUpperCase()+name.slice(1));if(pane)pane.classList.add("active");if(name==="rounds")await adminRounds();if(name==="games")await adminGames();if(name==="bets")await adminAllBets()}'''
new_show='''async function showAdminTab(name){document.querySelectorAll(".adminTabBtn").forEach(b=>b.classList.toggle("active",b.dataset.adminTab===name));document.querySelectorAll(".adminTabPane").forEach(p=>p.classList.remove("active"));const pane=$("#adminTab"+name.charAt(0).toUpperCase()+name.slice(1));if(pane)pane.classList.add("active");if(name==="rounds")await adminRounds();if(name==="games")await adminGames();if(name==="bets")await adminAllBets();if(name==="archive")await adminArchive()}'''
if old_show not in s: raise SystemExit('showAdminTab anchor not found')
s=s.replace(old_show,new_show,1)

anchor='''$("#refreshAdminBets").onclick=()=>adminAllBets(false);'''
archive_js='''$("#refreshAdminBets").onclick=()=>adminAllBets(false);let archiveRows=[],archiveFilter="all";function archiveCategory(b){if(b.result_status==="cancelled")return"cancelled";if(b.result_status==="won")return"won";if(b.result_status==="lost")return"lost";return"active"}function renderArchiveBet(b){const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[];return '<article class="adminBet"><div class="adminBetTop"><div><b class="betCode">'+esc(b.bet_code)+'</b><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div><span class="betStatus '+st[1]+'">'+st[0]+'</span></div><div class="adminBetMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס<b>'+Number(b.total_odd||0).toFixed(2)+'</b></div><div>זכייה<b>'+money(b.potential_win)+'</b></div><div>שולם ע״י<b>'+(b.paid_by?esc(b.paid_by):'-')+'</b></div></div><div class="adminBetPicks">'+picks.map(p=>esc((p.g||'')+' • '+(p.l||''))).join('<br>')+'</div>'+(b.prize_paid_at?'<div class="small" style="margin-top:9px">מסירת פרס: '+fmtDate(b.prize_paid_at)+(b.prize_paid_by?' • '+esc(b.prize_paid_by):'')+'</div>':'')+'</article>'}function renderArchive(){const box=$("#archiveBets"),rows=archiveFilter==="all"?archiveRows:archiveRows.filter(b=>archiveCategory(b)===archiveFilter);box.innerHTML=rows.length?rows.map(renderArchiveBet).join(''):'<div class="muted">אין טפסים בקטגוריה הזאת.</div>';document.querySelectorAll("[data-archive-filter]").forEach(b=>b.classList.toggle("activeState",b.dataset.archiveFilter===archiveFilter))}async function adminArchive(showLoading=true){const box=$("#archiveBets"),btn=$("#refreshArchive");const old=btn?btn.textContent:'';if(showLoading)box.innerHTML='<div class="muted">טוען...</div>';if(btn){btn.disabled=true;btn.textContent='מרענן...'}try{const d=await adminReq("list_bets");archiveRows=d.bets||[];renderArchive()}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}finally{if(btn){btn.disabled=false;btn.textContent=old||'🔄 רענן'}}}document.querySelectorAll("[data-archive-filter]").forEach(b=>b.onclick=()=>{archiveFilter=b.dataset.archiveFilter;renderArchive()});$("#refreshArchive").onclick=()=>adminArchive(false);'''
if anchor not in s: raise SystemExit('refreshAdminBets anchor not found')
s=s.replace(anchor,archive_js,1)

# After a status change, keep archive synchronized when it is currently open.
old_tail=''';if($("#minePage").classList.contains("activePage"))loadMyBets()}catch(e){'''
new_tail=''';if($("#minePage").classList.contains("activePage"))loadMyBets();if($("#adminTabArchive").classList.contains("active"))await adminArchive(false)}catch(e){'''
if old_tail not in s: raise SystemExit('adminBetAction tail anchor not found')
s=s.replace(old_tail,new_tail,1)

p.write_text(s,encoding='utf-8')
print('patched betting.html')
