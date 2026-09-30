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
        if c in ('"',"'",'`'): quote=c;i+=1;continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    return -1

# Styles for grouped/collapsible sessions.
css_anchor='.adminGame{background:#171717;border:1px solid #333;border-radius:12px;padding:12px;margin-bottom:10px}'
if css_anchor not in s:
    raise SystemExit('adminGame CSS anchor missing')
css_extra='''.adminGamesToolbar{display:flex;justify-content:flex-end;gap:8px;flex-wrap:wrap;margin:0 0 12px}.adminSessionGroup{border:1px solid #343434;border-radius:13px;background:#101010;margin-bottom:12px;overflow:hidden}.adminSessionHead{width:100%;display:flex;align-items:center;justify-content:space-between;gap:12px;background:#171717;color:#fff;border:0;border-bottom:1px solid transparent;padding:13px 14px;cursor:pointer;text-align:right}.adminSessionGroup.open .adminSessionHead{border-bottom-color:#303030}.adminSessionHeadMain{display:flex;align-items:center;gap:10px;min-width:0}.adminSessionArrow{font-size:18px;transition:transform .18s;flex:0 0 auto}.adminSessionGroup.open .adminSessionArrow{transform:rotate(90deg)}.adminSessionName{font-weight:800;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.adminSessionMeta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}.adminSessionCount{font-size:12px;color:#aaa;border:1px solid #3a3a3a;border-radius:999px;padding:4px 8px}.adminSessionState{font-size:11px;font-weight:800;border-radius:999px;padding:4px 8px}.adminSessionState.openState{color:#62e6a7;background:rgba(98,230,167,.10);border:1px solid rgba(98,230,167,.25)}.adminSessionState.lockedState{color:#aaa;background:#111;border:1px solid #3b3b3b}.adminSessionBody{display:none;padding:12px}.adminSessionGroup.open .adminSessionBody{display:block}.adminSessionBody .adminGame:last-child{margin-bottom:0}@media(max-width:700px){.adminSessionHead{align-items:flex-start}.adminSessionMeta{max-width:45%}.adminGamesToolbar .ghost{flex:1}}'''
s=s.replace(css_anchor,css_extra+css_anchor,1)

# Replace adminGames only; preserve every existing game action.
start=s.find('async function adminGames(){')
end=function_end(s,start)
if start<0 or end<0:
    raise SystemExit('adminGames function not found')

new_func=r'''let adminGameOpenSessions=null;
function toggleAdminGameSession(roundNo){if(!(adminGameOpenSessions instanceof Set))adminGameOpenSessions=new Set();const key=Number(roundNo);if(adminGameOpenSessions.has(key))adminGameOpenSessions.delete(key);else adminGameOpenSessions.add(key);const group=document.querySelector('.adminSessionGroup[data-session="'+key+'"]');if(group)group.classList.toggle('open',adminGameOpenSessions.has(key))}
function setAllAdminGameSessions(open){document.querySelectorAll('.adminSessionGroup').forEach(group=>{const key=Number(group.dataset.session);if(!(adminGameOpenSessions instanceof Set))adminGameOpenSessions=new Set();if(open)adminGameOpenSessions.add(key);else adminGameOpenSessions.delete(key);group.classList.toggle('open',open)})}
async function adminGames(){const box=$("#adminGames");box.innerHTML='<div class="muted">טוען...</div>';try{const [d,sd]=await Promise.all([adminReq("list_betting_games"),adminSessionReq("list_sessions")]),rows=d.games||[],sessions=sd.sessions||[],sessionMap=new Map(sessions.map(r=>[Number(r.round_no),r]));if(!rows.length){box.innerHTML='<div class="muted">אין משחקים קיימים.</div>';return}const grouped=new Map();rows.forEach(g=>{const k=Number(g.round_no);if(!grouped.has(k))grouped.set(k,[]);grouped.get(k).push(g)});const sessionOrder=[...sessions.map(r=>Number(r.round_no)).filter(k=>grouped.has(k)),...[...grouped.keys()].filter(k=>!sessionMap.has(k))];if(!(adminGameOpenSessions instanceof Set)){const initiallyOpen=sessionOrder.filter(k=>{const r=sessionMap.get(k);return r&&r.is_open});adminGameOpenSessions=new Set(initiallyOpen.length?initiallyOpen:[sessionOrder[0]])}const gameHtml=g=>'<div class="adminGame" data-id="'+g.id+'"><div class="adminGameTitle">'+esc(g.home_team)+' - '+esc(g.away_team)+'</div><div class="small">'+(g.starts_at?fmtDate(g.starts_at):'ללא תאריך')+'</div><div class="oddsEdit"><input class="goH" type="number" min="1.20" max="2.00" step="0.01" value="'+Number(g.odd_home).toFixed(2)+'"><input class="goD" type="number" min="1.20" max="2.00" step="0.01" value="'+Number(g.odd_draw).toFixed(2)+'"><input class="goA" type="number" min="1.20" max="2.00" step="0.01" value="'+Number(g.odd_away).toFixed(2)+'"></div><div class="adminActions"><button class="ghost saveGameOdds" type="button">💾 שמור יחסים</button><button class="ghost danger deleteGame" type="button">🗑 מחק</button></div><div class="gameResultRow"><span class="resultLabel">תוצאת סיום:</span>'+['1','X','2'].map(r=>'<button class="ghost gameResultBtn '+(g.result===r?'selected':'')+'" type="button" data-result="'+r+'">'+r+'</button>').join('')+(g.result?'<button class="ghost gameResultClear" type="button">↩ בטל תוצאה</button>':'')+'</div></div>';box.innerHTML='<div class="adminGamesToolbar"><button class="ghost" id="openAllGameSessions" type="button">▾ פתח הכל</button><button class="ghost" id="closeAllGameSessions" type="button">▸ סגור הכל</button></div>'+sessionOrder.map(k=>{const r=sessionMap.get(k)||{round_no:k,name:'סשן '+k,is_open:false},list=grouped.get(k)||[],opened=adminGameOpenSessions.has(k);return '<section class="adminSessionGroup '+(opened?'open':'')+'" data-session="'+k+'"><button class="adminSessionHead" type="button" onclick="toggleAdminGameSession('+k+')"><span class="adminSessionHeadMain"><span class="adminSessionArrow">▶</span><span class="adminSessionName">'+esc(r.name||('סשן '+k))+'</span></span><span class="adminSessionMeta"><span class="adminSessionCount">'+list.length+' משחקים</span><span class="adminSessionState '+(r.is_open?'openState':'lockedState')+'">'+(r.is_open?'● פתוח':'🔒 נעול')+'</span></span></button><div class="adminSessionBody">'+list.map(gameHtml).join('')+'</div></section>'}).join('');$("#openAllGameSessions").onclick=()=>setAllAdminGameSessions(true);$("#closeAllGameSessions").onclick=()=>setAllAdminGameSessions(false);box.querySelectorAll('.adminGame').forEach(card=>{card.querySelector('.saveGameOdds').onclick=async()=>{const oh=+card.querySelector('.goH').value,od=+card.querySelector('.goD').value,oa=+card.querySelector('.goA').value;try{await adminReq("update_betting_game",{id:card.dataset.id,patch:{odd_home:oh,odd_draw:od,odd_away:oa}});siteToast("היחסים עודכנו")}catch(e){siteAlert("לא ניתן לעדכן: "+e.message,"שגיאה")}};card.querySelector('.deleteGame').onclick=async()=>{if(!await siteConfirm("למחוק את המשחק?"))return;try{await adminReq("delete_betting_game",{id:card.dataset.id});await adminGames();await load();siteToast("המשחק נמחק")}catch(e){siteAlert(e.message,"שגיאה")}};card.querySelectorAll('.gameResultBtn').forEach(btn=>btn.onclick=async()=>{if(!await siteConfirm('לסמן את תוצאת המשחק כ־'+btn.dataset.result+'?\nכל הטפסים יתעדכנו אוטומטית לפי התוצאה.','אישור תוצאת משחק'))return;try{await adminResultReq('set_game_result',{id:card.dataset.id,result:btn.dataset.result});siteToast('תוצאת המשחק נשמרה');card.querySelectorAll('.gameResultBtn').forEach(x=>x.classList.toggle('selected',x.dataset.result===btn.dataset.result));if(!card.querySelector('.gameResultClear')){const c=document.createElement('button');c.className='ghost gameResultClear';c.type='button';c.textContent='↩ בטל תוצאה';card.querySelector('.gameResultRow').appendChild(c);bindDynamicGameResultClear(card,c)}if($("#adminTabBets").classList.contains("active"))await adminAllBets(false);if($("#minePage").classList.contains("activePage"))await loadMyBets()}catch(e){siteAlert('לא ניתן לשמור תוצאה: '+e.message,'שגיאה')}});const clear=card.querySelector('.gameResultClear');if(clear)bindDynamicGameResultClear(card,clear)})}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}}'''

s=s[:start]+new_func+s[end:]

for token in ['adminSessionGroup','toggleAdminGameSession','openAllGameSessions','closeAllGameSessions','sessionOrder.map','bindDynamicGameResultClear(card,clear)']:
    if token not in s:
        raise SystemExit('missing expected token: '+token)

p.write_text(s,encoding='utf-8')
print('grouped admin games by session')
