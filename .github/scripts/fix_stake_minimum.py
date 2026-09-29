from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

old='function clampStake(){let el=$("#stake"),v=Number(el.value);if(!Number.isFinite(v)){el.value=10000;ticket();return}if(v<10000||v>100000){setMsg("סכום ההימור חייב להיות בין 10,000 ל-100,000.");ticket();return}if(v%1000!==0){setMsg("יש לשלוח הימור בקפיצות של 1,000");ticket();return}setMsg("");ticket()}function ticket()'
new='function clampStake(){let el=$("#stake"),v=Number(el.value);if(!Number.isFinite(v)||v<10000){el.value=10000;setMsg("");ticket();return}if(v>100000){el.value=100000;setMsg("");ticket();return}if(v%1000!==0){setMsg("יש לשלוח הימור בקפיצות של 1,000");ticket();return}setMsg("");ticket()}function ticket()'
if old not in s:
    raise SystemExit('current clampStake anchor not found')
s=s.replace(old,new,1)

if 'id="stake" type="number" min="10000" max="100000" step="1000"' not in s:
    raise SystemExit('stake constraints missing')
if 'יש לשלוח הימור בקפיצות של 1,000' not in s:
    raise SystemExit('stake step message missing')

p.write_text(s,encoding='utf-8')
print('fixed minimum stake enforcement on blur')
