from pathlib import Path
import re

# ---------- Shared modal helpers ----------
modal_css = r'''
/* REDBALL-SITE-MODAL-V1 */
.siteModalBackdrop{display:none;position:fixed;inset:0;z-index:5000;background:rgba(0,0,0,.78);padding:16px;align-items:center;justify-content:center}.siteModalBackdrop.show{display:flex}.siteModalBox{width:min(460px,100%);background:#111;border:1px solid #454545;border-radius:16px;padding:18px;text-align:right;box-shadow:0 20px 70px #000}.siteModalBox h3{margin:0 0 10px;color:#fff}.siteModalMessage{color:#ddd;line-height:1.6;white-space:pre-line}.siteModalInput{width:100%;margin-top:12px;background:#181818;color:#fff;border:1px solid #555;border-radius:9px;padding:12px;font-size:16px}.siteModalActions{display:flex;gap:9px;margin-top:16px}.siteModalActions button{flex:1}.siteToast{position:fixed;z-index:5100;left:50%;bottom:24px;transform:translate(-50%,20px);background:#111;border:1px solid #444;border-radius:12px;padding:11px 16px;opacity:0;pointer-events:none;transition:.2s;max-width:min(90vw,520px);box-shadow:0 10px 35px #000}.siteToast.show{opacity:1;transform:translate(-50%,0)}.siteToast.success{border-color:#2e8b68;color:#62e6a7}.siteToast.error{border-color:#8c2c36;color:#ff7b86}
'''

modal_html = r'''<div id="siteModal" class="siteModalBackdrop" aria-hidden="true"><div class="siteModalBox" role="dialog" aria-modal="true"><h3 id="siteModalTitle">הודעה</h3><div id="siteModalMessage" class="siteModalMessage"></div><input id="siteModalInput" class="siteModalInput" style="display:none"><div class="siteModalActions"><button id="siteModalCancel" class="secondary ghost" type="button">ביטול</button><button id="siteModalOk" class="main primary" type="button">אישור</button></div></div></div><div id="siteToast" class="siteToast"></div>'''

modal_js = r'''
function siteModal({title='הודעה',message='',confirmText='אישור',cancelText='ביטול',showCancel=false,input=false,inputType='text',inputValue='',placeholder='' }={}){return new Promise(resolve=>{const m=document.getElementById('siteModal'),ttl=document.getElementById('siteModalTitle'),msg=document.getElementById('siteModalMessage'),inp=document.getElementById('siteModalInput'),ok=document.getElementById('siteModalOk'),cancel=document.getElementById('siteModalCancel');ttl.textContent=title;msg.textContent=message;ok.textContent=confirmText;cancel.textContent=cancelText;cancel.style.display=showCancel?'block':'none';inp.style.display=input?'block':'none';inp.type=inputType;inp.value=inputValue;inp.placeholder=placeholder;m.classList.add('show');m.setAttribute('aria-hidden','false');let done=false;const finish=v=>{if(done)return;done=true;m.classList.remove('show');m.setAttribute('aria-hidden','true');ok.onclick=null;cancel.onclick=null;m.onclick=null;document.removeEventListener('keydown',key);resolve(v)};const key=e=>{if(e.key==='Escape')finish(input?null:false);if(e.key==='Enter'&&(!input||document.activeElement===inp))finish(input?inp.value:true)};ok.onclick=()=>finish(input?inp.value:true);cancel.onclick=()=>finish(input?null:false);m.onclick=e=>{if(e.target===m&&showCancel)finish(input?null:false)};document.addEventListener('keydown',key);setTimeout(()=>input?inp.focus():ok.focus(),30)})}
function siteAlert(message,title='הודעה'){return siteModal({title,message,confirmText:'סגור'})}
function siteConfirm(message,title='אישור פעולה'){return siteModal({title,message,confirmText:'כן, אישור',cancelText:'ביטול',showCancel:true})}
function sitePrompt(message,{title='הזנת פרטים',type='text',placeholder='',value=''}={}){return siteModal({title,message,confirmText:'שמור',cancelText:'ביטול',showCancel:true,input:true,inputType:type,inputValue:value,placeholder})}
function siteToast(message,type='success'){const t=document.getElementById('siteToast');t.textContent=message;t.className='siteToast '+type+' show';clearTimeout(siteToast._t);siteToast._t=setTimeout(()=>t.classList.remove('show'),2200)}
'''

# ---------- betting.html ----------
p=Path('betting.html')
s=p.read_text(encoding='utf-8')
if 'REDBALL-SITE-MODAL-V1' not in s:
    s=s.replace('</style>', modal_css+'\n</style>',1)
    s=s.replace('<div id="ticketBackdrop"', modal_html+'\n<div id="ticketBackdrop"',1)
    s=s.replace('<script>\nif(window.top!==window.self)', '<script>\n'+modal_js+'\nif(window.top!==window.self)',1)

s=s.replace('ADMIN_URL=SB_URL+"/functions/v1/redball-admin",PUBLIC_URL=', 'ADMIN_URL=SB_URL+"/functions/v1/redball-admin",BETS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-bets",PUBLIC_URL=',1)

# add bet-admin request helper if absent
if 'async function adminBetReq(' not in s:
    anchor='async function adminReq(action,payload={},auth=true)'
    idx=s.find(anchor)
    if idx<0: raise SystemExit('betting adminReq anchor not found')
    helper='''async function adminBetReq(action,payload={}){const h={"Content-Type":"application/json","apikey":KEY};if(adminToken)h["x-admin-token"]=adminToken;const res=await fetch(BETS_ADMIN_URL,{method:"POST",headers:h,body:JSON.stringify({action,...payload})});let d={};try{d=await res.json()}catch(e){}if(!res.ok){if(res.status===401){adminToken="";sessionStorage.removeItem("redball_betting_admin")}throw new Error(d.error||"שגיאה")}return d}\n'''
    s=s[:idx]+helper+s[idx:]

# Replace admin bet control block completely
start=s.find('function adminBetButtons(b){')
end=s.find('$("#refreshAdminBets").onclick=adminAllBets;',start)
if start<0 or end<0: raise SystemExit('bet control block not found')
end += len('$("#refreshAdminBets").onclick=adminAllBets;')
new_block=r'''function adminBetButtons(b){let out=[];if(b.payment_status==='paid'){out.push('<button class="ghost adminActionPaid activeState" type="button" disabled>✅ שולם</button>');out.push('<button class="ghost" type="button" onclick="adminBetAction(\''+b.id+'\',\'unpaid\')">↩ בטל תשלום</button>');const wonClass=b.result_status==='won'?' activeState':'';const lostClass=b.result_status==='lost'?' activeState':'';out.push('<button class="ghost adminActionWon'+wonClass+'" type="button" onclick="adminBetAction(\''+b.id+'\',\'won\')">🏆 זכה</button>');out.push('<button class="ghost adminActionLost'+lostClass+'" type="button" onclick="adminBetAction(\''+b.id+'\',\'lost\')">❌ הפסיד</button>');if(b.result_status!=='pending')out.push('<button class="ghost" type="button" onclick="adminBetAction(\''+b.id+'\',\'result_pending\')">↩ בטל תוצאה</button>');if(b.result_status==='won'){if(b.prize_paid){out.push('<button class="ghost adminActionPrize activeState" type="button" disabled>✅ הלקוח קיבל את הכסף</button>');out.push('<button class="ghost" type="button" onclick="adminBetAction(\''+b.id+'\',\'prize_unpaid\')">↩ בטל מסירת פרס</button>')}else out.push('<button class="ghost adminActionPrize" type="button" onclick="adminBetAction(\''+b.id+'\',\'prize_paid\')">✅ הלקוח קיבל את הכסף</button>')}}else{out.push('<button class="ghost adminActionPaid" type="button" onclick="adminBetAction(\''+b.id+'\',\'paid\')">💵 סמן כשולם</button>')}return out.join('')}
function renderAdminBet(b){const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[];return '<article class="adminBet" data-bet-id="'+b.id+'"><div class="adminBetTop"><div><b class="betCode">'+esc(b.bet_code)+'</b><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div><span class="betStatus '+st[1]+'">'+st[0]+'</span></div><div class="adminBetMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס<b>'+Number(b.total_odd||0).toFixed(2)+'</b></div><div>זכייה<b>'+money(b.potential_win)+'</b></div><div>שולם ע״י<b>'+(b.paid_by?esc(b.paid_by):'-')+'</b></div></div><div class="adminBetPicks">'+picks.map(p=>esc((p.g||'')+' • '+(p.l||''))).join('<br>')+'</div><div class="adminBetControls">'+adminBetButtons(b)+'</div>'+(b.prize_paid_at?'<div class="small" style="margin-top:7px">מסירת פרס: '+fmtDate(b.prize_paid_at)+(b.prize_paid_by?' • '+esc(b.prize_paid_by):'')+'</div>':'')+'</article>'}
async function adminBetAction(id,status){const labels={paid:'לסמן את הטיקט כשולם?',unpaid:'לבטל את סימון התשלום? פעולה זו גם תחזיר את התוצאה למצב ממתין.',won:'לסמן את הטיקט כזוכה?',lost:'לסמן את הטיקט כמפסיד?',result_pending:'לבטל את התוצאה ולהחזיר למצב ממתין?',prize_paid:'לאשר שהלקוח קיבל את כספי הזכייה?',prize_unpaid:'לבטל את סימון מסירת הפרס?'};if(!await siteConfirm(labels[status]||'לאשר פעולה?'))return;const card=document.querySelector('.adminBet[data-bet-id="'+id+'"]');if(card)card.style.opacity='.55';try{const d=await adminBetReq("update_bet_status",{id,status});if(card&&d.bet)card.outerHTML=renderAdminBet(d.bet);else await adminAllBets(false);siteToast('הטיקט עודכן בהצלחה');if($("#minePage").classList.contains("activePage"))loadMyBets()}catch(e){if(card)card.style.opacity='1';await siteAlert("לא ניתן לעדכן את הטיקט: "+e.message,'שגיאה')}}
async function adminAllBets(showLoading=true){const box=$("#adminBets"),btn=$("#refreshAdminBets");const old=btn?btn.textContent:'';if(showLoading&&!box.children.length)box.innerHTML='<div class="muted">טוען...</div>';if(btn){btn.disabled=true;btn.textContent='מרענן...'}try{const d=await adminReq("list_bets"),rows=d.bets||[];box.innerHTML=rows.length?rows.map(renderAdminBet).join(''):'<div class="muted">אין הימורים במאגר</div>'}catch(e){if(!box.children.length)box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>';else siteToast('שגיאה ברענון ההימורים','error')}finally{if(btn){btn.disabled=false;btn.textContent=old||'🔄 רענן'}}}
$("#refreshAdminBets").onclick=()=>adminAllBets(false);'''
s=s[:start]+new_block+s[end:]

# active state style
s=s.replace('.adminPrizeDone{display:inline-block', '.activeState{box-shadow:0 0 0 2px rgba(110,216,255,.45) inset;filter:brightness(1.18)}.adminPrizeDone{display:inline-block',1)

# Native popups in betting -> site modals
s=s.replace('alert("לא ניתן לעדכן מחזור: "+e.message)', 'siteAlert("לא ניתן לעדכן מחזור: "+e.message,"שגיאה")')
s=s.replace('alert("היחסים עודכנו")', 'siteToast("היחסים עודכנו")')
s=s.replace('alert("לא ניתן לעדכן: "+e.message)', 'siteAlert("לא ניתן לעדכן: "+e.message,"שגיאה")')
s=s.replace('if(confirm("למחוק את המשחק?")){try{await adminReq("delete_betting_game",{id:b.dataset.id});await adminGames();await load()}catch(e){alert(e.message)}}', 'if(await siteConfirm("למחוק את המשחק?")){try{await adminReq("delete_betting_game",{id:b.dataset.id});await adminGames();await load();siteToast("המשחק נמחק")}catch(e){siteAlert(e.message,"שגיאה")}}')

p.write_text(s,encoding='utf-8')

# ---------- index.html ----------
p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'REDBALL-SITE-MODAL-V1' not in s:
    s=s.replace('</style></head>', modal_css+'\n</style></head>',1)
    s=s.replace('<script>', modal_html+'\n<script>',1)
    s=s.replace('<script>\n', '<script>\n'+modal_js+'\n',1)

# exact native popup replacements
s=s.replace("async function switchEmployee(){if(hasItems()&&!confirm('יש הזמנה פעילה. לעבור עובד?'))return;", "async function switchEmployee(){if(hasItems()&&!await siteConfirm('יש הזמנה פעילה. לעבור עובד?'))return;")
s=s.replace("function resetAll(skip=false){if(!skip&&hasItems()&&!confirm('לאפס את ההזמנה?'))return;", "async function resetAll(skip=false){if(!skip&&hasItems()&&!await siteConfirm('לאפס את ההזמנה?'))return;")
s=s.replace("if(orderSaveInProgress||!hasItems())return alert('אין פריטים בהזמנה');", "if(orderSaveInProgress||!hasItems())return siteAlert('אין פריטים בהזמנה');")
s=s.replace("alert('ההזמנה נשמרה בצורה מאובטחת ✅\\\nסה\"כ שאושר בשרת: '+d.total)", "await siteAlert('ההזמנה נשמרה בצורה מאובטחת ✅\\nסה\"כ שאושר בשרת: '+d.total,'הצלחה')")
s=s.replace("alert('המכירה לא נשמרה: '+e.message)", "await siteAlert('המכירה לא נשמרה: '+e.message,'שגיאה')")
s=s.replace("function copyOrder(){const s=getCartItemsArray().map(i=>i.name+' x'+i.qty).join(', ');if(!s)return alert('אין פריטים');navigator.clipboard.writeText(s);alert('הקבלה הועתקה')}", "async function copyOrder(){const s=getCartItemsArray().map(i=>i.name+' x'+i.qty).join(', ');if(!s)return siteAlert('אין פריטים');try{await navigator.clipboard.writeText(s);siteToast('הקבלה הועתקה')}catch(e){siteAlert('לא ניתן להעתיק את הקבלה','שגיאה')}}")

# employee/admin functions wholesale
pat=r"async function addEmployee\(\)\{.*?\}async function setEmployeePin\(name\)\{.*?\}async function deleteEmployeeByName\(name\)\{.*?\}async function changeAdminPassword\(\)\{.*?\}\n\nconst securityLabels="
m=re.search(pat,s,flags=re.S)
if not m: raise SystemExit('employee popup function block not found')
rep=r'''async function addEmployee(){const name=document.getElementById('newEmployeeName').value.trim(),pin=document.getElementById('newEmployeePin').value.trim();if(!name||!/^\d{4,8}$/.test(pin))return siteAlert('צריך שם ו-PIN של 4–8 ספרות','שגיאה');try{await adminRequest('add_employee',{name,pin});document.getElementById('newEmployeeName').value='';document.getElementById('newEmployeePin').value='';await loadEmployees();await loadEmployeeManager();siteToast('העובד נוסף עם PIN ✅')}catch(e){siteAlert(e.message,'שגיאה')}}async function setEmployeePin(name){const pin=await sitePrompt('PIN חדש ל-'+name+' (4–8 ספרות):',{title:'שינוי PIN',type:'password',placeholder:'4–8 ספרות'});if(pin===null)return;if(!/^\d{4,8}$/.test(pin))return siteAlert('PIN חייב להכיל 4–8 ספרות','שגיאה');try{await adminRequest('set_employee_pin',{name,pin});await loadEmployeeManager();siteAlert('ה-PIN עודכן וכל החיבורים הישנים של העובד נותקו ✅','הצלחה')}catch(e){siteAlert(e.message,'שגיאה')}}async function deleteEmployeeByName(name){if(!await siteConfirm('למחוק את '+name+'?'))return;try{await adminRequest('delete_employee',{name});await loadEmployees();await loadEmployeeManager();siteToast('העובד נמחק')}catch(e){siteAlert(e.message,'שגיאה')}}async function changeAdminPassword(){const p=await sitePrompt('סיסמה חדשה (לפחות 10 תווים):',{title:'שינוי סיסמת מנהל',type:'password'});if(p===null)return;if(p.length<10)return siteAlert('הסיסמה חייבת להכיל לפחות 10 תווים','שגיאה');try{await adminRequest('change_password',{newPassword:p});siteAlert('הסיסמה שונתה ✅','הצלחה')}catch(e){siteAlert(e.message,'שגיאה')}}

const securityLabels='''
s=s[:m.start()]+rep+s[m.end():]

s=s.replace("}catch(e){alert(e.message)}}async function deleteOrder(id){if(!confirm('למחוק?'))return;try{await adminRequest('delete_order',{id});await loadOrders()}catch(e){alert(e.message)}}", "}catch(e){siteAlert(e.message,'שגיאה')}}async function deleteOrder(id){if(!await siteConfirm('למחוק את ההזמנה?'))return;try{await adminRequest('delete_order',{id});await loadOrders();siteToast('ההזמנה נמחקה')}catch(e){siteAlert(e.message,'שגיאה')}}")
s=s.replace("async function setWorkerBetStatus(id,status){try{await workerRequest('update_bet_status',{id,status});await loadWorkerBets()}catch(e){alert(e.message)}}async function deletePendingBet(id){if(!confirm('למחוק את ההימור?'))return;try{await workerRequest('delete_pending_bet',{id});await loadWorkerBets()}catch(e){alert(e.message)}}", "async function setWorkerBetStatus(id,status){try{await workerRequest('update_bet_status',{id,status});await loadWorkerBets()}catch(e){siteAlert(e.message,'שגיאה')}}async function deletePendingBet(id){if(!await siteConfirm('למחוק את ההימור?'))return;try{await workerRequest('delete_pending_bet',{id});await loadWorkerBets();siteToast('ההימור נמחק')}catch(e){siteAlert(e.message,'שגיאה')}}")

# Final safety: no browser-native popup calls should remain in either page
p.write_text(s,encoding='utf-8')

for fname in ('betting.html','index.html'):
    txt=Path(fname).read_text(encoding='utf-8')
    leftovers=[]
    for token in ('alert(', 'confirm(', 'prompt('):
        if token in txt:leftovers.append(token)
    if leftovers:
        raise SystemExit(f'{fname}: native popup calls remain: {leftovers}')
print('Unified site modals + reversible bet controls applied successfully')
