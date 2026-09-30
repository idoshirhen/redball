from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

# Desktop nav becomes 4 columns.
s=s.replace('.mainNav{max-width:760px;margin:18px auto 0;display:grid;grid-template-columns:repeat(3,1fr);', '.mainNav{max-width:760px;margin:18px auto 0;display:grid;grid-template-columns:repeat(4,1fr);', 1)

# Add archive nav button.
old_nav='<button class="navBtn" data-page="mine" type="button">🎫 ההימורים שלי</button><button class="navBtn" id="adminNav" type="button">🔐 ניהול ההימורים</button>'
new_nav='<button class="navBtn" data-page="mine" type="button">🎫 ההימורים שלי</button><button class="navBtn" data-page="archive" type="button">📦 ארכיון משחקים</button><button class="navBtn" id="adminNav" type="button">🔐 ניהול ההימורים</button>'
if 'data-page="archive"' not in s:
    if old_nav not in s: raise SystemExit('nav anchor not found')
    s=s.replace(old_nav,new_nav,1)

# Add customer archive page.
archive_markup='''<section id="archivePage" class="page"><div class="pageTitle"><h1>📦 ארכיון משחקים</h1><p>סשנים שהמשחקים בהם כבר התחילו נשמרים כאן עם התוצאות</p></div><div class="myBetsWrap"><div id="sessionArchive"><div class="muted">טוען ארכיון...</div></div></div></section>\n'''
if 'id="archivePage"' not in s:
    anchor='<section id="adminPage" class="page">'
    if anchor not in s: raise SystemExit('admin page anchor not found')
    s=s.replace(anchor,archive_markup+anchor,1)

# Archive/locked game styling.
css='''\n/* REDBALL-CUSTOMER-SESSION-ARCHIVE-V1 */\n.game.lockedGame{opacity:.88;border-color:#3d3d3d;background:linear-gradient(180deg,rgba(24,24,24,.96),rgba(15,15,15,.96))}.gameState{display:inline-flex;align-items:center;gap:6px;margin-top:4px;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:800}.gameState.locked{color:#bbb;background:#151515;border:1px solid #3d3d3d}.gameState.finished{color:#62e6a7;background:rgba(98,230,167,.10);border:1px solid rgba(98,230,167,.25)}.gameResult{margin-top:10px;padding:9px 10px;border-radius:9px;background:#0d0d0d;border:1px solid #303030;font-size:13px}.game.lockedGame .odd{cursor:not-allowed;opacity:.55}.archiveSession{border:1px solid #343434;border-radius:14px;background:rgba(16,16,16,.97);margin-bottom:14px;overflow:hidden}.archiveSessionHead{padding:13px 14px;background:#181818;border-bottom:1px solid #303030;display:flex;justify-content:space-between;gap:10px;align-items:center}.archiveSessionHead b{font-size:16px}.archiveSessionBody{padding:12px}.archiveGame{padding:11px 0;border-bottom:1px solid #292929}.archiveGame:last-child{border-bottom:0}.archiveGameTop{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.archiveScore{font-weight:800;color:#6ed8ff;white-space:nowrap}.archiveResult{margin-top:5px;font-size:12px;color:#bbb}.archiveEmpty{padding:18px;text-align:center;color:#999}\n'''
if 'REDBALL-CUSTOMER-SESSION-ARCHIVE-V1' not in s:
    if '</style>' not in s: raise SystemExit('style end not found')
    s=s.replace('</style>',css+'</style>',1)

# Replace showPage only.
start=s.find('function showPage(name){')
end=s.find("document.querySelectorAll('.navBtn[data-page]')",start)
if start<0 or end<0: raise SystemExit('showPage boundaries not found')
show='''function showPage(name){document.querySelectorAll(".page").forEach(p=>p.classList.remove("activePage"));document.querySelectorAll(".navBtn").forEach(b=>b.classList.remove("active"));const page=$("#"+name+"Page");if(page)page.classList.add("activePage");const nav=document.querySelector('.navBtn[data-page="'+name+'"]');if(nav)nav.classList.add("active");if(name==="admin")$("#adminNav").classList.add("active");$("#mobileTicketBar").style.display=name==="sports"&&innerWidth<=800?"flex":"none";toggleTicket(false);window.scrollTo({top:0,behavior:"smooth"});if(name==="mine")loadMyBets();if(name==="archive")loadArchive()}'''
s=s[:start]+show+s[end:]

# Replace load() and add customer archive loader. This keeps started/finished games visible but non-bettable.
start=s.find('async function load(){')
end=s.find('function choose(b){',start)
if start<0 or end<0: raise SystemExit('load boundaries not found')
new_load=r'''async function load(){const [{data,error},{data:rd,error:re}]=await Promise.all([db.from("betting_games").select("*").order("starts_at"),db.from("betting_rounds").select("*").order("round_no")]);if(error||re){$("#games").innerHTML='<div class="muted">שגיאה בטעינת המשחקים</div>';return}rounds=rd||[];const now=Date.now(),allGames=data||[],openRounds=rounds.filter(r=>r.is_open).map(r=>r.round_no),roundHasFutureOpen=new Set(allGames.filter(g=>g.is_open&&openRounds.includes(g.round_no)&&(!g.starts_at||new Date(g.starts_at).getTime()>now)).map(g=>g.round_no));const visibleRounds=rounds.filter(r=>roundHasFutureOpen.has(r.round_no));if(!visibleRounds.some(r=>r.round_no===activeRound))activeRound=visibleRounds[0]?.round_no||activeRound;$("#roundNav").innerHTML=visibleRounds.length?visibleRounds.map(r=>'<button class="ghost '+(r.round_no===activeRound?'active ':'')+'" data-round="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+'</button>').join(""):'<span class="muted">אין כרגע סשנים פתוחים להימורים.</span>';document.querySelectorAll("#roundNav button").forEach(b=>b.onclick=()=>{activeRound=+b.dataset.round;load()});games=allGames.filter(g=>g.round_no===activeRound);for(const [id] of sel){const g=allGames.find(x=>x.id===id);if(!g||!g.is_open||!openRounds.includes(g.round_no)||(g.starts_at&&new Date(g.starts_at).getTime()<=now))sel.delete(id)}$("#games").innerHTML=games.length?games.map(g=>{const started=!!g.starts_at&&new Date(g.starts_at).getTime()<=now,finished=!!g.result,locked=!g.is_open||started||!openRounds.includes(g.round_no),score=g.api_home_goals!=null&&g.api_away_goals!=null?Number(g.api_home_goals)+' - '+Number(g.api_away_goals):'',state=finished?'<span class="gameState finished">✅ הסתיים</span>':locked?'<span class="gameState locked">🔒 נעול להימורים</span>':'',result=finished?'<div class="gameResult">תוצאה: <b>'+esc(String(g.result))+'</b>'+(score?' · '+esc(score):'')+'</div>':'';return '<div class="game '+(locked?'lockedGame':'')+'" data-game-id="'+g.id+'"><div class="small">'+(g.starts_at?fmtDate(g.starts_at):"")+'</div>'+state+'<div class="teams">'+esc(g.home_team)+' 🆚 '+esc(g.away_team)+'</div><div class="odds">'+[["1",g.home_team,g.odd_home],["X","תיקו",g.odd_draw],["2",g.away_team,g.odd_away]].map((x,j)=>'<button class="odd" data-j="'+j+'" '+(locked?'disabled':'')+'><span class="mark">'+x[0]+'</span><span class="teamName">'+esc(x[1])+'</span><b>'+Number(x[2]).toFixed(2)+'</b></button>').join("")+'</div>'+result+'</div>'}).join(""):'<div class="muted">אין משחקים בסשן הזה.</div>';document.querySelectorAll(".odd:not([disabled])").forEach(b=>b.onclick=()=>choose(b));syncSelectedOdds();ticket()}
function resultText(g){if(g.result==='1')return 'ניצחון '+g.home_team;if(g.result==='2')return 'ניצחון '+g.away_team;if(g.result==='X')return 'תיקו';return 'ממתין לתוצאה'}
async function loadArchive(){const box=$("#sessionArchive");if(!box)return;box.innerHTML='<div class="muted">טוען ארכיון...</div>';const [{data:allGames,error},{data:allRounds,error:re}]=await Promise.all([db.from("betting_games").select("*").order("starts_at",{ascending:false}),db.from("betting_rounds").select("*").order("round_no",{ascending:false})]);if(error||re){box.innerHTML='<div class="muted">שגיאה בטעינת הארכיון</div>';return}const now=Date.now(),byRound=new Map();for(const g of allGames||[]){if(!byRound.has(g.round_no))byRound.set(g.round_no,[]);byRound.get(g.round_no).push(g)}const archived=(allRounds||[]).map(r=>({round:r,games:byRound.get(r.round_no)||[]})).filter(x=>x.games.length&&x.games.every(g=>g.starts_at&&new Date(g.starts_at).getTime()<=now));if(!archived.length){box.innerHTML='<div class="panel archiveEmpty">עדיין אין סשנים שהסתיימו.</div>';return}box.innerHTML=archived.map(x=>'<section class="archiveSession"><div class="archiveSessionHead"><b>'+esc(x.round.name||('סשן '+x.round.round_no))+'</b><span class="small">'+x.games.length+' משחקים</span></div><div class="archiveSessionBody">'+x.games.sort((a,b)=>new Date(a.starts_at||0)-new Date(b.starts_at||0)).map(g=>{const score=g.api_home_goals!=null&&g.api_away_goals!=null?Number(g.api_home_goals)+' - '+Number(g.api_away_goals):'—';return '<div class="archiveGame"><div class="archiveGameTop"><div><b>'+esc(g.home_team)+' 🆚 '+esc(g.away_team)+'</b><div class="small">'+(g.starts_at?fmtDate(g.starts_at):'')+'</div></div><div class="archiveScore">'+esc(score)+'</div></div><div class="archiveResult">'+esc(resultText(g))+(g.result_set_by==='API_FOOTBALL'?' · עודכן אוטומטית':'')+'</div></div>'}).join('')+'</div></section>').join('')}
'''
s=s[:start]+new_load+s[end:]

# Replace choose so manually closed/started games can never be selected from stale DOM.
start=s.find('function choose(b){')
end=s.find('function syncSelectedOdds(){',start)
if start<0 or end<0: raise SystemExit('choose boundaries not found')
choose=r'''function choose(b){const box=b.closest(".game"),j=+b.dataset.j,g=games.find(x=>x.id===box.dataset.gameId);if(!g)return;const round=rounds.find(r=>r.round_no===g.round_no);if(!g.is_open||!round?.is_open||(g.starts_at&&new Date(g.starts_at).getTime()<=Date.now())){load();setMsg("המשחק נעול להימורים.");return}const odds=[+g.odd_home,+g.odd_draw,+g.odd_away],labels=["1 - "+g.home_team,"X - תיקו","2 - "+g.away_team],existing=sel.get(g.id);if(existing&&existing.j===j){sel.delete(g.id);b.classList.remove("sel");ticket();return}if(!existing&&sel.size>=5){setMsg("אפשר לבחור עד 5 משחקים בהימור.");return}box.querySelectorAll(".odd").forEach(x=>x.classList.remove("sel"));b.classList.add("sel");sel.set(g.id,{game_id:g.id,g:g.home_team+" - "+g.away_team,l:labels[j],o:odds[j],j});setMsg("");ticket()}'''
s=s[:start]+choose+s[end:]

for required in ['archivePage','loadArchive()','REDBALL-CUSTOMER-SESSION-ARCHIVE-V1','lockedGame','📦 ארכיון משחקים']:
    if required not in s: raise SystemExit('missing '+required)

p.write_text(s,encoding='utf-8')
print('customer session archive patch applied')
