from pathlib import Path

# betting.html
p=Path('betting.html')
s=p.read_text(encoding='utf-8')
old="""function adminBetButtons(b){let out=[];if(b.payment_status==='paid'){out.push('<button class=\"ghost adminActionPaid activeState\" type=\"button\" disabled>✅ שולם</button>');out.push('<button class=\"ghost\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'unpaid\\')\">↩ בטל תשלום</button>');const wonClass=b.result_status==='won'?' activeState':'';const lostClass=b.result_status==='lost'?' activeState':'';out.push('<button class=\"ghost adminActionWon'+wonClass+'\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'won\\')\">🏆 זכה</button>');out.push('<button class=\"ghost adminActionLost'+lostClass+'\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'lost\\')\">❌ הפסיד</button>');if(b.result_status!=='pending')out.push('<button class=\"ghost\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'result_pending\\')\">↩ בטל תוצאה</button>');if(b.result_status==='won'){if(b.prize_paid){out.push('<button class=\"ghost adminActionPrize activeState\" type=\"button\" disabled>✅ הלקוח קיבל את הכסף</button>');out.push('<button class=\"ghost\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'prize_unpaid\\')\">↩ בטל מסירת פרס</button>')}else out.push('<button class=\"ghost adminActionPrize\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'prize_paid\\')\">✅ הלקוח קיבל את הכסף</button>')}}else{out.push('<button class=\"ghost adminActionPaid\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'paid\\')\">💵 סמן כשולם</button>')}return out.join('')}"""
new="""function adminBetButtons(b){let out=[];if(b.payment_status==='paid'){out.push('<button class=\"ghost adminActionPaid activeState\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'unpaid\\')\">↩ בטל תשלום</button>');const wonClass=b.result_status==='won'?' adminResultWon':'';const lostClass=b.result_status==='lost'?' adminResultLost':'';out.push('<button class=\"ghost adminResultBtn'+wonClass+'\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'won\\')\">🏆 זכה</button>');out.push('<button class=\"ghost adminResultBtn'+lostClass+'\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'lost\\')\">❌ הפסיד</button>');if(b.result_status!=='pending')out.push('<button class=\"ghost\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'result_pending\\')\">↩ בטל תוצאה</button>');if(b.result_status==='won'){if(b.prize_paid){out.push('<button class=\"ghost adminActionPrize activeState\" type=\"button\" disabled>✅ הלקוח קיבל את הכסף</button>');out.push('<button class=\"ghost\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'prize_unpaid\\')\">↩ בטל מסירת פרס</button>')}else out.push('<button class=\"ghost adminActionPrize\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'prize_paid\\')\">✅ הלקוח קיבל את הכסף</button>')}}else{out.push('<button class=\"ghost adminActionPaid\" type=\"button\" onclick=\"adminBetAction(\\''+b.id+'\\',\\'paid\\')\">💵 סמן כשולם</button>')}return out.join('')}"""
if old not in s:
    raise SystemExit('adminBetButtons block not found')
s=s.replace(old,new,1)
css_old='.adminActionPaid{background:#0c3550;border-color:#2474a6}.adminActionWon{background:#087a4f;border-color:#14b875}.adminActionLost{background:#54191f;border-color:#8c2c36}.adminActionPrize'
css_new='.adminActionPaid{background:#0c3550;border-color:#2474a6}.adminResultBtn{background:#191919!important;border-color:#444!important;color:#fff}.adminResultWon{background:#087a4f!important;border-color:#14b875!important}.adminResultLost{background:#54191f!important;border-color:#8c2c36!important}.adminActionPrize'
if css_old not in s:
    raise SystemExit('result button CSS not found')
s=s.replace(css_old,css_new,1)
p.write_text(s,encoding='utf-8')

# index.html
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""actions=b.payment_status==='pending'&&b.result_status==='pending'?`<button class=\"main\" onclick=\"setWorkerBetStatus('${b.id}','paid')\">🟢 שולם / הפעל</button> <button class=\"danger\" onclick=\"deletePendingBet('${b.id}')\">🗑 מחק</button>`:b.payment_status==='paid'&&b.result_status==='pending'?`<button class=\"main\" onclick=\"setWorkerBetStatus('${b.id}','won')\">🏆 זכה</button> <button class=\"main\" onclick=\"setWorkerBetStatus('${b.id}','lost')\">❌ הפסיד</button>`:'';"""
new="""actions=(b.payment_status==='pending'&&b.result_status==='pending'?`<button class=\"main\" onclick=\"setWorkerBetStatus('${b.id}','paid')\">🟢 שולם / הפעל</button>`:b.payment_status==='paid'&&b.result_status==='pending'?`<button class=\"main\" onclick=\"setWorkerBetStatus('${b.id}','won')\">🏆 זכה</button> <button class=\"main\" onclick=\"setWorkerBetStatus('${b.id}','lost')\">❌ הפסיד</button>`:'')+` <button class=\"danger\" onclick=\"deleteSentBet('${b.id}')\">🗑 מחק</button>`;"""
if old not in s:
    raise SystemExit('worker bet actions block not found')
s=s.replace(old,new,1)
old_fn="""async function deletePendingBet(id){if(!await siteConfirm('למחוק את ההימור?'))return;try{await workerRequest('delete_pending_bet',{id});await loadWorkerBets();siteToast('ההימור נמחק')}catch(e){siteAlert(e.message,'שגיאה')}}"""
new_fn="""async function deletePendingBet(id){return deleteSentBet(id)}async function deleteSentBet(id){if(!await siteConfirm('למחוק את ההימור מרשימת ההימורים שנשלחו?','אישור מחיקה'))return;try{await workerRequest('update_bet_status',{id,status:'cancelled'});await loadWorkerBets();siteToast('ההימור נמחק מהרשימה')}catch(e){siteAlert(e.message,'שגיאה')}}"""
if old_fn not in s:
    raise SystemExit('deletePendingBet function not found')
s=s.replace(old_fn,new_fn,1)
p.write_text(s,encoding='utf-8')
print('Applied betting controls v2')
