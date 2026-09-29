from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

old='$("#stake").oninput=ticket;'
new='$("#stake").oninput=()=>{const el=$("#stake"),v=Number(el.value);if(Number.isFinite(v)&&v>100000)el.value=100000;ticket()};'
if old not in s:
    raise SystemExit('stake oninput anchor not found')
s=s.replace(old,new,1)

# Keep the HTML constraints explicit as a second browser-level hint.
needle='id="stake" type="number" min="10000" max="100000" step="1000"'
if needle not in s:
    raise SystemExit('stake input min/max/step not found')

# Ensure submit validation for the 1,000 increment is still present.
if 'יש לשלוח הימור בקפיצות של 1,000' not in s:
    raise SystemExit('1000 increment validation message missing')

p.write_text(s,encoding='utf-8')
print('patched live max stake enforcement')
