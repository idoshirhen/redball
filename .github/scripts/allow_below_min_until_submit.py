from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

old_clamp='function clampStake(){let el=$("#stake"),v=Number(el.value);if(!Number.isFinite(v)||v<10000){el.value=10000;setMsg("");ticket();return}if(v>100000){el.value=100000;setMsg("");ticket();return}if(v%1000!==0){setMsg("יש לשלוח הימור בקפיצות של 1,000");ticket();return}setMsg("");ticket()}function ticket()'
new_clamp='function clampStake(){let el=$("#stake"),v=Number(el.value);if(Number.isFinite(v)&&v>100000)el.value=100000;ticket()}function ticket()'
if old_clamp not in s:
    raise SystemExit('current clampStake anchor not found')
s=s.replace(old_clamp,new_clamp,1)

old_ticket='s=Math.min(100000,Math.max(10000,+$("#stake").value||10000))'
new_ticket='s=Math.min(100000,Math.max(0,+$("#stake").value||0))'
if old_ticket not in s:
    raise SystemExit('ticket stake calculation anchor not found')
s=s.replace(old_ticket,new_ticket,1)

old_input='id="stake" type="number" min="10000" max="100000" step="1000"'
new_input='id="stake" type="number" min="0" max="100000" step="1000"'
if old_input not in s:
    raise SystemExit('stake input constraints anchor not found')
s=s.replace(old_input,new_input,1)

old_submit='if(stake<10000||stake>100000)return setMsg("סכום ההימור חייב להיות בין 10,000 ל-100,000.");'
new_submit='if(stake<10000)return setMsg("סכום ההימור המינימלי הוא 10,000.");if(stake>100000)return setMsg("סכום ההימור המקסימלי הוא 100,000.");'
if old_submit not in s:
    raise SystemExit('submit stake validation anchor not found')
s=s.replace(old_submit,new_submit,1)

for token in [
    'min="0" max="100000" step="1000"',
    'סכום ההימור המינימלי הוא 10,000.',
    'Math.max(0,+$("#stake").value||0)',
    'if(Number.isFinite(v)&&v>100000)el.value=100000'
]:
    if token not in s:
        raise SystemExit('missing expected token: '+token)

p.write_text(s,encoding='utf-8')
print('stake can stay below 10,000 until submit while 100,000 max remains live')
