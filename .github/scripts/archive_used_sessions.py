from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

MARK='REDBALL-SAFE-SESSION-ARCHIVE-V1'
if MARK in s:
    raise SystemExit('patch already applied')

def function_end(src,start):
    brace=src.find('{',start)
    if brace<0:return -1
    depth=0;i=brace;quote=None;escape=False;line_comment=False;block_comment=False
    while i<len(src):
        c=src[i];n=src[i+1] if i+1<len(src) else ''
        if line_comment:
            if c=='\n': line_comment=False
            i+=1;continue
        if block_comment:
            if c=='*' and n=='/': block_comment=False;i+=2;continue
            i+=1;continue
        if quote:
            if escape: escape=False
            elif c=='\\': escape=True
            elif c==quote: quote=None
            i+=1;continue
        if c=='/' and n=='/': line_comment=True;i+=2;continue
        if c=='/' and n=='*': block_comment=True;i+=2;continue
        if c in ('"',"'",'`'): quote=c;i+=1;continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    return -1

# marker + endpoint
s=s.replace('<script>','<script>\n/* '+MARK+' */',1)
old='ELO_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-elo",PUBLIC_URL=SB_URL+"/functions/v1/redball-public";'
new='ELO_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-elo",ARCHIVE_ADMIN_URL=SB_URL+"/functions/v1/redball-admin-archive-session",PUBLIC_URL=SB_URL+"/functions/v1/redball-public";'
if old not in s: raise SystemExit('endpoint anchor missing')
s=s.replace(old,new,1)

# add archive request helper after session request helper
anchor='async function adminEloReq(action,payload={})'
pos=s.find(anchor)
if pos<0: raise SystemExit('adminEloReq anchor missing')
helper='''async function adminArchiveReq(action,payload={}){const h={"Content-Type":"application/json","apikey":KEY};if(adminToken)h["x-admin-token"]=adminToken;const res=await fetch(ARCHIVE_ADMIN_URL,{method:"POST",headers:h,body:JSON.stringify({action,...payload})});let d={};try{d=await res.json()}catch(e){}if(!res.ok){if(res.status===401){adminToken="";adminRole="";sessionStorage.removeItem("redball_betting_admin_v2");sessionStorage.removeItem("redball_betting_admin_role")}throw new Error(d.error||"שגיאה")}return d}\n'''
s=s[:pos]+helper+s[pos:]

# replace adminRounds with safe-delete/archive behavior
start=s.find('async function adminRounds(){')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit('adminRounds parse failed')
admin_rounds=r'''async function adminRounds(){try{const d=await adminSessionReq("list_sessions"),rows=(d.sessions||[]).filter(r=>!r.archived_at),select=$("#round"),selected=select?select.value:"";if(select){select.innerHTML='<option value="">בחר סשן</option>'+rows.map(r=>'<option value="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+'</option>').join("");if(selected&&rows.some(r=>String(r.round_no)===selected))select.value=selected}$("#adminRounds").innerHTML=rows.length?rows.map(r=>'<div class="roundAdmin '+(r.customer_visible===false?'sessionHidden':'')+'" data-round="'+r.round_no+'"><div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;flex-wrap:wrap"><b class="sessionNameText" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(r.name||("סשן "+r.round_no))+'</b><span class="small">'+(r.is_open?'🟢 פתוח':'🔒 נעול')+'</span><button class="ghost renameSession" type="button" data-round="'+r.round_no+'" data-name="'+esc(r.name||("סשן "+r.round_no))+'" style="padding:6px 9px;font-size:12px">✏️ שנה שם</button><button class="ghost danger deleteSession" type="button" data-round="'+r.round_no+'" data-name="'+esc(r.name||("סשן "+r.round_no))+'" style="padding:6px 9px;font-size:12px">🗑 מחק סשן</button></div><button class="ghost sessionEye" title="'+(r.customer_visible===false?'מוסתר מהלקוחות - לחץ להצגה':'מוצג ללקוחות - לחץ להסתרה')+'" data-round="'+r.round_no+'" data-visible="'+(r.customer_visible!==false)+'">'+(r.customer_visible===false?'🙈':'👁️')+'</button><button class="ghost roundToggle" data-round="'+r.round_no+'" data-open="'+r.is_open+'">'+(r.is_open?'🔒 נעל':'🔓 פתח')+'</button></div>').join(""):'<div class="muted">עדיין אין סשנים פעילים.</div>';document.querySelectorAll(".renameSession").forEach(b=>b.onclick=async()=>{const current=b.dataset.name||'',name=(await sitePrompt("שם חדש לסשן:",current,"שינוי שם סשן"));if(name===null)return;const clean=String(name).trim();if(!clean)return siteAlert("יש להזין שם לסשן.","שגיאה");if(clean===current)return;try{await adminSessionReq("rename_session",{round_no:+b.dataset.round,name:clean});siteToast("שם הסשן עודכן");await adminRounds();await adminGames();await load()}catch(e){siteAlert("לא ניתן לשנות שם: "+e.message,"שגיאה")}});document.querySelectorAll(".deleteSession").forEach(b=>b.onclick=async()=>{const name=b.dataset.name||("סשן "+b.dataset.round);if(!await siteConfirm("למחוק את הסשן ‘"+name+"’?\nאם אין טפסים שמשתמשים בו – הסשן והמשחקים יימחקו לצמיתות.\nאם קיימים טפסים והמשחקים כבר התחילו – הסשן יעבור לארכיון והמשחקים יישמרו כדי שהטפסים והתוצאות ימשיכו לעבוד.","מחיקת סשן"))return;try{const d=await adminSessionReq("delete_session",{round_no:+b.dataset.round});siteToast("הסשן נמחק"+(d.deleted_games?" יחד עם "+d.deleted_games+" משחקים":""))}catch(e){const m=String(e?.message||e||'');if(!m.includes("משחקים שמופיעים בטפסי הימור"))return siteAlert("לא ניתן למחוק סשן: "+m,"שגיאה");try{await adminArchiveReq("archive_session",{round_no:+b.dataset.round});siteToast("הסשן הועבר לארכיון. הטפסים והמשחקים נשמרו.")}catch(ae){return siteAlert("לא ניתן להעביר את הסשן לארכיון: "+ae.message,"שגיאה")}}await adminRounds();await adminGames();await load();if($("#adminTabArchive")?.classList.contains("active"))await loadArchive()});document.querySelectorAll(".roundToggle").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_open",{round_no:+b.dataset.round,is_open:b.dataset.open!=="true"});await adminRounds();await adminGames();await load();if($("#adminTabArchive")?.classList.contains("active"))await loadArchive()}catch(e){siteAlert("לא ניתן לעדכן סשן: "+e.message,"שגיאה")}});document.querySelectorAll(".sessionEye").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_visible",{round_no:+b.dataset.round,customer_visible:b.dataset.visible!=="true"});await adminRounds();await load();siteToast(b.dataset.visible==="true"?"הסשן הוסתר מהלקוחות":"הסשן מוצג ללקוחות")}catch(e){siteAlert("לא ניתן לעדכן תצוגה: "+e.message,"שגיאה")}})}catch(e){$("#adminRounds").textContent=e.message}}'''
s=s[:start]+admin_rounds+s[end:]

# archive should include explicitly archived sessions, plus naturally completed historical sessions
start=s.find('async function loadArchive(){')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit('loadArchive parse failed')
archive_fn=r'''async function loadArchive(){const box=$("#adminSessionArchive");if(!box)return;box.innerHTML='<div class="muted">טוען ארכיון...</div>';try{const [gd,rd]=await Promise.all([adminReq("list_betting_games"),adminSessionReq("list_sessions")]),allGames=gd.games||[],allRounds=rd.sessions||[],now=Date.now(),byRound=new Map();allGames.forEach(g=>{const k=Number(g.round_no);if(!byRound.has(k))byRound.set(k,[]);byRound.get(k).push(g)});const archived=allRounds.map(r=>({round:r,games:byRound.get(Number(r.round_no))||[]})).filter(x=>x.games.length&&(!!x.round.archived_at||x.games.every(g=>g.starts_at&&new Date(g.starts_at).getTime()<=now))).sort((a,b)=>{const ad=a.round.archived_at?new Date(a.round.archived_at).getTime():0,bd=b.round.archived_at?new Date(b.round.archived_at).getTime():0;return bd-ad||Number(b.round.round_no)-Number(a.round.round_no)});if(!archived.length){box.innerHTML='<div class="panel archiveEmpty">עדיין אין סשנים שהסתיימו או הועברו לארכיון.</div>';return}box.innerHTML=archived.map(x=>'<section class="archiveSession"><div class="archiveSessionHead"><div><b>'+esc(x.round.name||('סשן '+x.round.round_no))+'</b>'+(x.round.archived_at?'<div class="small">📦 הועבר לארכיון</div>':'<div class="small">היסטוריית משחקים</div>')+'</div><span class="small">'+x.games.length+' משחקים</span></div><div class="archiveSessionBody">'+x.games.sort((a,b)=>new Date(a.starts_at||0)-new Date(b.starts_at||0)).map(g=>{const score=g.api_home_goals!=null&&g.api_away_goals!=null?Number(g.api_home_goals)+' - '+Number(g.api_away_goals):'—';return '<div class="archiveGame"><div class="archiveGameTop"><div><b>'+esc(g.home_team)+' 🆚 '+esc(g.away_team)+'</b><div class="small">'+(g.starts_at?fmtDate(g.starts_at):'')+'</div></div><div class="archiveScore">'+esc(score)+'</div></div><div class="archiveResult">'+esc(resultText(g))+(g.result_set_by==='API_FOOTBALL'?' · עודכן אוטומטית':'')+'</div></div>'}).join('')+'</div></section>').join('')}catch(e){box.innerHTML='<div class="statusMsg error">שגיאה בטעינת הארכיון: '+esc(e.message||String(e))+'</div>'}}'''
s=s[:start]+archive_fn+s[end:]

p.write_text(s,encoding='utf-8')
print('safe archive behavior patched')
