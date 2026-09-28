from pathlib import Path

CSP = "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https://images.unsplash.com; connect-src 'self' https://eqtgyxabuosyinnhairr.supabase.co wss://eqtgyxabuosyinnhairr.supabase.co; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests\">\n<meta name=\"referrer\" content=\"strict-origin-when-cross-origin\">\n"

def add_meta(s):
    if 'Content-Security-Policy' not in s:
        s=s.replace('<meta name="viewport" content="width=device-width,initial-scale=1.0">','<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'+CSP,1)
        s=s.replace('<meta name="viewport" content="width=device-width,initial-scale=1">','<meta name="viewport" content="width=device-width,initial-scale=1">\n'+CSP,1)
    return s

# index.html
p=Path('index.html'); s=p.read_text(encoding='utf-8'); s=add_meta(s)
old="async function loadEmployees(){const {data,error}=await supabaseClient.from('employees').select('name').order('name');if(error)throw error;WORKERS=(data||[]).map(x=>x.name);fillWorkerSelects()}"
new="async function loadEmployees(){const d=await api(PUBLIC_FUNCTION_URL,'list_workers');WORKERS=d.workers||[];fillWorkerSelects()}"
if old in s: s=s.replace(old,new,1)
if "if(window.top!==window.self)" not in s:
    s=s.replace("<script>\nconst SUPABASE_URL=","<script>\nif(window.top!==window.self){try{window.top.location=window.self.location.href}catch(e){document.documentElement.innerHTML=''}}\nconst SUPABASE_URL=",1)
p.write_text(s,encoding='utf-8')

# betting.html
p=Path('betting.html'); s=p.read_text(encoding='utf-8'); s=add_meta(s)
if "PUBLIC_URL=SB_URL+\"/functions/v1/redball-public\"" not in s:
    s=s.replace('ADMIN_URL=SB_URL+"/functions/v1/redball-admin";','ADMIN_URL=SB_URL+"/functions/v1/redball-admin",PUBLIC_URL=SB_URL+"/functions/v1/redball-public";',1)
if "async function publicReq(" not in s:
    anchor='function showPage(name)'
    helper='async function publicReq(action,payload={}){const res=await fetch(PUBLIC_URL,{method:"POST",headers:{"Content-Type":"application/json","apikey":KEY,"x-redball-client":clientToken},body:JSON.stringify({action,...payload})});let d={};try{d=await res.json()}catch(e){}if(!res.ok)throw new Error(d.error||"שגיאה");return d}\n'
    s=s.replace(anchor,helper+anchor,1)
old='const total=selectedGames.reduce((a,x)=>a*x.o,1),code="RB-"+Date.now().toString(36).toUpperCase();$("#send").disabled=true;$("#send").textContent="שולח...";const {error}=await db.from("bets").insert({bet_code:code,player_name:name,stake,total_odd:total,potential_win:Math.floor(stake*total),picks:selectedGames,payment_status:"pending",result_status:"pending",client_token:clientToken});$("#send").disabled=false;$("#send").textContent="שלח הימור לעובדים";if(error)return setMsg("שגיאה בשליחת ההימור: "+error.message);localStorage.setItem("redball_player_name",name);setMsg("✅ ההימור "+code+" נשלח לעובדים וממתין לתשלום.","success");'
new='$("#send").disabled=true;$("#send").textContent="שולח...";let created;try{created=await publicReq("create_bet",{player_name:name,stake,selections:selectedGames.map(x=>({game_id:x.game_id,pick:x.j===0?"1":x.j===1?"X":"2"}))})}catch(e){$("#send").disabled=false;$("#send").textContent="שלח הימור לעובדים";return setMsg("שגיאה בשליחת ההימור: "+e.message)}$("#send").disabled=false;$("#send").textContent="שלח הימור לעובדים";const code=created.bet_code;saveTicketCode(code);localStorage.setItem("redball_player_name",name);setMsg("✅ ההימור "+code+" נשלח לעובדים וממתין לתשלום.","success");'
if old in s: s=s.replace(old,new,1)
old2='async function fetchImportedBet(code){const lookup=ticketLookupClient(code);const {data,error}=await lookup.from("bets").select("id,bet_code,created_at,player_name,stake,total_odd,potential_win,picks,payment_status,result_status,paid_at,paid_by").eq("bet_code",code).maybeSingle();if(error)throw error;return data||null}'
new2='async function fetchImportedBet(code){const d=await publicReq("lookup_ticket",{code});return d.bet||null}'
if old2 in s: s=s.replace(old2,new2,1)
if "if(window.top!==window.self)" not in s:
    s=s.replace("<script>\nconst SB_URL=","<script>\nif(window.top!==window.self){try{window.top.location=window.self.location.href}catch(e){document.documentElement.innerHTML=''}}\nconst SB_URL=",1)
p.write_text(s,encoding='utf-8')

# assertions
idx=Path('index.html').read_text(encoding='utf-8'); bet=Path('betting.html').read_text(encoding='utf-8')
assert "list_workers" in idx and "from('employees').select('name')" not in idx
assert 'publicReq("create_bet"' in bet and 'publicReq("lookup_ticket"' in bet
assert 'Content-Security-Policy' in idx and 'Content-Security-Policy' in bet
print('Stage 3 patch applied')
