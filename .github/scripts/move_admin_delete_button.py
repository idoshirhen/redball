from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

start=s.find('function adminBetButtons(b){')
end=s.find('function renderAdminBet(b){',start)
if start<0 or end<0:
    raise SystemExit('adminBetButtons/renderAdminBet block not found')

buttons=s[start:end]
buttons=buttons.replace("out.push('<button class=\"ghost danger\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'cancelled\\')\">🗑 מחק טיקט</button>');","")
s=s[:start]+buttons+s[end:]

old="<span class=\"betStatus '+st[1]+'\">'+st[0]+'</span>"
new="<div style=\"display:flex;align-items:center;gap:7px;flex-wrap:wrap\"><span class=\"betStatus '+st[1]+'\">'+st[0]+'</span><button class=\"ghost danger\" type=\"button\" style=\"padding:6px 10px;font-size:12px\" onclick=\"adminBetAction('"+"\\''+b.id+'\\',\\'cancelled\\')\""+">🗑 מחק</button></div>"
if old not in s:
    raise SystemExit('status span anchor not found')
s=s.replace(old,new,1)

if '🗑 מחק טיקט' in s:
    raise SystemExit('old delete label still exists')
if '🗑 מחק</button>' not in s:
    raise SystemExit('new delete button not found')

p.write_text(s,encoding='utf-8')
print('moved admin delete button next to status')
