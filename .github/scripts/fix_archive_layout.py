from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

MARK='REDBALL-ARCHIVE-LAYOUT-FIX-V1'
if MARK in s:
    raise SystemExit('patch already applied')

# Move archive pane so it is a sibling of the other admin panes rather than nested inside "All Bets".
start=s.find('<section id="adminTabArchive"')
if start < 0:
    raise SystemExit('adminTabArchive not found')
end=s.find('</section>', start)
if end < 0:
    raise SystemExit('adminTabArchive closing section not found')
end += len('</section>')
archive_markup=s[start:end]
s=s[:start]+s[end:]

bets_start=s.find('<section id="adminTabBets"')
if bets_start < 0:
    raise SystemExit('adminTabBets not found')
bets_end=s.find('</section>', bets_start)
if bets_end < 0:
    raise SystemExit('adminTabBets closing section not found')
bets_end += len('</section>')
s=s[:bets_end]+archive_markup+s[bets_end:]

# Clarify archive definition: only sessions whose games have all started belong in the archive.
s=s.replace('סשנים שכל המשחקים בהם כבר התחילו נשמרים כאן לצפייה ניהולית.','סשנים שכל המשחקים בהם כבר התחילו נשמרים כאן לצפייה ניהולית.',1)

# Replace archive loader with a strict all-games-started rule and visible error state.
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

fs=s.find('async function loadArchive(){')
fe=function_end(s,fs)
if fs<0 or fe<0:
    raise SystemExit('loadArchive parse failed')
new_fn=r'''async function loadArchive(){const box=$("#adminSessionArchive");if(!box)return;box.innerHTML='<div class="muted">טוען ארכיון...</div>';try{const [gd,rd]=await Promise.all([adminReq("list_betting_games"),adminSessionReq("list_sessions")]),allGames=gd.games||[],allRounds=rd.sessions||[],now=Date.now(),byRound=new Map();allGames.forEach(g=>{const k=Number(g.round_no);if(!byRound.has(k))byRound.set(k,[]);byRound.get(k).push(g)});const archived=allRounds.map(r=>({round:r,games:byRound.get(Number(r.round_no))||[]})).filter(x=>x.games.length&&x.games.every(g=>g.starts_at&&new Date(g.starts_at).getTime()<=now)).sort((a,b)=>Number(b.round.round_no)-Number(a.round.round_no));if(!archived.length){box.innerHTML='<div class="panel archiveEmpty">עדיין אין סשנים שהסתיימו.</div>';return}box.innerHTML=archived.map(x=>'<section class="archiveSession"><div class="archiveSessionHead"><b>'+esc(x.round.name||('סשן '+x.round.round_no))+'</b><span class="small">'+x.games.length+' משחקים</span></div><div class="archiveSessionBody">'+x.games.sort((a,b)=>new Date(a.starts_at||0)-new Date(b.starts_at||0)).map(g=>{const score=g.api_home_goals!=null&&g.api_away_goals!=null?Number(g.api_home_goals)+' - '+Number(g.api_away_goals):'—';return '<div class="archiveGame"><div class="archiveGameTop"><div><b>'+esc(g.home_team)+' 🆚 '+esc(g.away_team)+'</b><div class="small">'+(g.starts_at?fmtDate(g.starts_at):'')+'</div></div><div class="archiveScore">'+esc(score)+'</div></div><div class="archiveResult">'+esc(resultText(g))+(g.result_set_by==='API_FOOTBALL'?' · עודכן אוטומטית':'')+'</div></div>'}).join('')+'</div></section>').join('')}catch(e){box.innerHTML='<div class="statusMsg error">שגיאה בטעינת הארכיון: '+esc(e.message||String(e))+'</div>'}}'''
s=s[:fs]+new_fn+s[fe:]

# Marker for idempotency / diagnostics.
s=s.replace('</style>','/* REDBALL-ARCHIVE-LAYOUT-FIX-V1 */\n</style>',1)

# Safety checks.
if s.count('id="adminTabArchive"') != 1:
    raise SystemExit('archive pane count unexpected')
if 'async function loadArchive(){const box=$("#adminSessionArchive")' not in s:
    raise SystemExit('archive loader missing')

p.write_text(s,encoding='utf-8')
print('archive pane layout and loader fixed')
