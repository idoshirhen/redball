from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

# Add Elo admin endpoint
if 'ELO_ADMIN_URL=' not in s:
    old='SESSIONS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-sessions",PUBLIC_URL='
    new='SESSIONS_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-sessions",ELO_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-elo",PUBLIC_URL='
    if old not in s:
        raise SystemExit('endpoint anchor not found')
    s=s.replace(old,new,1)

# Add refresh button to session management
if 'id="refreshEloOdds"' not in s:
    old='<button id="createSession" class="primary full" type="button">+ סשן חדש</button><p id="sessionMsg" class="small full"></p>'
    new='<button id="createSession" class="primary full" type="button">+ סשן חדש</button><button id="refreshEloOdds" class="ghost full" type="button">🔄 רענן Elo וחישוב יחסים</button><p id="sessionMsg" class="small full"></p>'
    if old not in s:
        raise SystemExit('session button anchor not found')
    s=s.replace(old,new,1)

# Add request helper before the main admin request helper
if 'async function adminEloReq(' not in s:
    anchor='async function adminReq(action,payload={},auth=true)'
    idx=s.find(anchor)
    if idx<0:
        raise SystemExit('adminReq anchor not found')
    helper='async function adminEloReq(action,payload={}){const h={"Content-Type":"application/json","apikey":KEY};if(adminToken)h["x-admin-token"]=adminToken;const res=await fetch(ELO_ADMIN_URL,{method:"POST",headers:h,body:JSON.stringify({action,...payload})});let d={};try{d=await res.json()}catch(e){}if(!res.ok){if(res.status===401){adminToken="";sessionStorage.removeItem("redball_betting_admin_v2")}throw new Error(d.error||"שגיאה")}return d}\n'
    s=s[:idx]+helper+s[idx:]

# Add click handler before the next helper function
if 'refreshEloOdds").onclick' not in s:
    anchor='function bindDynamicGameResultClear'
    idx=s.find(anchor)
    if idx<0:
        raise SystemExit('bindDynamicGameResultClear anchor not found')
    handler='''$("#refreshEloOdds").onclick=async()=>{if(!await siteConfirm("למשוך Elo עדכני מ-EloFootball ולחשב מחדש את היחסים לכל המשחקים העתידיים?\\nמשחקים שכבר התחילו או שיש להם תוצאה לא ישתנו.","רענון Elo ויחסים"))return;const btn=$("#refreshEloOdds"),old=btn.textContent;btn.disabled=true;btn.textContent="⏳ מושך Elo ומחשב...";try{const d=await adminEloReq("refresh_all");let msg="✅ עודכנו "+Number(d.updated||0)+" משחקים מתוך "+Number(d.eligible||0);if(Number(d.skipped_count||0)>0)msg+="\\n⚠️ "+Number(d.skipped_count||0)+" משחקים לא עודכנו";if(Array.isArray(d.missing_teams)&&d.missing_teams.length)msg+="\\nקבוצות שלא נמצאו: "+d.missing_teams.join(", ");if(Array.isArray(d.source_errors)&&d.source_errors.length)msg+="\\nשגיאות מקור: "+d.source_errors.map(x=>x.country).join(", ");siteAlert(msg,"רענון Elo הושלם");await adminGames();await load()}catch(e){siteAlert("לא ניתן לרענן Elo: "+e.message,"שגיאה")}finally{btn.disabled=false;btn.textContent=old}}\n'''
    s=s[:idx]+handler+s[idx:]

for required in ['ELO_ADMIN_URL','redball-admin-elo','refreshEloOdds','adminEloReq','🔄 רענן Elo וחישוב יחסים']:
    if required not in s:
        raise SystemExit('missing '+required)

p.write_text(s,encoding='utf-8')
print('Elo refresh button patch applied')
