from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

def function_end(src,start):
    brace=src.find('{',start)
    if brace<0: return -1
    depth=0;i=brace;quote=None;escape=False;line_comment=False;block_comment=False
    while i<len(src):
        c=src[i];n=src[i+1] if i+1<len(src) else ''
        if line_comment:
            if c=='\n': line_comment=False
            i+=1;continue
        if block_comment:
            if c=='*' and n=='/': block_comment=False;i+=2;continue
            i+=1;continue
        if quote:
            if escape: escape=False
            elif c=='\\': escape=True
            elif c==quote: quote=None
            i+=1;continue
        if c=='/' and n=='/': line_comment=True;i+=2;continue
        if c=='/' and n=='*': block_comment=True;i+=2;continue
        if c in ('\"',"'",'`'): quote=c;i+=1;continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return i+1
        i+=1
    return -1

css_anchor='.adminBetMeta{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:10px}'
css_add='''.gameResultRow{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:10px;padding-top:10px;border-top:1px solid #2d2d2d}.gameResultRow .resultLabel{font-size:12px;color:#aaa;margin-left:3px}.gameResultBtn{min-width:45px;padding:7px 12px!important;background:#191919!important;border:1px solid #444!important;color:#fff!important}.gameResultBtn.selected{background:#087a4f!important;border-color:#14b875!important;box-shadow:0 0 0 1px rgba(20,184,117,.25) inset}.gameResultClear{padding:7px 10px!important;font-size:12px}.pickOutcome{display:inline-flex;align-items:center;justify-content:center;width:25px;height:25px;border-radius:50%;margin-left:8px;font-size:15px;flex:0 0 25px}.pickOutcome.pending{background:rgba(255,177,67,.11);border:1px solid rgba(255,177,67,.28)}.pickOutcome.won{background:rgba(98,230,167,.11);border:1px solid rgba(98,230,167,.28)}.pickOutcome.lost{background:rgba(255,90,103,.11);border:1px solid rgba(255,90,103,.30)}.myPickWithOutcome{display:flex;align-items:center;justify-content:space-between;gap:10px}.myPickText{min-width:0;flex:1}'''
if 'gameResultRow{' not in s:
    if css_anchor not in s: raise SystemExit('CSS anchor missing')
    s=s.replace(css_anchor,css_add+css_anchor,1)

old_const='BETS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-bets",PUBLIC_URL='
new_const='BETS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-bets",RESULTS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-results",PUBLIC_URL='
if 'RESULTS_ADMIN_URL=' not in s:
    if old_const not in s: raise SystemExit('results URL anchor missing')
    s=s.replace(old_const,new_const,1)

if 'async function adminResultReq(' not in s:
    anchor='async function adminReq(action,payload={},auth=true)'
    idx=s.find(anchor)
    if idx<0: raise SystemExit('adminReq anchor missing')
    helper='''async function adminResultReq(action,payload={}){const h={"Content-Type":"application/json","apikey":KEY};if(adminToken)h["x-admin-token"]=adminToken;const res=await fetch(RESULTS_ADMIN_URL,{method:"POST",headers:h,body:JSON.stringify({action,...payload})});let d={};try{d=await res.json()}catch(e){}if(!res.ok){if(res.status===401){adminToken="";sessionStorage.removeItem("redball_betting_admin")}throw new Error(d.error||"שגיאה")}return d}\n'''
    s=s[:idx]+helper+s[idx:]

start=s.find('async function adminGames(){')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit(f'adminGames block parse failed start={start} end={end}')
new_admin_games=r'''async function adminGames(){const box=$("#adminGames");box.innerHTML='<div class="muted">טוען...</div>';try{const d=await adminReq("list_betting_games"),rows=d.games||[];box.innerHTML=rows.length?rows.map(g=>'<div class="adminGame" data-id="'+g.id+'"><div class="adminGameTitle">מחזור '+g.round_no+' • '+esc(g.home_team)+' - '+esc(g.away_team)+'</div><div class="small">'+(g.starts_at?fmtDate(g.starts_at):'ללא תאריך')+'</div><div class="oddsEdit"><input class="goH" type="number" min="1.20" max="2.00" step="0.01" value="'+Number(g.odd_home).toFixed(2)+'"><input class="goD" type="number" min="1.20" max="2.00" step="0.01" value="'+Number(g.odd_draw).toFixed(2)+'"><input class="goA" type="number" min="1.20" max="2.00" step="0.01" value="'+Number(g.odd_away).toFixed(2)+'"></div><div class="adminActions"><button class="ghost saveGameOdds" type="button">💾 שמור יחסים</button><button class="ghost danger deleteGame" type="button">🗑 מחק</button></div><div class="gameResultRow"><span class="resultLabel">תוצאת סיום:</span>'+['1','X','2'].map(r=>'<button class="ghost gameResultBtn '+(g.result===r?'selected':'')+'" type="button" data-result="'+r+'">'+r+'</button>').join('')+(g.result?'<button class="ghost gameResultClear" type="button">↩ בטל תוצאה</button>':'')+'</div></div>').join(''):'<div class="muted">אין משחקים קיימים.</div>';box.querySelectorAll('.adminGame').forEach(card=>{card.querySelector('.saveGameOdds').onclick=async()=>{const oh=+card.querySelector('.goH').value,od=+card.querySelector('.goD').value,oa=+card.querySelector('.goA').value;try{await adminReq("update_betting_game",{id:card.dataset.id,patch:{odd_home:oh,odd_draw:od,odd_away:oa}});siteToast("היחסים עודכנו")}catch(e){siteAlert("לא ניתן לעדכן: "+e.message,"שגיאה")}};card.querySelector('.deleteGame').onclick=async()=>{if(!await siteConfirm("למחוק את המשחק?"))return;try{await adminReq("delete_betting_game",{id:card.dataset.id});await adminGames();await load();siteToast("המשחק נמחק")}catch(e){siteAlert(e.message,"שגיאה")}};card.querySelectorAll('.gameResultBtn').forEach(btn=>btn.onclick=async()=>{if(!await siteConfirm('לסמן את תוצאת המשחק כ־'+btn.dataset.result+'?\nכל הטפסים יתעדכנו אוטומטית לפי התוצאה.','אישור תוצאת משחק'))return;try{await adminResultReq('set_game_result',{id:card.dataset.id,result:btn.dataset.result});siteToast('תוצאת המשחק נשמרה');await adminGames();if($("#adminTabBets").classList.contains("active"))await adminAllBets(false);if($("#minePage").classList.contains("activePage"))await loadMyBets()}catch(e){siteAlert('לא ניתן לשמור תוצאה: '+e.message,'שגיאה')}});const clear=card.querySelector('.gameResultClear');if(clear)clear.onclick=async()=>{if(!await siteConfirm('לבטל את תוצאת המשחק?\nהטפסים יחזרו לחישוב לפי שאר המשחקים.','ביטול תוצאה'))return;try{await adminResultReq('set_game_result',{id:card.dataset.id,result:null});siteToast('תוצאת המשחק בוטלה');await adminGames();if($("#adminTabBets").classList.contains("active"))await adminAllBets(false);if($("#minePage").classList.contains("activePage"))await loadMyBets()}catch(e){siteAlert('לא ניתן לבטל תוצאה: '+e.message,'שגיאה')}}})}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}}'''
s=s[:start]+new_admin_games+s[end:]

start=s.find('function renderMyBets(rows){')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit('renderMyBets parse failed')
new_my=r'''function pickOutcomeIcon(p){if(p.pick_status==='won')return '<span class="pickOutcome won" title="הימור נכון">✅</span>';if(p.pick_status==='lost')return '<span class="pickOutcome lost" title="הימור לא נכון">❌</span>';return '<span class="pickOutcome pending" title="ממתין לתוצאת משחק">⏳</span>'}
function renderMyBets(rows){const box=$("#myBets");if(!rows.length){box.innerHTML='<div style="text-align:center;padding:30px 10px"><div style="font-size:34px">🎫</div><h3>עדיין אין הימורים שמורים</h3><div class="muted">שלח הימור או חפש טיקט לפי הקוד שלו.</div></div>';return}box.innerHTML=rows.map(b=>{const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[];return '<article class="myBet"><div class="myBetTop"><div><div class="betCodeRow"><div class="betCode">'+esc(b.bet_code)+'</div><button class="copyCodeBtn" type="button" data-code="'+esc(b.bet_code)+'" onclick="copyBetCode(this)">📋 העתק קוד</button></div><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div><span class="betStatus '+st[1]+'">'+st[0]+'</span></div><div>'+picks.map(p=>'<div class="myPick myPickWithOutcome"><div class="myPickText"><b>'+esc(p.g||"")+'</b><br>'+esc(p.l||"")+' • יחס '+Number(p.o||0).toFixed(2)+'</div>'+pickOutcomeIcon(p)+'</div>').join("")+'</div><div class="betMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס כולל<b>'+Number(b.total_odd).toFixed(2)+'</b></div><div>זכייה אפשרית<b>'+money(b.potential_win)+'</b></div></div></article>'}).join("")}'''
s=s[:start]+new_my+s[end:]

for token in ['RESULTS_ADMIN_URL','set_game_result','pickOutcomeIcon','gameResultBtn','⏳','✅','❌']:
    if token not in s: raise SystemExit('missing '+token)

p.write_text(s,encoding='utf-8')
print('game results + automatic settlement UI applied v3')
