from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')
marker='RED-BALL-STAGE4-SECURITY-DASHBOARD'
if marker in s:
    print('Stage 4 dashboard already applied')
    raise SystemExit(0)

css='''\n/* RED-BALL-STAGE4-SECURITY-DASHBOARD */\n.securityPanel{background:#0d1117;border:1px solid #334155;border-radius:14px;padding:15px;margin:18px 0}.securityHeader{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}.securityHeader h2{margin:0}.securityStats{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:14px 0}.securityStat{background:#111827;border:1px solid #293548;border-radius:11px;padding:12px;text-align:center}.securityStat .securityNum{display:block;font-size:23px;font-weight:700;color:#6ed8ff;margin-top:5px}.securityStatus{font-weight:700;padding:7px 11px;border-radius:999px;display:inline-block}.securityStatus.ok{background:rgba(20,150,90,.16);color:#62e6a7}.securityStatus.warning{background:rgba(255,166,0,.14);color:#ffb143}.securityStatus.critical{background:rgba(255,70,85,.14);color:#ff6672}.securityEvents{display:grid;gap:7px;margin-top:10px;max-height:430px;overflow:auto}.securityEvent{display:grid;grid-template-columns:150px 100px minmax(160px,1fr) minmax(120px,.7fr);gap:8px;align-items:center;background:#111;border:1px solid #2b2b2b;border-radius:9px;padding:9px;font-size:12px}.securitySeverity{font-weight:700}.securitySeverity.warn{color:#ffb143}.securitySeverity.high,.securitySeverity.critical{color:#ff6672}.securityEmpty{padding:18px;text-align:center;opacity:.7}\n'''
needle='@media(max-width:900px)'
if needle not in s: raise SystemExit('CSS insertion point not found')
s=s.replace(needle,css+needle,1)
# mobile css append inside existing max-width 700 by simple before </style>
s=s.replace('</style></head>','@media(max-width:700px){.securityStats{grid-template-columns:1fr 1fr}.securityEvent{grid-template-columns:1fr}.securityEvent>span{display:block}}\n</style></head>',1)

old="const SUPABASE_URL='https://eqtgyxabuosyinnhairr.supabase.co',SUPABASE_ANON_KEY='sb_publishable_NGc9M7HpJ4biIkTLSys-nw_qj1N2ZtA',ADMIN_FUNCTION_URL=SUPABASE_URL+'/functions/v1/redball-admin',PUBLIC_FUNCTION_URL=SUPABASE_URL+'/functions/v1/redball-public';"
new="const SUPABASE_URL='https://eqtgyxabuosyinnhairr.supabase.co',SUPABASE_ANON_KEY='sb_publishable_NGc9M7HpJ4biIkTLSys-nw_qj1N2ZtA',ADMIN_FUNCTION_URL=SUPABASE_URL+'/functions/v1/redball-admin',PUBLIC_FUNCTION_URL=SUPABASE_URL+'/functions/v1/redball-public',SECURITY_FUNCTION_URL=SUPABASE_URL+'/functions/v1/redball-security';"
if old not in s: raise SystemExit('constant line not found')
s=s.replace(old,new,1)

logout='<button class="danger" onclick="adminLogout()">🔒 יציאה מאובטחת</button>'
if logout not in s: raise SystemExit('admin logout button not found')
s=s.replace(logout,'<button id="securityToggleBtn" class="secondary" onclick="toggleSecurityPanel()">🛡️ אבטחה</button>'+logout,1)

panel='''<div id="securityPanel" class="securityPanel hidden"><div class="securityHeader"><div><h2>🛡️ מרכז אבטחה</h2><div style="font-size:12px;opacity:.7;margin-top:4px">ניטור משותף לקופה ולאתר ההימורים · נשמרים 90 יום</div></div><div><span id="securityStatus" class="securityStatus ok">טוען...</span><button class="secondary" onclick="loadSecurityPanel()">🔄 רענן</button></div></div><div class="securityStats"><div class="securityStat">אירועים 24 שעות<span id="secEvents24" class="securityNum">-</span></div><div class="securityStat">כניסות כושלות<span id="secFailed24" class="securityNum">-</span></div><div class="securityStat">חסימות<span id="secBlocks24" class="securityNum">-</span></div><div class="securityStat">שינויים רגישים<span id="secSensitive24" class="securityNum">-</span></div><div class="securityStat">HIGH / CRITICAL<span id="secHigh24" class="securityNum">-</span></div></div><div id="securityLoadMsg" style="font-size:12px;min-height:18px"></div><h3>אירועי אבטחה אחרונים</h3><div id="securityEvents" class="securityEvents"><div class="securityEmpty">טוען...</div></div></div>'''
filters='<div class="filters">'
if filters not in s: raise SystemExit('filters insertion point not found')
s=s.replace(filters,panel+filters,1)

js='''\nconst securityLabels={admin_login_failed:'ניסיון סיסמת מנהל שגויה',worker_pin_failed:'PIN עובד שגוי',rate_limit_blocked:'חסימת Rate Limit',admin_session_created:'כניסת מנהל',admin_session_ended:'סיום חיבור מנהל',worker_session_created:'כניסת עובד',worker_session_ended:'סיום חיבור עובד',admin_password_changed:'שינוי סיסמת מנהל',worker_pin_created:'הגדרת PIN עובד',worker_pin_changed:'שינוי PIN עובד',worker_pin_deleted:'מחיקת PIN עובד',employee_created:'הוספת עובד',employee_deleted:'מחיקת עובד',bet_status_changed:'שינוי סטטוס הימור',betting_round_changed:'שינוי מחזור הימורים',betting_game_insert:'הוספת משחק',betting_game_update:'עדכון משחק/יחסים',betting_game_delete:'מחיקת משחק',order_update:'עריכת הזמנה',order_delete:'מחיקת הזמנה'};\nasync function securityRequest(action='summary',payload={}){if(!adminToken)throw new Error('אין חיבור מנהל פעיל');const r=await fetch(SECURITY_FUNCTION_URL,{method:'POST',headers:{'Content-Type':'application/json','apikey':SUPABASE_ANON_KEY,'x-admin-token':adminToken},body:JSON.stringify({action,...payload})});let d={};try{d=await r.json()}catch(e){}if(r.status===401){adminToken='';sessionStorage.removeItem('redball_admin_token');throw new Error('פג תוקף חיבור המנהל')}if(!r.ok)throw new Error(d.error||'שגיאה בטעינת נתוני אבטחה');return d}\nfunction toggleSecurityPanel(){const p=document.getElementById('securityPanel');const opening=p.classList.contains('hidden');p.classList.toggle('hidden');if(opening)loadSecurityPanel()}\nfunction securityDetails(e){const d=e.details||{};if(e.event_type==='bet_status_changed')return (d.bet_code||'')+' '+(d.new_payment_status||'')+' '+(d.new_result_status||'');if(e.event_type.startsWith('betting_game_'))return (d.home_team||'')+' - '+(d.away_team||'');if(e.event_type==='betting_round_changed')return 'מחזור '+(d.round_no??'')+' '+(d.is_open?'פתוח':'נעול');if(e.event_type.startsWith('order_'))return 'הזמנה '+String(d.id||'').slice(0,8);if(e.event_type==='rate_limit_blocked')return 'נחסם מקור לאחר חריגה מהמגבלה';return e.actor_identifier||''}\nasync function loadSecurityPanel(){const msg=document.getElementById('securityLoadMsg'),box=document.getElementById('securityEvents');msg.textContent='טוען נתוני אבטחה...';try{const d=await securityRequest('summary'),c=d.counts||{};document.getElementById('secEvents24').textContent=c.last24??0;document.getElementById('secFailed24').textContent=c.failedLogins24h??0;document.getElementById('secBlocks24').textContent=c.rateBlocks24h??0;document.getElementById('secSensitive24').textContent=c.sensitiveChanges24h??0;document.getElementById('secHigh24').textContent=(c.high24h??0)+(c.critical24h??0);const st=document.getElementById('securityStatus');st.className='securityStatus '+(d.status||'ok');st.textContent=d.status==='critical'?'🔴 קריטי':d.status==='warning'?'🟠 דורש בדיקה':'🟢 תקין';const rows=d.recent||[];box.innerHTML=rows.length?rows.slice(0,60).map(e=>`<div class="securityEvent"><span>${escapeHtml(formatDate(e.created_at))}</span><span class="securitySeverity ${escapeHtml(e.severity)}">${escapeHtml(String(e.severity||'').toUpperCase())}</span><span><b>${escapeHtml(securityLabels[e.event_type]||e.event_type)}</b></span><span>${escapeHtml(securityDetails(e))}</span></div>`).join(''):'<div class="securityEmpty">אין אירועי אבטחה בתקופה האחרונה</div>';msg.textContent='עודכן: '+new Date().toLocaleTimeString('he-IL')}catch(e){msg.textContent='שגיאה: '+e.message;box.innerHTML='<div class="securityEmpty">לא ניתן לטעון את מרכז האבטחה</div>'}}\n'''
insert='async function loadOrders(){'
if insert not in s: raise SystemExit('JS insertion point not found')
s=s.replace(insert,js+insert,1)

# Ensure logout hides the security panel
old_logout="document.getElementById('adminPasswordInput').value='';backToPosOrLogin()"
new_logout="document.getElementById('adminPasswordInput').value='';document.getElementById('securityPanel')?.classList.add('hidden');backToPosOrLogin()"
if old_logout in s:s=s.replace(old_logout,new_logout,1)

path.write_text(s,encoding='utf-8')
print('Stage 4 security dashboard applied')
