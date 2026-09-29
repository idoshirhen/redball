from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

# Text/UI terminology
s=s.replace('ניהול מחזורים, משחקים וטפסים','ניהול סשנים, משחקים וטפסים')
s=s.replace('data-admin-tab="rounds">פתיחה/נעילת מחזורים</button>','data-admin-tab="rounds">ניהול סשנים</button>')
s=s.replace('<section id="adminTabRounds" class="adminTabPane active panel"><h2 style="margin-top:0">פתיחה / נעילת מחזורים</h2><div id="adminRounds"><div class="muted">טוען...</div></div></section>', '<section id="adminTabRounds" class="adminTabPane active panel"><h2 style="margin-top:0">ניהול סשנים</h2><div class="adminFormGrid" style="margin-bottom:14px"><input id="newSessionName" class="full" placeholder="שם הסשן, לדוגמה: חצי גמר ליגת האלופות"><button id="createSession" class="primary full" type="button">+ סשן חדש</button><p id="sessionMsg" class="small full"></p></div><div id="adminRounds"><div class="muted">טוען...</div></div></section>')

old_select='<select id="round"><option value="2">מחזור 2</option><option value="3">מחזור 3</option><option value="4">מחזור 4</option><option value="5">מחזור 5</option><option value="6">מחזור 6</option><option value="7">מחזור 7</option><option value="8">מחזור 8</option></select>'
new_select='<select id="round"><option value="">בחר סשן</option></select>'
if old_select not in s:
    raise SystemExit('round select anchor missing')
s=s.replace(old_select,new_select,1)

# New server endpoint
old='BETS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-bets",RESULTS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-results",PUBLIC_URL='
new='BETS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-bets",RESULTS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-results",SESSIONS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-sessions",PUBLIC_URL='
if old not in s:
    raise SystemExit('endpoint anchor missing')
s=s.replace(old,new,1)

# Session request helper
anchor='async function adminReq(action,payload={},auth=true)'
idx=s.find(anchor)
if idx<0:
    raise SystemExit('adminReq anchor missing')
if 'async function adminSessionReq(' not in s:
    helper='async function adminSessionReq(action,payload={}){const h={"Content-Type":"application/json","apikey":KEY};if(adminToken)h["x-admin-token"]=adminToken;const res=await fetch(SESSIONS_ADMIN_URL,{method:"POST",headers:h,body:JSON.stringify({action,...payload})});let d={};try{d=await res.json()}catch(e){}if(!res.ok){if(res.status===401){adminToken="";sessionStorage.removeItem("redball_betting_admin")}throw new Error(d.error||"שגיאה")}return d}\n'
    s=s[:idx]+helper+s[idx:]

# Sports page: display session names instead of numeric round labels
old_nav='$("#roundNav").innerHTML=rounds.map(r=>\'<button class="ghost \'+(r.round_no===activeRound?\'active \':\'\')+(!r.is_open?\'locked\':\'\')+\'" data-round="\'+r.round_no+\'" \'+(!r.is_open?\'disabled\':\'\')+\'>מחזור \'+r.round_no+(r.is_open?\'\':\' 🔒\')+\'</button>\').join("")'
new_nav='$("#roundNav").innerHTML=rounds.map(r=>\'<button class="ghost \'+(r.round_no===activeRound?\'active \':\'\')+(!r.is_open?\'locked\':\'\')+\'" data-round="\'+r.round_no+\'" \'+(!r.is_open?\'disabled\':\'\')+\'>\'+esc(r.name||("סשן "+r.round_no))+(r.is_open?\'\':\' 🔒\')+\'</button>\').join("")'
if old_nav not in s:
    raise SystemExit('sports session nav anchor missing')
s=s.replace(old_nav,new_nav,1)
s=s.replace("'אין כרגע משחקים פתוחים במחזור '+activeRound+'.'", "'אין כרגע משחקים פתוחים בסשן הזה.'", 1)

# Add game now uses flexible session endpoint and requires a selected session
old_add='$("#addGame").onclick=async()=>{const game={home_team:$("#home").value.trim(),away_team:$("#away").value.trim(),starts_at:$("#start").value?new Date($("#start").value).toISOString():null,odd_home:+$("#oh").value,odd_draw:+$("#od").value,odd_away:+$("#oa").value,round_no:+$("#round").value};if(!game.home_team||!game.away_team||game.odd_home<=0||game.odd_draw<=0||game.odd_away<=0)return $("#adminMsg").textContent="יש למלא קבוצות ואת כל היחסים.";try{await adminReq("add_betting_game",{game});$("#adminMsg").textContent="✅ המשחק נוסף";await adminGames();await load()}catch(e){$("#adminMsg").textContent=e.message}};'
new_add='$("#addGame").onclick=async()=>{const game={home_team:$("#home").value.trim(),away_team:$("#away").value.trim(),starts_at:$("#start").value?new Date($("#start").value).toISOString():null,odd_home:+$("#oh").value,odd_draw:+$("#od").value,odd_away:+$("#oa").value,round_no:+$("#round").value};if(!game.round_no)return $("#adminMsg").textContent="יש לבחור סשן.";if(!game.home_team||!game.away_team||game.odd_home<=0||game.odd_draw<=0||game.odd_away<=0)return $("#adminMsg").textContent="יש למלא קבוצות ואת כל היחסים.";try{await adminSessionReq("add_game",{game});$("#adminMsg").textContent="✅ המשחק נוסף";await adminGames();await load()}catch(e){$("#adminMsg").textContent=e.message}};'
if old_add not in s:
    raise SystemExit('add game anchor missing')
s=s.replace(old_add,new_add,1)

# Replace legacy rounds manager with named sessions manager
start=s.find('async function adminRounds(){')
end=s.find('function bindDynamicGameResultClear',start)
if start<0 or end<0:
    raise SystemExit('adminRounds function boundaries missing')
new_rounds='''async function adminRounds(){try{const d=await adminSessionReq("list_sessions"),rows=d.sessions||[],select=$("#round"),selected=select?select.value:"";if(select){select.innerHTML='<option value="">בחר סשן</option>'+rows.map(r=>'<option value="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+'</option>').join("");if(selected&&rows.some(r=>String(r.round_no)===selected))select.value=selected}else{}$("#adminRounds").innerHTML=rows.length?rows.map(r=>'<div class="roundAdmin"><b>'+esc(r.name||("סשן "+r.round_no))+'</b><button class="ghost roundToggle" data-round="'+r.round_no+'" data-open="'+r.is_open+'">'+(r.is_open?'🔒 נעל':'🔓 פתח')+'</button></div>').join(""):'<div class="muted">עדיין אין סשנים.</div>';document.querySelectorAll(".roundToggle").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_open",{round_no:+b.dataset.round,is_open:b.dataset.open!=="true"});await adminRounds();await load()}catch(e){siteAlert("לא ניתן לעדכן סשן: "+e.message,"שגיאה")}})}catch(e){$("#adminRounds").textContent=e.message}}
$("#createSession").onclick=async()=>{const input=$("#newSessionName"),msg=$("#sessionMsg"),name=input.value.trim();if(!name){msg.textContent="יש להזין שם לסשן.";return}const btn=$("#createSession"),old=btn.textContent;btn.disabled=true;btn.textContent="יוצר...";try{await adminSessionReq("create_session",{name});input.value="";msg.textContent="✅ הסשן נוצר ונפתח";await adminRounds();await load()}catch(e){msg.textContent=e.message}finally{btn.disabled=false;btn.textContent=old}}
'''
s=s[:start]+new_rounds+s[end:]

# Existing games: show session name, keeping current ordering and controls
old_games='async function adminGames(){const box=$("#adminGames");box.innerHTML=\'<div class="muted">טוען...</div>\';try{const d=await adminReq("list_betting_games"),rows=d.games||[];box.innerHTML=rows.length?rows.map(g=>\'<div class="adminGame" data-id="\'+g.id+\'"><div class="adminGameTitle">מחזור \'+g.round_no+\' • \'+esc(g.home_team)+\' - \'+esc(g.away_team)+\'</div>'
new_games='async function adminGames(){const box=$("#adminGames");box.innerHTML=\'<div class="muted">טוען...</div>\';try{const [d,sd]=await Promise.all([adminReq("list_betting_games"),adminSessionReq("list_sessions")]),rows=d.games||[],sessionNames=new Map((sd.sessions||[]).map(r=>[Number(r.round_no),r.name||("סשן "+r.round_no)]));box.innerHTML=rows.length?rows.map(g=>\'<div class="adminGame" data-id="\'+g.id+\'"><div class="adminGameTitle">\'+esc(sessionNames.get(Number(g.round_no))||("סשן "+g.round_no))+\' • \'+esc(g.home_team)+\' - \'+esc(g.away_team)+\'</div>'
if old_games not in s:
    raise SystemExit('adminGames title anchor missing')
s=s.replace(old_games,new_games,1)

# Guardrails
for bad in ['פתיחה/נעילת מחזורים','פתיחה / נעילת מחזורים','<option value="8">מחזור 8</option>']:
    if bad in s:
        raise SystemExit('legacy UI remains: '+bad)
for good in ['ניהול סשנים','create_session','set_session_open','SESSIONS_ADMIN_URL','adminSessionReq','חצי גמר ליגת האלופות']:
    if good not in s:
        raise SystemExit('missing '+good)

p.write_text(s,encoding='utf-8')
print('converted betting rounds UI to named sessions')
