from pathlib import Path
p=Path('betting.html')
s=p.read_text(encoding='utf-8')
old_css='.pickOutcome{display:inline-flex;align-items:center;justify-content:center;width:25px;height:25px;border-radius:50%;margin-left:8px;font-size:15px;flex:0 0 25px}'
new_css='.pickOutcome{display:inline-flex;align-items:center;justify-content:center;width:25px;height:25px;border-radius:50%;margin-left:0;margin-right:0;font-size:15px;flex:0 0 25px}.myPickWithOutcome{display:flex;align-items:center;justify-content:flex-start;gap:10px;direction:rtl}'
if old_css not in s:
    raise SystemExit('outcome css anchor not found')
s=s.replace(old_css,new_css,1)
s=s.replace('.myPickWithOutcome{display:flex;align-items:center;justify-content:space-between;gap:10px}', '', 1)
old="<div class=\"myPick myPickWithOutcome\"><div class=\"myPickText\"><b>'+esc(p.g||\"\")+'</b><br>'+esc(p.l||\"\")+' • יחס '+Number(p.o||0).toFixed(2)+'</div>'+pickOutcomeIcon(p)+'</div>"
new="<div class=\"myPick myPickWithOutcome\">'+pickOutcomeIcon(p)+'<div class=\"myPickText\"><b>'+esc(p.g||\"\")+'</b><br>'+esc(p.l||\"\")+' • יחס '+Number(p.o||0).toFixed(2)+'</div></div>"
if old not in s:
    raise SystemExit('my bets pick markup anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Moved My Bets outcome icons to the right')