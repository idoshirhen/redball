from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

def replace_func(name,new):
    global s
    markers=[f'async function {name}(',f'function {name}(']
    starts=[s.find(m) for m in markers]
    starts=[x for x in starts if x>=0]
    if not starts: raise SystemExit('missing function '+name)
    start=min(starts)
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

# CSS
css_anchor='.adminPrizeDone{display:inline-block;margin-top:12px;padding:9px 12px;border-radius:9px;background:rgba(50,200,120,.12);border:1px solid rgba(98,230,167,.3);color:#62e6a7;font-weight:800}'
if css_anchor not in s: raise SystemExit('missing css anchor')
css_add='''.adminPrizeDone{display:inline-block;margin-top:12px;padding:9px 12px;border-radius:9px;background:rgba(50,200,120,.12);border:1px solid rgba(98,230,167,.3);color:#62e6a7;font-weight:800}.adminBetStats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:14px 0}.adminStat{background:#0d0d0d;border:1px solid #303030;border-radius:11px;padding:11px;text-align:center}.adminStat span{display:block;color:#999;font-size:11px;margin-bottom:5px}.adminStat b{font-size:18px;color:#fff}.adminBetSearch{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;margin:12px 0}.adminBetSearch input{margin:0}.adminBetSummary{display:flex;justify-content:space-between;align-items:center;gap:10px;cursor:pointer}.adminBetSummaryMain{min-width:0;display:flex;align-items:center;gap:10px;flex-wrap:wrap}.adminBetSummaryMeta{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.adminBetDetails{display:none;margin-top:12px;padding-top:12px;border-top:1px solid #292929}.adminBet.expanded .adminBetDetails{display:block}.adminBetExpand{width:34px;height:34px;padding:0;flex:0 0 34px}.adminBet.expanded .adminBetExpand{transform:rotate(180deg)}.adminAttention{display:inline-flex;align-items:center;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:800;white-space:nowrap}.attentionPay{background:rgba(255,90,103,.12);border:1px solid rgba(255,90,103,.3);color:#ff7b86}.attentionWait{background:rgba(255,177,67,.12);border:1px solid rgba(255,177,67,.3);color:#ffb143}.attentionPrize{background:rgba(110,216,255,.13);border:1px solid rgba(110,216,255,.3);color:#6ed8ff}.attentionDone{background:rgba(98,230,167,.11);border:1px solid rgba(98,230,167,.28);color:#62e6a7}.adminBet.adminNeedsAction{border-color:#6a4c18}.adminBet.adminPrizeAction{border-color:#24515f}@media(max-width:800px){.adminBetStats{grid-template-columns:1fr 1fr}.adminBetSummary{align-items:flex-start}.adminBetSummaryMeta{justify-content:flex-start}.adminBetSearch{grid-template-columns:1fr}.adminBetSearch .ghost{width:100%}}'''
s=s.replace(css_anchor,css_add,1)

# Replace the whole All Bets pane, keeping archive unified here.
start=s.find('<section id="adminTabBets"')
if start<0: raise SystemExit('missing adminTabBets')
end=s.find('</section>',start)
if end<0: raise SystemExit('missing adminTabBets end')
end+=len('</section>')
new_pane='''<section id="adminTabBets" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">כל ההימורים</h2><button id="refreshAdminBets" class="ghost" type="button">🔄 רענן</button></div><div id="adminBetStats" class="adminBetStats"></div><div class="adminBetSearch"><input id="adminBetSearch" type="search" placeholder="חיפוש לפי קוד טיקט או שם שחקן" autocomplete="off"><button id="clearAdminBetSearch" class="ghost" type="button">נקה חיפוש</button></div><div id="betFilters" class="adminActions"><button class="ghost activeState" type="button" data-bet-filter="all">הכול (0)</button><button class="ghost" type="button" data-bet-filter="active">פעילים (0)</button><button class="ghost" type="button" data-bet-filter="won">זכו (0)</button><button class="ghost" type="button" data-bet-filter="lost">הפסידו (0)</button><button class="ghost" type="button" data-bet-filter="cancelled">בוטלו / נמחקו (0)</button></div><div id="adminBets" style="margin-top:12px"><div class="muted">טוען...</div></div></section>'''
s=s[:start]+new_pane+s[end:]

replace_func('renderAdminBet', '''function renderAdminBet(b){const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[],topAction=b.result_status==='cancelled'?'':('<button class="ghost danger" type="button" onclick="event.stopPropagation();adminBetAction(\\''+b.id+'\\',\\'cancelled\\')">🗑 מחק</button>'),attention=adminBetAttention(b),expanded=adminExpandedBets.has(b.id);return '<article class="adminBet '+(expanded?'expanded ':'')+attention.cardClass+'" data-bet-id="'+b.id+'"><div class="adminBetSummary" onclick="toggleAdminBetDetails(\\''+b.id+'\\')"><div class="adminBetSummaryMain"><button class="ghost adminBetExpand" type="button" onclick="event.stopPropagation();toggleAdminBetDetails(\\''+b.id+'\\')">⌄</button><div><div class="betCodeRow"><b class="betCode">'+esc(b.bet_code)+'</b><button class="copyCodeBtn" type="button" data-code="'+esc(b.bet_code)+'" onclick="event.stopPropagation();copyBetCode(this)">📋 העתק קוד</button></div><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div></div><div class="adminBetSummaryMeta"><span class="adminAttention '+attention.cls+'">'+attention.text+'</span><span class="small">'+money(b.stake)+'</span><span class="betStatus '+st[1]+'">'+st[0]+'</span>'+topAction+'</div></div><div class="adminBetDetails"><div class="adminBetMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס<b>'+Number(b.total_odd||0).toFixed(2)+'</b></div><div>זכייה<b>'+money(b.potential_win)+'</b></div><div>שולם ע״י<b>'+(b.paid_by?esc(b.paid_by):'-')+'</b></div></div><div class="adminBetPicks">'+picks.map(p=>'<div class="myPick myPickWithOutcome">'+pickOutcomeIcon(p)+'<div class="myPickText">'+esc((p.g||''))+'<br><span class="muted">'+esc((p.l||''))+' • יחס '+Number(p.o||0).toFixed(2)+'</span></div></div>').join('')+'</div><div class="adminBetControls">'+adminBetButtons(b)+'</div>'+(b.cancelled_at?'<div class="small" style="margin-top:7px">בוטל: '+fmtDate(b.cancelled_at)+'</div>':'')+(b.prize_paid_at?'<div class="small" style="margin-top:7px">מסירת פרס: '+fmtDate(b.prize_paid_at)+(b.prize_paid_by?' • '+esc(b.prize_paid_by):'')+'</div>':'')+'</div></article>'}''')

# Replace list-management block.
block_start=s.find('let adminBetRows=[]')
block_end=s.find('$("#addGame").onclick=',block_start)
if block_start<0 or block_end<0: raise SystemExit('missing admin bet list block')
new_block='''let adminBetRows=[],adminBetFilter="all",adminBetSearchQuery="",adminExpandedBets=new Set();
function adminBetCategory(b){if(b.result_status==="cancelled")return"cancelled";if(b.result_status==="won")return"won";if(b.result_status==="lost")return"lost";return"active"}
function adminBetAttention(b){if(b.result_status==='cancelled')return{text:'🗑 בוטל',cls:'attentionDone',cardClass:''};if(b.payment_status!=='paid')return{text:'🔴 ממתין לתשלום',cls:'attentionPay',cardClass:'adminNeedsAction'};if(b.result_status==='won'&&!b.prize_paid)return{text:'💰 פרס ממתין',cls:'attentionPrize',cardClass:'adminPrizeAction'};if(b.result_status==='pending')return{text:'🟡 ממתין לתוצאות',cls:'attentionWait',cardClass:'adminNeedsAction'};return{text:'🟢 הסתיים',cls:'attentionDone',cardClass:''}}
function toggleAdminBetDetails(id){if(adminExpandedBets.has(id))adminExpandedBets.delete(id);else adminExpandedBets.add(id);const card=document.querySelector('.adminBet[data-bet-id="'+id+'"]');if(card)card.classList.toggle('expanded',adminExpandedBets.has(id))}
function updateAdminBetStats(){const rows=adminBetRows,counts={all:rows.length,active:0,won:0,lost:0,cancelled:0},today=new Date();today.setHours(0,0,0,0);let todayStake=0,potential=0,pendingPay=0;rows.forEach(b=>{counts[adminBetCategory(b)]++;if(b.result_status!=='cancelled'&&new Date(b.created_at)>=today)todayStake+=Number(b.stake||0);if(b.result_status!=='cancelled')potential+=Number(b.potential_win||0);if(b.result_status!=='cancelled'&&b.payment_status!=='paid')pendingPay++});const stats=$("#adminBetStats");if(stats)stats.innerHTML='<div class="adminStat"><span>פעילים</span><b>'+counts.active+'</b></div><div class="adminStat"><span>ממתינים לתשלום</span><b>'+pendingPay+'</b></div><div class="adminStat"><span>זכו</span><b>'+counts.won+'</b></div><div class="adminStat"><span>הפסידו</span><b>'+counts.lost+'</b></div><div class="adminStat"><span>סכומי הימור היום</span><b>'+money(todayStake)+'</b></div><div class="adminStat"><span>זכיות פוטנציאליות</span><b>'+money(potential)+'</b></div>';const labels={all:'הכול',active:'פעילים',won:'זכו',lost:'הפסידו',cancelled:'בוטלו / נמחקו'};document.querySelectorAll('[data-bet-filter]').forEach(btn=>{const f=btn.dataset.betFilter;btn.textContent=labels[f]+' ('+(counts[f]||0)+')';btn.classList.toggle('activeState',f===adminBetFilter)})}
function renderAdminBetList(){const box=$("#adminBets"),q=adminBetSearchQuery.trim().toLowerCase();let rows=adminBetFilter==="all"?adminBetRows:adminBetRows.filter(b=>adminBetCategory(b)===adminBetFilter);if(q)rows=rows.filter(b=>String(b.bet_code||'').toLowerCase().includes(q)||String(b.player_name||'').toLowerCase().includes(q));box.innerHTML=rows.length?rows.map(renderAdminBet).join(''):'<div class="muted">לא נמצאו טפסים מתאימים.</div>';updateAdminBetStats()}
async function adminAllBets(showLoading=true){const box=$("#adminBets"),btn=$("#refreshAdminBets");const old=btn?btn.textContent:'';if(showLoading)box.innerHTML='<div class="muted">טוען...</div>';if(btn){btn.disabled=true;btn.textContent='מרענן...'}try{const d=await adminReq("list_bets");adminBetRows=d.bets||[];renderAdminBetList()}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}finally{if(btn){btn.disabled=false;btn.textContent=old||'🔄 רענן'}}}
$("#refreshAdminBets").onclick=()=>adminAllBets(false);document.querySelectorAll("[data-bet-filter]").forEach(b=>b.onclick=()=>{adminBetFilter=b.dataset.betFilter;renderAdminBetList()});$("#adminBetSearch").oninput=e=>{adminBetSearchQuery=e.target.value||'';renderAdminBetList()};$("#clearAdminBetSearch").onclick=()=>{$("#adminBetSearch").value='';adminBetSearchQuery='';renderAdminBetList()};
'''
s=s[:block_start]+new_block+s[block_end:]

p.write_text(s,encoding='utf-8')
print('patched betting.html')
