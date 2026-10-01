from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

MARK='REDBALL-BULK-VISIBILITY-V1'
if MARK in s:
    raise SystemExit('patch already applied')

def function_end(src,start):
    brace=src.find('{',start)
    if brace<0:return -1
    depth=0;i=brace;quote=None;escape=False;line_comment=False;block_comment=False
    while i<len(src):
        c=src[i];n=src[i+1] if i+1<len(src) else ''
        if line_comment:
            if c=='\n':line_comment=False
            i+=1;continue
        if block_comment:
            if c=='*' and n=='/':block_comment=False;i+=2;continue
            i+=1;continue
        if quote:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c==quote:quote=None
            i+=1;continue
        if c=='/' and n=='/':line_comment=True;i+=2;continue
        if c=='/' and n=='*':block_comment=True;i+=2;continue
        if c in ('"',"'",'`'):quote=c;i+=1;continue
        if c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    return -1

# CSS
css='''\n/* REDBALL-BULK-VISIBILITY-V1 */\n.bulkAddBox{margin-top:18px;padding-top:18px;border-top:1px solid #333}.bulkAddBox h3{margin:0 0 8px}.bulkHelp{margin:0 0 10px;color:#999;font-size:12px;line-height:1.6}.bulkGamesInput{width:100%;min-height:180px;resize:vertical;background:#111;color:#fff;border:1px solid #444;border-radius:10px;padding:12px;font-family:inherit;font-size:14px;line-height:1.7;direction:rtl}.bulkResults{margin-top:12px}.bulkResultRow{display:grid;grid-template-columns:1.5fr auto auto auto;gap:8px;align-items:center;padding:9px 0;border-bottom:1px solid #292929;font-size:12px}.bulkResultRow:last-child{border-bottom:0}.bulkOk{color:#62e6a7}.bulkWarn{color:#ffb143}.bulkBad{color:#ff6672}.sessionEye{min-width:46px;font-size:18px!important}.sessionHidden{opacity:.55}.roundNav button.locked{opacity:.72;border-style:dashed}.roundNav button.hiddenSession{display:none}@media(max-width:700px){.bulkResultRow{grid-template-columns:1fr 1fr}.bulkResultRow span:first-child{grid-column:1/-1}}\n'''
s=s.replace('</style>',css+'</style>',1)

# Bulk UI inside add-game tab.
add_start=s.find('<section id="adminTabAdd"')
if add_start<0: raise SystemExit('adminTabAdd not found')
add_end=s.find('</section>',add_start)
if add_end<0: raise SystemExit('adminTabAdd end not found')
bulk_markup='''<div class="bulkAddBox"><h3>📋 הוספת מחזור / רשימת משחקים</h3><p class="bulkHelp">בחר סשן למעלה והדבק עד 40 משחקים. פורמט מומלץ: <b>01/10 19:00 | ארסנל - ברצלונה</b><br>המערכת תחפש Fixture ב-API-Football, תבדוק Elo ותחשב יחסים לבד. משחק שלא אומת יישמר נעול.</p><textarea id="bulkGamesInput" class="bulkGamesInput" placeholder="01/10 19:00 | ארסנל - ברצלונה&#10;01/10 21:00 | ריאל מדריד - אינטר"></textarea><button id="bulkAddGames" class="primary" type="button">🔎 בדוק והוסף את כל המשחקים</button><p id="bulkGamesMsg" class="statusMsg"></p><div id="bulkGamesResults" class="bulkResults"></div></div>'''
s=s[:add_end]+bulk_markup+s[add_end:]

# Replace adminRounds: add customer visibility eye toggle and keep existing actions.
start=s.find('async function adminRounds(){')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit('adminRounds parse failed')
admin_rounds=r'''async function adminRounds(){try{const d=await adminSessionReq("list_sessions"),rows=d.sessions||[],select=$("#round"),selected=select?select.value:"";if(select){select.innerHTML='<option value="">בחר סשן</option>'+rows.map(r=>'<option value="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+'</option>').join("");if(selected&&rows.some(r=>String(r.round_no)===selected))select.value=selected}$("#adminRounds").innerHTML=rows.length?rows.map(r=>'<div class="roundAdmin '+(r.customer_visible===false?'sessionHidden':'')+'" data-round="'+r.round_no+'"><div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;flex-wrap:wrap"><b class="sessionNameText" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(r.name||("סשן "+r.round_no))+'</b><span class="small">'+(r.is_open?'🟢 פתוח':'🔒 נעול')+'</span><button class="ghost renameSession" type="button" data-round="'+r.round_no+'" data-name="'+esc(r.name||("סשן "+r.round_no))+'" style="padding:6px 9px;font-size:12px">✏️ שנה שם</button><button class="ghost danger deleteSession" type="button" data-round="'+r.round_no+'" data-name="'+esc(r.name||("סשן "+r.round_no))+'" style="padding:6px 9px;font-size:12px">🗑 מחק סשן</button></div><button class="ghost sessionEye" title="'+(r.customer_visible===false?'מוסתר מהלקוחות - לחץ להצגה':'מוצג ללקוחות - לחץ להסתרה')+'" data-round="'+r.round_no+'" data-visible="'+(r.customer_visible!==false)+'">'+(r.customer_visible===false?'🙈':'👁️')+'</button><button class="ghost roundToggle" data-round="'+r.round_no+'" data-open="'+r.is_open+'">'+(r.is_open?'🔒 נעל':'🔓 פתח')+'</button></div>').join(""):'<div class="muted">עדיין אין סשנים.</div>';document.querySelectorAll(".renameSession").forEach(b=>b.onclick=async()=>{const current=b.dataset.name||'',name=(await sitePrompt("שם חדש לסשן:",current,"שינוי שם סשן"));if(name===null)return;const clean=String(name).trim();if(!clean)return siteAlert("יש להזין שם לסשן.","שגיאה");if(clean===current)return;try{await adminSessionReq("rename_session",{round_no:+b.dataset.round,name:clean});siteToast("שם הסשן עודכן");await adminRounds();await adminGames();await load()}catch(e){siteAlert("לא ניתן לשנות שם: "+e.message,"שגיאה")}});document.querySelectorAll(".deleteSession").forEach(b=>b.onclick=async()=>{const name=b.dataset.name||("סשן "+b.dataset.round);if(!await siteConfirm("למחוק את הסשן ‘"+name+"’?\nכל המשחקים שבו יימחקו גם הם.\nאם קיימים טפסי הימור שמשתמשים במשחקים מהסשן – המחיקה תיחסם.","מחיקת סשן"))return;try{const d=await adminSessionReq("delete_session",{round_no:+b.dataset.round});siteToast("הסשן נמחק"+(d.deleted_games?" יחד עם "+d.deleted_games+" משחקים":""));await adminRounds();await adminGames();await load();if($("#adminTabArchive")?.classList.contains("active"))await loadArchive()}catch(e){siteAlert("לא ניתן למחוק סשן: "+e.message,"שגיאה")}});document.querySelectorAll(".roundToggle").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_open",{round_no:+b.dataset.round,is_open:b.dataset.open!=="true"});await adminRounds();await adminGames();await load();if($("#adminTabArchive")?.classList.contains("active"))await loadArchive()}catch(e){siteAlert("לא ניתן לעדכן סשן: "+e.message,"שגיאה")}});document.querySelectorAll(".sessionEye").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_visible",{round_no:+b.dataset.round,customer_visible:b.dataset.visible!=="true"});await adminRounds();await load();siteToast(b.dataset.visible==="true"?"הסשן הוסתר מהלקוחות":"הסשן מוצג ללקוחות")}catch(e){siteAlert("לא ניתן לעדכן תצוגה: "+e.message,"שגיאה")}})}catch(e){$("#adminRounds").textContent=e.message}}'''
s=s[:start]+admin_rounds+s[end:]

# Replace customer load: visible locked sessions remain visible; eye controls hiding.
start=s.find('async function load(){')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit('load parse failed')
load_fn=r'''async function load(){const [{data,error},{data:rd,error:re}]=await Promise.all([db.from("betting_games").select("*").order("starts_at"),db.from("betting_rounds").select("*").order("round_no")]);if(error||re){$("#games").innerHTML='<div class="muted">שגיאה בטעינת המשחקים</div>';return}rounds=rd||[];const now=Date.now(),allGames=data||[],byRound=new Map();allGames.forEach(g=>{const k=Number(g.round_no);if(!byRound.has(k))byRound.set(k,[]);byRound.get(k).push(g)});const visibleRounds=rounds.filter(r=>r.customer_visible!==false&&(byRound.get(Number(r.round_no))||[]).length);const hasFuture=r=>(byRound.get(Number(r.round_no))||[]).some(g=>!g.starts_at||new Date(g.starts_at).getTime()>now);if(!visibleRounds.some(r=>r.round_no===activeRound)){const preferred=visibleRounds.find(r=>r.is_open&&hasFuture(r))||visibleRounds.find(r=>hasFuture(r))||visibleRounds[visibleRounds.length-1];activeRound=preferred?.round_no||activeRound}$("#roundNav").innerHTML=visibleRounds.length?visibleRounds.map(r=>'<button class="ghost '+(r.round_no===activeRound?'active ':'')+(!r.is_open?'locked ':'')+'" data-round="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+(r.is_open?'':' · 🔒')+'</button>').join(""):'<span class="muted">אין כרגע סשנים להצגה.</span>';document.querySelectorAll("#roundNav button").forEach(b=>b.onclick=()=>{activeRound=+b.dataset.round;load()});games=allGames.filter(g=>g.round_no===activeRound);const activeSession=rounds.find(r=>r.round_no===activeRound);for(const [id] of sel){const g=allGames.find(x=>x.id===id),r=rounds.find(x=>x.round_no===g?.round_no);if(!g||!g.is_open||!r?.is_open||r?.customer_visible===false||(g.starts_at&&new Date(g.starts_at).getTime()<=now))sel.delete(id)}$("#games").innerHTML=games.length?games.map(g=>{const started=!!g.starts_at&&new Date(g.starts_at).getTime()<=now,finished=!!g.result,sessionLocked=!activeSession?.is_open,locked=!g.is_open||started||sessionLocked,score=g.api_home_goals!=null&&g.api_away_goals!=null?Number(g.api_home_goals)+' - '+Number(g.api_away_goals):'',state=finished?'<span class="gameState finished">✅ הסתיים</span>':sessionLocked?'<span class="gameState locked">🔒 הסשן נעול</span>':locked?'<span class="gameState locked">🔒 נעול להימורים</span>':'',result=finished?'<div class="gameResult">תוצאה: <b>'+esc(String(g.result))+'</b>'+(score?' · '+esc(score):'')+'</div>':'';return '<div class="game '+(locked?'lockedGame':'')+'" data-game-id="'+g.id+'"><div class="small">'+(g.starts_at?fmtDate(g.starts_at):"")+'</div>'+state+'<div class="teams">'+esc(g.home_team)+' 🆚 '+esc(g.away_team)+'</div><div class="odds">'+[["1",g.home_team,g.odd_home],["X","תיקו",g.odd_draw],["2",g.away_team,g.odd_away]].map((x,j)=>'<button class="odd" data-j="'+j+'" '+(locked?'disabled':'')+'><span class="mark">'+x[0]+'</span><span class="teamName">'+esc(x[1])+'</span><b>'+Number(x[2]).toFixed(2)+'</b></button>').join("")+'</div>'+result+'</div>'}).join(""):'<div class="muted">אין משחקים בסשן הזה.</div>';document.querySelectorAll(".odd:not([disabled])").forEach(b=>b.onclick=()=>choose(b));syncSelectedOdds();ticket()}'''
s=s[:start]+load_fn+s[end:]

# Replace archive loader: use authenticated admin endpoints and consider locked sessions archived too.
start=s.find('async function loadArchive(){')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit('loadArchive parse failed')
archive_fn=r'''async function loadArchive(){const box=$("#adminSessionArchive");if(!box)return;box.innerHTML='<div class="muted">טוען ארכיון...</div>';try{const [gd,rd]=await Promise.all([adminReq("list_betting_games"),adminSessionReq("list_sessions")]),allGames=gd.games||[],allRounds=rd.sessions||[],now=Date.now(),byRound=new Map();allGames.forEach(g=>{const k=Number(g.round_no);if(!byRound.has(k))byRound.set(k,[]);byRound.get(k).push(g)});const archived=allRounds.map(r=>({round:r,games:byRound.get(Number(r.round_no))||[]})).filter(x=>x.games.length&&(!x.round.is_open||x.games.every(g=>g.result||g.starts_at&&new Date(g.starts_at).getTime()<=now))).sort((a,b)=>Number(b.round.round_no)-Number(a.round.round_no));if(!archived.length){box.innerHTML='<div class="panel archiveEmpty">עדיין אין סשנים בארכיון.</div>';return}box.innerHTML=archived.map(x=>'<section class="archiveSession"><div class="archiveSessionHead"><div><b>'+esc(x.round.name||('סשן '+x.round.round_no))+'</b><div class="small">'+(x.round.is_open?'כל המשחקים כבר התחילו':'🔒 הסשן נעול')+' · '+(x.round.customer_visible===false?'🙈 מוסתר מהלקוחות':'👁️ מוצג ללקוחות')+'</div></div><span class="small">'+x.games.length+' משחקים</span></div><div class="archiveSessionBody">'+x.games.sort((a,b)=>new Date(a.starts_at||0)-new Date(b.starts_at||0)).map(g=>{const score=g.api_home_goals!=null&&g.api_away_goals!=null?Number(g.api_home_goals)+' - '+Number(g.api_away_goals):'—',rt=g.result==='1'?'ניצחון '+g.home_team:g.result==='2'?'ניצחון '+g.away_team:g.result==='X'?'תיקו':'ממתין לתוצאה';return '<div class="archiveGame"><div class="archiveGameTop"><div><b>'+esc(g.home_team)+' 🆚 '+esc(g.away_team)+'</b><div class="small">'+(g.starts_at?fmtDate(g.starts_at):'')+'</div></div><div class="archiveScore">'+esc(score)+'</div></div><div class="archiveResult">'+esc(rt)+(g.result_set_by==='API_FOOTBALL'?' · עודכן אוטומטית':'')+'</div></div>'}).join('')+'</div></section>').join('')}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}}'''
s=s[:start]+archive_fn+s[end:]

# Bulk parser + handler, inserted before single add-game handler.
anchor='$("#addGame").onclick=async()=>'
idx=s.find(anchor)
if idx<0: raise SystemExit('addGame handler anchor missing')
bulk_js=r'''function parseBulkGames(text){const out=[],bad=[];String(text||'').split(/\r?\n/).map(x=>x.trim()).filter(Boolean).forEach((line,i)=>{const parts=line.split('|').map(x=>x.trim());if(parts.length!==2){bad.push({line:i+1,text:line,reason:'חסר | בין התאריך למשחק'});return}const dateRe=/(\d{1,2})\/(\d{1,2})(?:\/(\d{4}))?\s+(\d{1,2}):(\d{2})/;const datePart=dateRe.test(parts[0])?parts[0]:dateRe.test(parts[1])?parts[1]:null,gamePart=datePart===parts[0]?parts[1]:datePart===parts[1]?parts[0]:null;if(!datePart||!gamePart){bad.push({line:i+1,text:line,reason:'תאריך/שעה לא זוהו'});return}const m=datePart.match(dateRe),gm=gamePart.match(/^(.+?)\s+[-–—]\s+(.+)$/);if(!m||!gm){bad.push({line:i+1,text:line,reason:'פורמט קבוצות לא תקין'});return}const day=+m[1],month=+m[2],year=+(m[3]||new Date().getFullYear()),hour=+m[4],minute=+m[5],d=new Date(year,month-1,day,hour,minute,0,0);if(Number.isNaN(d.getTime())||d.getDate()!==day||d.getMonth()!==month-1){bad.push({line:i+1,text:line,reason:'תאריך לא תקין'});return}out.push({home_team:gm[1].trim(),away_team:gm[2].trim(),starts_at:d.toISOString(),source_line:i+1})});return{games:out,bad}}
function renderBulkResults(rows){const box=$("#bulkGamesResults");if(!box)return;box.innerHTML=(rows||[]).map(r=>'<div class="bulkResultRow"><span><b>'+esc(r.game||'')+'</b></span><span class="'+(r.api_ok?'bulkOk':'bulkBad')+'">'+(r.api_ok?'✅ API':'⚠️ API')+'</span><span class="'+(r.elo_ok?'bulkOk':'bulkBad')+'">'+(r.elo_ok?'✅ Elo':'⚠️ Elo')+'</span><span class="'+(r.ok?(r.opened?'bulkOk':'bulkWarn'):'bulkBad')+'">'+(r.ok?(r.opened?('🟢 '+(r.odds||[]).map(x=>Number(x).toFixed(2)).join(' / ')):'🔒 נשמר נעול'):'❌ '+esc(r.error||'נכשל'))+'</span></div>').join('')}
const bulkBtn=$("#bulkAddGames");if(bulkBtn)bulkBtn.onclick=async()=>{const msg=$("#bulkGamesMsg"),round=+$("#round").value,parsed=parseBulkGames($("#bulkGamesInput").value);msg.className='statusMsg';$("#bulkGamesResults").innerHTML='';if(!round){msg.textContent='יש לבחור סשן למעלה.';msg.classList.add('error');return}if(parsed.bad.length){msg.textContent='יש '+parsed.bad.length+' שורות שלא הצלחתי לקרוא. שורה '+parsed.bad[0].line+': '+parsed.bad[0].reason;msg.classList.add('error');return}if(!parsed.games.length){msg.textContent='לא נמצאו משחקים להוספה.';msg.classList.add('error');return}if(parsed.games.length>40){msg.textContent='אפשר להוסיף עד 40 משחקים בפעולה אחת.';msg.classList.add('error');return}const old=bulkBtn.textContent;bulkBtn.disabled=true;bulkBtn.textContent='⏳ בודק API, Elo ומוסיף...';try{const d=await adminSessionReq('bulk_add_games',{round_no:round,games:parsed.games});msg.textContent='✅ נוספו '+d.inserted+' מתוך '+d.total+' · נפתחו '+d.opened+' · נשמרו נעולים '+d.locked+(d.failed?' · נכשלו '+d.failed:'');msg.className='statusMsg '+(d.failed?'':'success');renderBulkResults(d.results||[]);await adminGames();await adminRounds();await load()}catch(e){msg.textContent=e.message;msg.className='statusMsg error'}finally{bulkBtn.disabled=false;bulkBtn.textContent=old}}
'''
s=s[:idx]+bulk_js+s[idx:]

for token in [MARK,'bulk_add_games','set_session_visible','sessionEye','id="bulkGamesInput"','async function loadArchive(){const box=$("#adminSessionArchive")']:
    if token not in s: raise SystemExit('missing '+token)

p.write_text(s,encoding='utf-8')
print('bulk import + visibility + archive patch applied')
