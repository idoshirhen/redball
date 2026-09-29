from pathlib import Path
import re

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

start=s.find('function adminBetButtons(b){')
end=s.find('function renderAdminBet(b){',start)
if start<0 or end<0:
    raise SystemExit('adminBetButtons block not found')

new_fn=r'''function adminBetButtons(b){let out=[];if(b.payment_status==='paid'){out.push('<button class="ghost adminActionPaid" type="button" onclick="adminBetAction(\''+b.id+'\',\'unpaid\')">↩ בטל תשלום</button>');const wonClass=b.result_status==='won'?' adminResultWon':'';const lostClass=b.result_status==='lost'?' adminResultLost':'';out.push('<button class="ghost adminResultBtn'+wonClass+'" type="button" onclick="adminBetAction(\''+b.id+'\',\'won\')">🏆 זכה</button>');out.push('<button class="ghost adminResultBtn'+lostClass+'" type="button" onclick="adminBetAction(\''+b.id+'\',\'lost\')">❌ הפסיד</button>');if(b.result_status!=='pending')out.push('<button class="ghost" type="button" onclick="adminBetAction(\''+b.id+'\',\'result_pending\')">↩ בטל תוצאה</button>');if(b.result_status==='won'){if(b.prize_paid){out.push('<button class="ghost adminActionPrize activeState" type="button" disabled>✅ הלקוח קיבל את הכסף</button>');out.push('<button class="ghost" type="button" onclick="adminBetAction(\''+b.id+'\',\'prize_unpaid\')">↩ בטל מסירת פרס</button>')}else out.push('<button class="ghost adminActionPrize" type="button" onclick="adminBetAction(\''+b.id+'\',\'prize_paid\')">✅ הלקוח קיבל את הכסף</button>')}}else{out.push('<button class="ghost adminActionPaid" type="button" onclick="adminBetAction(\''+b.id+'\',\'paid\')">💵 סמן כשולם</button>')}out.push('<button class="ghost danger" type="button" onclick="adminBetAction(\''+b.id+'\',\'cancelled\')">🗑 מחק טיקט</button>');return out.join('')}
'''
s=s[:start]+new_fn+s[end:]

# add cancelled confirmation label
s=s.replace("prize_unpaid:'לבטל את סימון מסירת הפרס?'", "prize_unpaid:'לבטל את סימון מסירת הפרס?',cancelled:'למחוק את הטיקט מהרשימה? הפעולה תסמן אותו כמבוטל ותשמור היסטוריה.'",1)

# replace post-update render logic so cancelled removes only the card
old="if(card&&d.bet)card.outerHTML=renderAdminBet(d.bet);else await adminAllBets(false);siteToast('הטיקט עודכן בהצלחה')"
new="if(status==='cancelled'&&card){card.remove();siteToast('הטיקט נמחק מהרשימה')}else{if(card&&d.bet)card.outerHTML=renderAdminBet(d.bet);else await adminAllBets(false);siteToast('הטיקט עודכן בהצלחה')}"
if old not in s:
    raise SystemExit('adminBetAction render anchor not found')
s=s.replace(old,new,1)

# hide cancelled bets from all-bets list
old2='const d=await adminReq("list_bets"),rows=d.bets||[];box.innerHTML=rows.length?rows.map(renderAdminBet).join(\'\'):'
new2='const d=await adminReq("list_bets"),rows=(d.bets||[]).filter(b=>b.result_status!=="cancelled");box.innerHTML=rows.length?rows.map(renderAdminBet).join(\'\'):'
if old2 not in s:
    raise SystemExit('adminAllBets rows anchor not found')
s=s.replace(old2,new2,1)

# validation
if '🗑 מחק טיקט' not in s or "status==='cancelled'" not in s:
    raise SystemExit('delete control validation failed')

p.write_text(s,encoding='utf-8')
print('patched betting.html admin delete control')
