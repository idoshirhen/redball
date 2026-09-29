from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')
old="<div class=\"adminBetPicks\">'+picks.map(p=>esc((p.g||'')+' • '+(p.l||''))).join('<br>')+'</div>"
new="<div class=\"adminBetPicks\">'+picks.map(p=>'<div class=\"myPick myPickWithOutcome\">'+pickOutcomeIcon(p)+'<div class=\"myPickText\">'+esc((p.g||'')+' • '+(p.l||''))+'</div></div>').join('')+'</div>"
if old not in s:
    raise SystemExit('admin picks anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('patched betting.html')
