from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

def function_end(src,start):
    brace=src.find('{',start)
    if brace<0:return -1
    depth=0;i=brace;quote=None;escape=False;line_comment=False;block_comment=False
    while i<len(src):
        c=src[i];n=src[i+1] if i+1<len(src) else ''
        if line_comment:
            if c=='\n':line_comment=False
            i+=1;continue
        if block_comment:
            if c=='*' and n=='/':block_comment=False;i+=2;continue
            i+=1;continue
        if quote:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c==quote:quote=None
            i+=1;continue
        if c=='/' and n=='/':line_comment=True;i+=2;continue
        if c=='/' and n=='*':block_comment=True;i+=2;continue
        if c in ('"',"'",'`'):quote=c;i+=1;continue
        if c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    return -1

# Add fixture id field to new-game form.
old='<input id="start" type="datetime-local" step="60"><select id="round">'
new='<input id="start" type="datetime-local" step="60"><input id="fixtureId" type="number" min="1" step="1" inputmode="numeric" placeholder="API-Football Fixture ID"><select id="round">'
if 'id="fixtureId"' not in s:
    if old not in s: raise SystemExit('add game form anchor missing')
    s=s.replace(old,new,1)

# Verification badges.
css_anchor='.adminGameTitle{font-weight:700;margin-bottom:5px}'
css_extra='.verifyBadges{display:flex;gap:6px;flex-wrap:wrap;margin:7px 0}.verifyBadge{font-size:11px;font-weight:800;border-radius:999px;padding:4px 8px;border:1px solid #444}.verifyOk{color:#62e6a7;background:rgba(98,230,167,.10);border-color:rgba(98,230,167,.28)}.verifyWarn{color:#ffb143;background:rgba(255,177,67,.10);border-color:rgba(255,177,67,.30)}.verifyBad{color:#ff6672;background:rgba(255,90,103,.10);border-color:rgba(255,90,103,.30)}.verifyMuted{color:#aaa;background:#111;border-color:#3b3b3b}'
if '.verifyBadges{' not in s:
    if css_anchor not in s: raise SystemExit('admin game css anchor missing')
    s=s.replace(css_anchor,css_anchor+css_extra,1)

# Helper for admin game verification badges.
anchor='async function adminGames(){'
if 'function gameVerificationBadges(g)' not in s:
    idx=s.find(anchor)
    if idx<0: raise SystemExit('adminGames anchor missing')
    helper=r'''function gameVerificationBadges(g){const es=String(g.elo_status||'unchecked'),as=String(g.api_link_status||'unchecked');const elo=es==='verified'?'<span class="verifyBadge verifyOk">✅ Elo מאומת</span>':es==='missing'?'<span class="verifyBadge verifyBad">⚠️ חסר Elo</span>':'<span class="verifyBadge verifyMuted">Elo לא נבדק</span>';const api=as==='verified'?'<span class="verifyBadge verifyOk">✅ API מחובר</span>':as==='mismatch'?'<span class="verifyBadge verifyBad">⚠️ API לא תואם</span>':as==='missing'?'<span class="verifyBadge verifyBad">⚠️ אין חיבור API</span>':'<span class="verifyBadge verifyMuted">API לא נבדק</span>';const state=g.is_open?'<span class="verifyBadge verifyOk">🟢 פתוח ללקוחות</span>':'<span class="verifyBadge verifyWarn">🔒 נעול ללקוחות</span>';return '<div class="verifyBadges">'+elo+api+state+'</div>'}
'''
    s=s[:idx]+helper+s[idx:]

old_title='<div class="adminGameTitle">'+"'+esc(g.home_team)+' - '+esc(g.away_team)+'"+'</div><div class="small">'
# Build literal safely.
old_title = '<div class="adminGameTitle">\'+esc(g.home_team)+\' - \'+esc(g.away_team)+\'</div><div class="small">'
new_title = '<div class="adminGameTitle">\'+esc(g.home_team)+\' - \'+esc(g.away_team)+\'</div>\'+gameVerificationBadges(g)+\'<div class="small">'
if 'gameVerificationBadges(g)' not in s[s.find('async function adminGames(){'):]:
    if old_title not in s: raise SystemExit('admin game title markup anchor missing')
    s=s.replace(old_title,new_title,1)

# Replace add-game handler with guarded verification flow.
start=s.find('$("#addGame").onclick=async()=>')
end=function_end(s,start)
if start<0 or end<0: raise SystemExit('addGame handler parse failed')
new_handler=r'''$("#addGame").onclick=async()=>{const msg=$("#adminMsg"),btn=$("#addGame"),home=$("#home").value.trim(),away=$("#away").value.trim(),round=+$("#round").value,fixtureId=+$("#fixtureId").value,startVal=$("#start").value;if(!home||!away||!round||!startVal||!Number.isInteger(fixtureId)||fixtureId<1){msg.textContent="יש למלא קבוצת בית, קבוצת חוץ, תאריך, סשן ו-Fixture ID של API-Football";return}const game={home_team:home,away_team:away,starts_at:new Date(startVal).toISOString(),round_no:round,api_fixture_id:fixtureId,odd_home:+$("#oh").value||1.5,odd_draw:+$("#od").value||1.5,odd_away:+$("#oa").value||1.5};const old=btn.textContent;btn.disabled=true;btn.textContent="⏳ בודק Elo ו-API...";try{const d=await adminSessionReq("add_game",{game}),v=d.verification||{};if(v.verified){msg.textContent="✅ המשחק אומת ונפתח ללקוחות. Elo: "+v.elo.home+" / "+v.elo.away+" • API: "+(v.api.home||"")+" - "+(v.api.away||"");msg.style.color="#62e6a7"}else{const parts=[];if(!v.elo?.ok)parts.push(v.elo?.reason||"Elo לא אומת");if(!v.api?.ok)parts.push(v.api?.reason||"API לא אומת");msg.textContent="⚠️ המשחק נשמר אבל נשאר נעול: "+parts.join(" • ");msg.style.color="#ffb143"}$("#home").value="";$("#away").value="";$("#start").value="";$("#fixtureId").value="";$("#oh").value="";$("#od").value="";$("#oa").value="";await adminGames();await load()}catch(e){msg.textContent=e.message;msg.style.color="#ff6672"}finally{btn.disabled=false;btn.textContent=old}}'''
s=s[:start]+new_handler+s[end:]

for token in ['fixtureId','gameVerificationBadges','Elo מאומת','API מחובר','בודק Elo ו-API']:
    if token not in s: raise SystemExit('missing token '+token)

p.write_text(s,encoding='utf-8')
print('game verification controls applied')
