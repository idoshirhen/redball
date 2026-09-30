from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

start=s.find('async function adminRounds(){')
if start<0:
    raise SystemExit('adminRounds start not found')
brace=s.find('{',start)
if brace<0:
    raise SystemExit('adminRounds brace not found')

depth=0
end=None
in_str=None
esc=False
for i in range(brace,len(s)):
    ch=s[i]
    if in_str:
        if esc:
            esc=False
        elif ch=='\\':
            esc=True
        elif ch==in_str:
            in_str=None
        continue
    if ch in ('"',"'",'`'):
        in_str=ch
        continue
    if ch=='{':
        depth+=1
    elif ch=='}':
        depth-=1
        if depth==0:
            end=i+1
            break
if end is None:
    raise SystemExit('adminRounds end not found')

new_fn=r'''async function adminRounds(){try{const d=await adminSessionReq("list_sessions"),rows=d.sessions||[],select=$("#round"),selected=select?select.value:"";if(select){select.innerHTML='<option value="">בחר סשן</option>'+rows.map(r=>'<option value="'+r.round_no+'">'+esc(r.name||("סשן "+r.round_no))+'</option>').join("");if(selected&&rows.some(r=>String(r.round_no)===selected))select.value=selected}else{}$("#adminRounds").innerHTML=rows.length?rows.map(r=>'<div class="roundAdmin" data-round="'+r.round_no+'"><div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;flex-wrap:wrap"><b class="sessionNameText" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(r.name||("סשן "+r.round_no))+'</b><button class="ghost renameSession" type="button" data-round="'+r.round_no+'" data-name="'+esc(r.name||("סשן "+r.round_no))+'" style="padding:6px 9px;font-size:12px">✏️ שנה שם</button><button class="ghost danger deleteSession" type="button" data-round="'+r.round_no+'" data-name="'+esc(r.name||("סשן "+r.round_no))+'" style="padding:6px 9px;font-size:12px">🗑 מחק סשן</button></div><button class="ghost roundToggle" data-round="'+r.round_no+'" data-open="'+r.is_open+'">'+(r.is_open?'🔒 נעל':'🔓 פתח')+'</button></div>').join(""):'<div class="muted">עדיין אין סשנים.</div>';document.querySelectorAll(".renameSession").forEach(b=>b.onclick=async()=>{const current=b.dataset.name||'',name=(await sitePrompt("שם חדש לסשן:",current,"שינוי שם סשן"));if(name===null)return;const clean=String(name).trim();if(!clean)return siteAlert("יש להזין שם לסשן.","שגיאה");if(clean===current)return;try{await adminSessionReq("rename_session",{round_no:+b.dataset.round,name:clean});siteToast("שם הסשן עודכן");await adminRounds();await adminGames();await load()}catch(e){siteAlert("לא ניתן לשנות שם: "+e.message,"שגיאה")}});document.querySelectorAll(".deleteSession").forEach(b=>b.onclick=async()=>{const name=b.dataset.name||("סשן "+b.dataset.round);if(!await siteConfirm("למחוק את הסשן ‘"+name+"’?\nכל המשחקים שבו יימחקו גם הם.\nאם קיימים טפסי הימור שמשתמשים במשחקים מהסשן – המחיקה תיחסם.","מחיקת סשן"))return;try{const d=await adminSessionReq("delete_session",{round_no:+b.dataset.round});siteToast("הסשן נמחק"+(d.deleted_games?" יחד עם "+d.deleted_games+" משחקים":""));await adminRounds();await adminGames();await load()}catch(e){siteAlert("לא ניתן למחוק סשן: "+e.message,"שגיאה")}});document.querySelectorAll(".roundToggle").forEach(b=>b.onclick=async()=>{try{await adminSessionReq("set_session_open",{round_no:+b.dataset.round,is_open:b.dataset.open!=="true"});await adminRounds();await load()}catch(e){siteAlert("לא ניתן לעדכן סשן: "+e.message,"שגיאה")}})}catch(e){$("#adminRounds").textContent=e.message}}'''

s=s[:start]+new_fn+s[end:]
for required in ['delete_session','deleteSession','🗑 מחק סשן','siteConfirm("למחוק את הסשן']:
    if required not in s:
        raise SystemExit('missing '+required)
p.write_text(s,encoding='utf-8')
print('delete session button patch applied')
