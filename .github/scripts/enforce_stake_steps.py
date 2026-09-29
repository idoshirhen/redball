from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

old='function clampStake(){let el=$("#stake"),v=Number(el.value);if(!Number.isFinite(v))v=10000;v=Math.min(100000,Math.max(10000,v));el.value=Math.round(v/1000)*1000;ticket()}function ticket()'
new='function clampStake(){let el=$("#stake"),v=Number(el.value);if(!Number.isFinite(v)){el.value=10000;ticket();return}if(v<10000||v>100000){setMsg("סכום ההימור חייב להיות בין 10,000 ל-100,000.");ticket();return}if(v%1000!==0){setMsg("יש לשלוח הימור בקפיצות של 1,000");ticket();return}setMsg("");ticket()}function ticket()'
if old not in s:
    raise SystemExit('clampStake anchor not found')
s=s.replace(old,new,1)

old2='if(stake<10000||stake>100000)return setMsg("סכום ההימור חייב להיות בין 10,000 ל-100,000.");const selectedGames='
new2='if(stake<10000||stake>100000)return setMsg("סכום ההימור חייב להיות בין 10,000 ל-100,000.");if(stake%1000!==0)return setMsg("יש לשלוח הימור בקפיצות של 1,000");const selectedGames='
if old2 not in s:
    raise SystemExit('submit validation anchor not found')
s=s.replace(old2,new2,1)

# input already uses step=1000; assert it remains so
if 'id="stake" type="number" min="10000" max="100000" step="1000"' not in s:
    raise SystemExit('stake input step=1000 missing')
if 'יש לשלוח הימור בקפיצות של 1,000' not in s:
    raise SystemExit('stake step message missing')

p.write_text(s,encoding='utf-8')
print('stake increment validation added')
