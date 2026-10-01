from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')
MARK='REDBALL-ADMIN-ROLES-V1'
if MARK in s:
    raise SystemExit('patch already applied')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' anchor not found')
    s=s.replace(old,new,1)

# CSS for role selector and restricted tabs.
css='''\n/* REDBALL-ADMIN-ROLES-V1 */\n.adminRoleChoices{display:grid;grid-template-columns:1fr;gap:8px;margin:12px 0}.adminRoleChoice{width:100%;text-align:right;background:#171717;color:#ddd;border:1px solid #3b3b3b;border-radius:11px;padding:12px 14px;cursor:pointer;font-weight:800}.adminRoleChoice:hover{border-color:#6ed8ff}.adminRoleChoice.selected{border-color:#ff4de1;background:linear-gradient(180deg,rgba(255,77,225,.25),rgba(110,216,255,.10));color:#fff}.adminRoleChoice small{display:block;color:#888;font-weight:500;margin-top:3px}.adminRoleChoice.selected small{color:#bbb}.adminIdentity{margin:7px 0 0;color:#6ed8ff;font-weight:800}.adminTabBtn.roleHidden,.adminRoleRestricted{display:none!important}\n'''
replace_once('</style>',css+'</style>','style')

# Admin identity under title.
replace_once('<section id="adminPage" class="page"><div class="pageTitle"><h1>ניהול ההימורים</h1><p>ניהול סשנים, משחקים וטפסים</p><button id="adminLogoutBtn"',
             '<section id="adminPage" class="page"><div class="pageTitle"><h1>ניהול ההימורים</h1><p>ניהול סשנים, משחקים וטפסים</p><div id="adminIdentity" class="adminIdentity"></div><button id="adminLogoutBtn"',
             'admin identity')

# Login modal: choose user first, then password.
old_modal='<div id="adminLoginModal" class="loginBackdrop"><div class="loginBox"><div class="loginHead"><h2>🔐 כניסת מנהל</h2><button id="closeAdminLogin" class="closeBtn" type="button">✕</button></div><label>סיסמת מנהל</label><input id="adminPass" type="password" autocomplete="current-password"><button class="primary" id="adminLoginBtn" type="button">כניסה לניהול</button><p id="adminLoginMsg" class="statusMsg"></p></div></div>'
new_modal='''<div id="adminLoginModal" class="loginBackdrop"><div class="loginBox"><div class="loginHead"><h2>🔐 כניסה לניהול הימורים</h2><button id="closeAdminLogin" class="closeBtn" type="button">✕</button></div><div class="small">בחר משתמש:</div><div class="adminRoleChoices"><button class="adminRoleChoice" type="button" data-admin-role="sani">Sani - מנכ״ל<small>גישה מלאה</small></button><button class="adminRoleChoice" type="button" data-admin-role="vladi">Vladi - סמנכ״ל<small>גישה מלאה</small></button><button class="adminRoleChoice" type="button" data-admin-role="betzi">Betzi - אחראי עובדים<small>ניהול סשנים, כל ההימורים וארכיון משחקים</small></button></div><label>סיסמה</label><input id="adminPass" type="password" autocomplete="current-password"><button class="primary" id="adminLoginBtn" type="button">כניסה לניהול</button><p id="adminLoginMsg" class="statusMsg"></p></div></div>'''
replace_once(old_modal,new_modal,'login modal')

# Add client-side role state next to token.
old_state='let games=[],rounds=[],activeRound=2,adminToken=sessionStorage.getItem("redball_betting_admin_v2")||"";'
new_state='let games=[],rounds=[],activeRound=2,adminToken=sessionStorage.getItem("redball_betting_admin_v2")||"",adminRole=sessionStorage.getItem("redball_betting_admin_role")||"",pendingAdminRole="";'
replace_once(old_state,new_state,'admin state')

# Replace admin opening flow; existing sessions are resolved with whoami.
old_open='function openAdmin(){if(adminToken){showPage("admin");showAdminTab("rounds")}else{$("#adminLoginModal").classList.add("show");setTimeout(()=>$("#adminPass").focus(),40)}}$("#adminNav").onclick=openAdmin;'
new_open='''function roleDisplayName(role){return role==="sani"?"Sani - מנכ״ל":role==="vladi"?"Vladi - סמנכ״ל":role==="betzi"?"Betzi - אחראי עובדים":""}function applyAdminPermissions(){const limited=adminRole==="betzi";document.querySelectorAll(".adminTabBtn").forEach(b=>{const restricted=["add","games"].includes(b.dataset.adminTab);b.classList.toggle("roleHidden",limited&&restricted)});const tabs=$(".adminTabs"),visible=[...document.querySelectorAll(".adminTabBtn:not(.roleHidden)")].length;if(tabs)tabs.style.gridTemplateColumns="repeat("+Math.max(1,visible)+",1fr)";const elo=$("#refreshEloOdds");if(elo)elo.classList.toggle("adminRoleRestricted",limited);const id=$("#adminIdentity");if(id)id.textContent=roleDisplayName(adminRole)}async function resolveAdminRole(){if(!adminToken)return false;try{const d=await adminReq("whoami");adminRole=d.role||"";sessionStorage.setItem("redball_betting_admin_role",adminRole);applyAdminPermissions();return true}catch(e){adminToken="";adminRole="";sessionStorage.removeItem("redball_betting_admin_v2");sessionStorage.removeItem("redball_betting_admin_role");return false}}function showAdminLogin(){pendingAdminRole="";document.querySelectorAll(".adminRoleChoice").forEach(b=>b.classList.remove("selected"));$("#adminPass").value="";$("#adminLoginMsg").textContent="";$("#adminLoginModal").classList.add("show")}async function openAdmin(){if(adminToken){if(!adminRole&&!(await resolveAdminRole()))return showAdminLogin();applyAdminPermissions();showPage("admin");await showAdminTab("rounds")}else showAdminLogin()}$("#adminNav").onclick=openAdmin;'''
replace_once(old_open,new_open,'open admin')

# Role selection handlers before login function.
anchor='async function adminReq(action,payload={},auth=true)'
idx=s.find(anchor)
if idx<0: raise SystemExit('adminReq anchor not found')
role_bind='''document.querySelectorAll(".adminRoleChoice").forEach(b=>b.onclick=()=>{pendingAdminRole=b.dataset.adminRole||"";document.querySelectorAll(".adminRoleChoice").forEach(x=>x.classList.toggle("selected",x===b));$("#adminPass").focus()});\n'''
s=s[:idx]+role_bind+s[idx:]

# Replace login/logout and tab guarding.
start=s.find('async function adminLogin(){')
end=s.find('function adminBetButtons',start)
if start<0 or end<0: raise SystemExit('admin login block not found')
old=s[start:end]
new='''async function adminLogin(){const msg=$("#adminLoginMsg"),btn=$("#adminLoginBtn");if(!pendingAdminRole){msg.textContent="יש לבחור משתמש ניהול.";msg.className="statusMsg error";return}msg.textContent="מתחבר...";msg.className="statusMsg";btn.disabled=true;try{const d=await adminReq("login",{role:pendingAdminRole,password:$("#adminPass").value},false);adminToken=d.token;adminRole=d.role||pendingAdminRole;sessionStorage.setItem("redball_betting_admin_v2",adminToken);sessionStorage.setItem("redball_betting_admin_role",adminRole);applyAdminPermissions();$("#adminLoginModal").classList.remove("show");msg.textContent="";showPage("admin");await showAdminTab("rounds")}catch(e){msg.textContent="שגיאה: "+(e.message||"לא ניתן להתחבר");msg.className="statusMsg error"}finally{btn.disabled=false}}async function adminLogout(){try{if(adminToken)await adminReq("logout")}catch(e){}finally{adminToken="";adminRole="";pendingAdminRole="";sessionStorage.removeItem("redball_betting_admin_v2");sessionStorage.removeItem("redball_betting_admin_role");$("#adminPass").value="";showPage("sports")}}$("#adminLogoutBtn").onclick=adminLogout;$("#adminLoginBtn").onclick=adminLogin;$("#adminPass").addEventListener("keydown",e=>{if(e.key==="Enter")adminLogin()});\nasync function showAdminTab(name){if(adminRole==="betzi"&&["add","games"].includes(name))name="rounds";document.querySelectorAll(".adminTabBtn").forEach(b=>b.classList.toggle("active",b.dataset.adminTab===name));document.querySelectorAll(".adminTabPane").forEach(p=>p.classList.remove("active"));const pane=$("#adminTab"+name.charAt(0).toUpperCase()+name.slice(1));if(pane)pane.classList.add("active");if(name==="rounds")await adminRounds();if(name==="games")await adminGames();if(name==="bets")await adminAllBets();if(name==="archive")await loadArchive()}document.querySelectorAll(".adminTabBtn").forEach(b=>b.onclick=()=>showAdminTab(b.dataset.adminTab));const archiveRefresh=$("#refreshGameArchive");if(archiveRefresh)archiveRefresh.onclick=()=>loadArchive();\n'''
s=s[:start]+new+s[end:]

# Keep role selection when closing/reopening clean.
replace_once('$("#closeAdminLogin").onclick=()=>$("#adminLoginModal").classList.remove("show");', '$("#closeAdminLogin").onclick=()=>$("#adminLoginModal").classList.remove("show");', 'close login')

# Safety assertions.
for needle in ['data-admin-role="sani"','data-admin-role="vladi"','data-admin-role="betzi"','redball_betting_admin_role','adminRole==="betzi"','adminReq("login",{role:pendingAdminRole']:
    if needle not in s: raise SystemExit('missing '+needle)

p.write_text(s,encoding='utf-8')
print('betting admin role selector and permissions added')
