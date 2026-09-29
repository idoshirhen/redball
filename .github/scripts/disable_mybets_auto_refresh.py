from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')
old='setInterval(()=>{load();if($("#minePage").classList.contains("activePage"))loadMyBets()},30000);'
new='setInterval(()=>{load()},30000);'
if old not in s:
    raise SystemExit('30-second My Bets auto refresh anchor not found')
s=s.replace(old,new,1)
if 'setInterval(()=>{load();if($("#minePage").classList.contains("activePage"))loadMyBets()},30000)' in s:
    raise SystemExit('My Bets auto refresh still present')
p.write_text(s,encoding='utf-8')
print('Disabled 30-second My Bets auto refresh')
