from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

def need(old, label):
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')

def replace_once(old,new,label):
    global s
    need(old,label)
    s=s.replace(old,new,1)

def replace_func(name,new):
    global s
    marker='async function '+name+'('
    start=s.find(marker)
    if start<0:
        marker='function '+name+'('
        start=s.find(marker)
    if start<0: raise SystemExit('missing function '+name)
    brace=s.find('{',start)
    if brace<0: raise SystemExit('missing brace '+name)
    depth=0; quote=None; esc=False; i=brace
    while i<len(s):
        c=s[i]
        if quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
        else:
            if c in ('\"',"'",'`'): quote=c
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    s=s[:start]+new+s[i+1:]
                    return
        i+=1
    raise SystemExit('unclosed function '+name)

replace_once('.adminTabs{display:grid;grid-template-columns:repeat(5,1fr);', '.adminTabs{display:grid;grid-template-columns:repeat(4,1fr);', 'admin tabs columns')
replace_once('<button class="adminTabBtn" type="button" data-admin-tab="archive">📦 ארכיון</button>', '', 'archive tab')

old_bets='<section id="adminTabBets" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">כל ההימורים</h2><button id="refreshAdminBets" class="ghost" type="button">🔄 רענן</button></div><div id="adminBets" style="margin-top:12px"><div class="muted">טוען...</div></div></section><section id="adminTabArchive" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">📦 ארכיון טפסים</h2><button id="refreshArchive" class="ghost" type="button">🔄 רענן</button></div><div id="archiveFilters" class="adminActions" style="margin-top:12px"><button class="ghost activeState" type="button" data-archive-filter="all">הכול</button><button class="ghost" type="button" data-archive-filter="active">פעילים</button><button class="ghost" type="button" data-archive-filter="won">זכו</button><button class="ghost" type="button" data-archive-filter="lost">הפסידו</button><button class="ghost" type="button" data-archive-filter="cancelled">בוטלו / נמחקו</button></div><div id="archiveBets" style="margin-top:12px"><div class="muted">טוען...</div></div></section>'
new_bets='<section id="adminTabBets" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">כל ההימורים</h2><button id="refreshAdminBets" class="ghost" type="button">🔄 רענן</button></div><div id="betFilters" class="adminActions" style="margin-top:12px"><button class="ghost activeState" type="button" data-bet-filter="all">הכול</button><button class="ghost" type="button" data-bet-filter="active">פעילים</button><button class="ghost" type="button" data-bet-filter="won">זכו</button><button class="ghost" type="button" data-bet-filter="lost">הפסידו</button><button class="ghost" type="button" data-bet-filter="cancelled">בוטלו / נמחקו</button></div><div id="adminBets" style="margin-top:12px"><div class="muted">טוען...</div></div></section>'
replace_once(old_bets,new_bets,'bets/archive html')

replace_once('<p id="ticketSearchMsg" class="statusMsg searchMsg"></p></div><div id="myBets"', '<p id="ticketSearchMsg" class="statusMsg searchMsg"></p></div><div id="ticketSearchResult"></div><div id="myBets"', 'search result container')

replace_func('renderMyBets', '''function myBetCard(b){const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[];return '<article class="myBet"><div class="myBetTop"><div><div class="betCodeRow"><div class="betCode">'+esc(b.bet_code)+'</div><button class="copyCodeBtn" type="button" data-code="'+esc(b.bet_code)+'" onclick="copyBetCode(this)">📋 העתק קוד</button></div><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div><span class="betStatus '+st[1]+'">'+st[0]+'</span></div><div>'+picks.map(p=>'<div class="myPick myPickWithOutcome">'+pickOutcomeIcon(p)+'<div class="myPickText"><b>'+esc(p.g||"")+'</b><br>'+esc(p.l||"")+' • יחס '+Number(p.o||0).toFixed(2)+'</div></div>').join("")+'</div><div class="betMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס כולל<b>'+Number(b.total_odd).toFixed(2)+'</b></div><div>זכייה אפשרית<b>'+money(b.potential_win)+'</b></div></div></article>'}
function renderMyBets(rows){const box=$("#myBets");if(!rows.length){box.innerHTML='<div style="text-align:center;padding:30px 10px"><div style="font-size:34px">🎫</div><h3>עדיין אין הימורים שמורים</h3><div class="muted">שלח הימור או חפש טיקט לפי הקוד שלו.</div></div>';return}box.innerHTML=rows.map(myBetCard).join("")}''')

replace_func('searchTicket', '''async function searchTicket(){const input=$("#ticketSearchInput"),msg=$("#ticketSearchMsg"),btn=$("#ticketSearchBtn"),resultBox=$("#ticketSearchResult"),code=(input.value||"").trim().toUpperCase();msg.textContent="";msg.className="statusMsg searchMsg";resultBox.innerHTML="";if(!code){msg.textContent="הכנס קוד טיקט לחיפוש.";msg.className="statusMsg error searchMsg";return}btn.disabled=true;btn.textContent="מחפש...";try{const bet=await fetchImportedBet(code);if(!bet){msg.textContent="לא נמצא טיקט עם הקוד הזה במאגר.";msg.className="statusMsg error searchMsg";return}input.value=bet.bet_code;msg.textContent="✅ הטיקט נמצא במאגר.";msg.className="statusMsg success searchMsg";resultBox.innerHTML='<div class="small" style="margin:10px 2px 0;color:#6ed8ff;font-weight:700">תוצאת חיפוש</div>'+myBetCard(bet);if(bet.result_status!=="cancelled")saveTicketCode(bet.bet_code)}catch(e){msg.textContent=e.message||"לא ניתן לבצע את החיפוש כרגע.";msg.className="statusMsg error searchMsg"}finally{btn.disabled=false;btn.textContent="🔎 חפש"}}''')

replace_once('$("#ticketSearchClear").onclick=()=>{$("#ticketSearchInput").value="";$("#ticketSearchMsg").textContent="";$("#ticketSearchMsg").className="statusMsg searchMsg"}', '$("#ticketSearchClear").onclick=()=>{$("#ticketSearchInput").value="";$("#ticketSearchMsg").textContent="";$("#ticketSearchMsg").className="statusMsg searchMsg";$("#ticketSearchResult").innerHTML=""}', 'clear search result')

replace_func('showAdminTab', '''async function showAdminTab(name){document.querySelectorAll(".adminTabBtn").forEach(b=>b.classList.toggle("active",b.dataset.adminTab===name));document.querySelectorAll(".adminTabPane").forEach(p=>p.classList.remove("active"));const pane=$("#adminTab"+name.charAt(0).toUpperCase()+name.slice(1));if(pane)pane.classList.add("active");if(name==="rounds")await adminRounds();if(name==="games")await adminGames();if(name==="bets")await adminAllBets()}''')

replace_func('adminBetButtons', '''function adminBetButtons(b){let out=[];if(b.result_status==='cancelled')return '<button class="ghost activeState" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'restore\\')">↩ החזר טופס</button>';if(b.payment_status==='paid'){out.push('<button class="ghost adminActionPaid" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'unpaid\\')">↩ בטל תשלום</button>');const wonClass=b.result_status==='won'?' adminResultWon':'';const lostClass=b.result_status==='lost'?' adminResultLost':'';out.push('<button class="ghost adminResultBtn'+wonClass+'" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'won\\')">🏆 זכה</button>');out.push('<button class="ghost adminResultBtn'+lostClass+'" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'lost\\')">❌ הפסיד</button>');if(b.result_status!=='pending')out.push('<button class="ghost" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'result_pending\\')">↩ בטל תוצאה</button>');if(b.result_status==='won'){if(b.prize_paid){out.push('<button class="ghost adminActionPrize activeState" type="button" disabled>✅ הלקוח קיבל את הכסף</button>');out.push('<button class="ghost" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'prize_unpaid\\')">↩ בטל מסירת פרס</button>')}else out.push('<button class="ghost adminActionPrize" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'prize_paid\\')">✅ הלקוח קיבל את הכסף</button>')}}else{out.push('<button class="ghost adminActionPaid" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'paid\\')">💵 סמן כשולם</button>')}return out.join('')}''')

replace_func('renderAdminBet', '''function renderAdminBet(b){const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[],topAction=b.result_status==='cancelled'?'':('<button class="ghost danger" type="button" onclick="adminBetAction(\\''+b.id+'\\',\\'cancelled\\')">🗑 מחק</button>');return '<article class="adminBet" data-bet-id="'+b.id+'"><div class="adminBetTop"><div><b class="betCode">'+esc(b.bet_code)+'</b><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div><div class="adminBetStatusActions"><span class="betStatus '+st[1]+'">'+st[0]+'</span>'+topAction+'</div></div><div class="adminBetMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס<b>'+Number(b.total_odd||0).toFixed(2)+'</b></div><div>זכייה<b>'+money(b.potential_win)+'</b></div><div>שולם ע״י<b>'+(b.paid_by?esc(b.paid_by):'-')+'</b></div></div><div class="adminBetPicks">'+picks.map(p=>esc((p.g||'')+' • '+(p.l||''))).join('<br>')+'</div><div class="adminBetControls">'+adminBetButtons(b)+'</div>'+(b.cancelled_at?'<div class="small" style="margin-top:7px">בוטל: '+fmtDate(b.cancelled_at)+'</div>':'')+(b.prize_paid_at?'<div class="small" style="margin-top:7px">מסירת פרס: '+fmtDate(b.prize_paid_at)+(b.prize_paid_by?' • '+esc(b.prize_paid_by):'')+'</div>':'')+'</article>'}''')

replace_func('adminBetAction', '''async function adminBetAction(id,status){const labels={paid:'לסמן את הטיקט כשולם?',unpaid:'לבטל את סימון התשלום? פעולה זו גם תחזיר את התוצאה למצב ממתין.',won:'לסמן את הטיקט כזוכה?',lost:'לסמן את הטיקט כמפסיד?',result_pending:'לבטל את התוצאה ולהחזיר למצב ממתין?',prize_paid:'לאשר שהלקוח קיבל את כספי הזכייה?',prize_unpaid:'לבטל את סימון מסירת הפרס?',cancelled:'להעביר את הטיקט לבוטלו / נמחקו?',restore:'להחזיר את הטיקט מהביטול לסטטוס שהיה לו קודם?'};if(!await siteConfirm(labels[status]||'לאשר פעולה?'))return;try{await adminBetReq("update_bet_status",{id,status});siteToast(status==='restore'?'הטיקט הוחזר בהצלחה':status==='cancelled'?'הטיקט הועבר לבוטלו / נמחקו':'הטיקט עודכן בהצלחה');await adminAllBets(false);if($("#minePage").classList.contains("activePage"))loadMyBets()}catch(e){await siteAlert("לא ניתן לעדכן את הטיקט: "+e.message,'שגיאה')}}''')

start=s.find('async function adminAllBets(')
end=s.find('$("#addGame").onclick=',start)
if start<0 or end<0: raise SystemExit('missing admin bets block')
new_admin='''let adminBetRows=[],adminBetFilter="all";function adminBetCategory(b){if(b.result_status==="cancelled")return"cancelled";if(b.result_status==="won")return"won";if(b.result_status==="lost")return"lost";return"active"}function renderAdminBetList(){const box=$("#adminBets"),rows=adminBetFilter==="all"?adminBetRows:adminBetRows.filter(b=>adminBetCategory(b)===adminBetFilter);box.innerHTML=rows.length?rows.map(renderAdminBet).join(''):'<div class="muted">אין טפסים בקטגוריה הזאת.</div>';document.querySelectorAll("[data-bet-filter]").forEach(b=>b.classList.toggle("activeState",b.dataset.betFilter===adminBetFilter))}async function adminAllBets(showLoading=true){const box=$("#adminBets"),btn=$("#refreshAdminBets");const old=btn?btn.textContent:'';if(showLoading)box.innerHTML='<div class="muted">טוען...</div>';if(btn){btn.disabled=true;btn.textContent='מרענן...'}try{const d=await adminReq("list_bets");adminBetRows=d.bets||[];renderAdminBetList()}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}finally{if(btn){btn.disabled=false;btn.textContent=old||'🔄 רענן'}}}$("#refreshAdminBets").onclick=()=>adminAllBets(false);document.querySelectorAll("[data-bet-filter]").forEach(b=>b.onclick=()=>{adminBetFilter=b.dataset.betFilter;renderAdminBetList()});
'''
s=s[:start]+new_admin+s[end:]

p.write_text(s,encoding='utf-8')
print('patched betting.html')
