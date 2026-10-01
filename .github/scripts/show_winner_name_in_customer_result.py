from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

old="result=finished?'<div class=\"gameResult\">תוצאה: <b>'+esc(String(g.result))+'</b>'+(score?' · '+esc(score):'')+'</div>':'';"
new="result=finished?'<div class=\"gameResult\">תוצאה: <b>'+esc(g.result==='1'?g.home_team:g.result==='2'?g.away_team:g.result==='X'?'תיקו':String(g.result))+'</b>'+(score?' · '+esc(score):'')+'</div>':'';"

if old not in s:
    raise SystemExit('customer result markup anchor not found')
s=s.replace(old,new,1)

if "g.result==='1'?g.home_team" not in s or "g.result==='X'?'תיקו'" not in s:
    raise SystemExit('winner label patch missing')

p.write_text(s,encoding='utf-8')
print('customer game result now shows winner team name or draw')
