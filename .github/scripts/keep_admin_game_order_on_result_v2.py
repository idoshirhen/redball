from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

old1="siteToast('תוצאת המשחק נשמרה');await adminGames();if($(\"#adminTabBets\").classList.contains(\"active\"))await adminAllBets(false);if($(\"#minePage\").classList.contains(\"activePage\"))await loadMyBets()"
new1="siteToast('תוצאת המשחק נשמרה');card.querySelectorAll('.gameResultBtn').forEach(x=>x.classList.toggle('selected',x.dataset.result===btn.dataset.result));if(!card.querySelector('.gameResultClear')){const c=document.createElement('button');c.className='ghost gameResultClear';c.type='button';c.textContent='↩ בטל תוצאה';card.querySelector('.gameResultRow').appendChild(c);bindDynamicGameResultClear(card,c)}if($(\"#adminTabBets\").classList.contains(\"active\"))await adminAllBets(false);if($(\"#minePage\").classList.contains(\"activePage\"))await loadMyBets()"
if old1 not in s: raise SystemExit('result reload anchor not found')
s=s.replace(old1,new1,1)

old2="siteToast('תוצאת המשחק בוטלה');await adminGames();if($(\"#adminTabBets\").classList.contains(\"active\"))await adminAllBets(false);if($(\"#minePage\").classList.contains(\"activePage\"))await loadMyBets()"
new2="siteToast('תוצאת המשחק בוטלה');card.querySelectorAll('.gameResultBtn').forEach(x=>x.classList.remove('selected'));clear.remove();if($(\"#adminTabBets\").classList.contains(\"active\"))await adminAllBets(false);if($(\"#minePage\").classList.contains(\"activePage\"))await loadMyBets()"
if old2 not in s: raise SystemExit('clear reload anchor not found')
s=s.replace(old2,new2,1)

anchor='async function adminGames(){'
helper="""function bindDynamicGameResultClear(card,clear){clear.onclick=async()=>{if(!await siteConfirm('לבטל את תוצאת המשחק?\\nהטפסים יחזרו לחישוב לפי שאר המשחקים.','ביטול תוצאה'))return;try{await adminResultReq('set_game_result',{id:card.dataset.id,result:null});siteToast('תוצאת המשחק בוטלה');card.querySelectorAll('.gameResultBtn').forEach(x=>x.classList.remove('selected'));clear.remove();if($(\"#adminTabBets\").classList.contains(\"active\"))await adminAllBets(false);if($(\"#minePage\").classList.contains(\"activePage\"))await loadMyBets()}catch(e){siteAlert('לא ניתן לבטל תוצאה: '+e.message,'שגיאה')}}}\n"""
if 'function bindDynamicGameResultClear(' not in s:
    if anchor not in s: raise SystemExit('adminGames anchor not found')
    s=s.replace(anchor,helper+anchor,1)

if "siteToast('תוצאת המשחק נשמרה');await adminGames()" in s: raise SystemExit('result still reloads adminGames')
if "siteToast('תוצאת המשחק בוטלה');await adminGames()" in s: raise SystemExit('clear still reloads adminGames')

p.write_text(s,encoding='utf-8')
print('admin game result updates now stay in place')
