from pathlib import Path
import subprocess

BASE='533677dc2a39b6b9d75ceada48a372f5bf1569b3'
s=subprocess.check_output(['git','show',f'{BASE}:betting.html'],text=True)

# Remove delete from the bottom action row.
old_delete="out.push('<button class=\"ghost danger\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'cancelled\\')\">🗑 מחק טיקט</button>');"
if old_delete not in s:
    raise SystemExit('Expected bottom delete control was not found in base file')
s=s.replace(old_delete,'',1)

# Put a compact delete button beside the ticket status in admin -> all bets only.
old_status="<span class=\"betStatus '+st[1]+'\">'+st[0]+'</span>"
new_status="<div class=\"adminBetStatusActions\"><span class=\"betStatus '+st[1]+'\">'+st[0]+'</span><button class=\"ghost danger\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'cancelled\\')\">🗑 מחק</button></div>"
# There are status spans in multiple renderers. Target only renderAdminBet block.
start=s.find('function renderAdminBet(b){')
end=s.find('async function adminBetAction',start)
if start<0 or end<0:
    raise SystemExit('renderAdminBet block not found')
block=s[start:end]
if old_status not in block:
    raise SystemExit('Admin status span not found')
block=block.replace(old_status,new_status,1)
s=s[:start]+block+s[end:]

css_anchor='.adminBetTop{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}'
css_add=css_anchor+'.adminBetStatusActions{display:flex;align-items:center;gap:7px;flex-wrap:wrap}.adminBetStatusActions .danger{padding:6px 10px;font-size:12px;min-width:auto}'
if css_anchor not in s:
    raise SystemExit('CSS anchor not found')
s=s.replace(css_anchor,css_add,1)

# Guardrails: customer My Bets must not get admin delete controls.
my_start=s.find('function renderMyBets(rows){')
my_end=s.find('async function fetchImportedBet',my_start)
if my_start<0 or my_end<0:
    raise SystemExit('renderMyBets block not found')
my_block=s[my_start:my_end]
if "adminBetAction" in my_block or '🗑 מחק' in my_block:
    raise SystemExit('Delete button leaked into My Bets')
if '🗑 מחק</button>' not in s:
    raise SystemExit('Admin delete button missing')
if "cancelled:'למחוק את הטיקט" not in s:
    raise SystemExit('Cancelled confirmation missing')

Path('betting.html').write_text(s,encoding='utf-8')
print('Repaired betting.html and moved delete button beside admin status')
