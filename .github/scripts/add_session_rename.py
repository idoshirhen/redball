from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

old='''async function adminRounds(){try{const d=await adminSessionReq("list_sessions"),rows=d.sessions||[],select=$("#round"),selected=select?select.value:"";if(select){select.innerHTML='<option value="">בחר סשן</option>'+rows.map(r=>'<option value="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+'</option>').join("");if(selected&&rows.some(r=>String(r.round_no)===selected))select.value=selected}else{}$("#adminRounds").innerHTML=rows.length?rows.map(r=>'<div class="roundAdmin"><b>'+esc(r.name||("סשן "+r.round_no))+'</b><button class="ghost roundToggle" data-round="'+r.round_no+'" data-open="'+r.is_open+'">'+(r.is_open?'🔒 נעל':'🔓 פתח')+'</button></div>').join(""):'<div class="muted">עדיין אין סשנים.</div>';document.querySelectorAll(".roundToggle").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_open",{round_no:+b.dataset.round,is_open:b.dataset.open!=="true"});await adminRounds();await load()}catch(e){siteAlert("לא ניתן לעדכן סשן: "+e.message,"שגיאה")}})}catch(e){$("#adminRounds").textContent=e.message}}'''

new='''async function adminRounds(){try{const d=await adminSessionReq("list_sessions"),rows=d.sessions||[],select=$("#round"),selected=select?select.value:"";if(select){select.innerHTML='<option value="">בחר סשן</option>'+rows.map(r=>'<option value="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+'</option>').join("");if(selected&&rows.some(r=>String(r.round_no)===selected))select.value=selected}else{}$("#adminRounds").innerHTML=rows.length?rows.map(r=>'<div class="roundAdmin" data-round="'+r.round_no+'"><div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1"><b class="sessionNameText" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(r.name||("סשן "+r.round_no))+'</b><button class="ghost renameSession" type="button" data-round="'+r.round_no+'" data-name="'+esc(r.name||("סשן "+r.round_no))+'" style="padding:6px 9px;font-size:12px">✏️ שנה שם</button></div><button class="ghost roundToggle" data-round="'+r.round_no+'" data-open="'+r.is_open+'">'+(r.is_open?'🔒 נעל':'🔓 פתח')+'</button></div>').join(""):'<div class="muted">עדיין אין סשנים.</div>';document.querySelectorAll(".renameSession").forEach(b=>b.onclick=async()=>{const current=b.dataset.name||'',name=(await sitePrompt("שם חדש לסשן:",current,"שינוי שם סשן"));if(name===null)return;const clean=String(name).trim();if(!clean)return siteAlert("יש להזין שם לסשן.","שגיאה");if(clean===current)return;try{await adminSessionReq("rename_session",{round_no:+b.dataset.round,name:clean});siteToast("שם הסשן עודכן");await adminRounds();await adminGames();await load()}catch(e){siteAlert("לא ניתן לשנות שם: "+e.message,"שגיאה")}});document.querySelectorAll(".roundToggle").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_open",{round_no:+b.dataset.round,is_open:b.dataset.open!=="true"});await adminRounds();await load()}catch(e){siteAlert("לא ניתן לעדכן סשן: "+e.message,"שגיאה")}})}catch(e){$("#adminRounds").textContent=e.message}}'''

if old not in s:
    raise SystemExit('adminRounds anchor not found')
s=s.replace(old,new,1)

if 'rename_session' not in s or 'renameSession' not in s or '✏️ שנה שם' not in s:
    raise SystemExit('rename UI missing')

p.write_text(s,encoding='utf-8')
print('session rename UI applied')
