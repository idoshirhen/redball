from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')

# 1) Main navigation: archive is admin-only, so customer nav returns to 3 items.
s=s.replace('.mainNav{max-width:760px;margin:18px auto 0;display:grid;grid-template-columns:repeat(4,1fr);', '.mainNav{max-width:760px;margin:18px auto 0;display:grid;grid-template-columns:repeat(3,1fr);', 1)
archive_nav='<button class="navBtn" data-page="archive" type="button">📦 ארכיון משחקים</button>'
if archive_nav in s:
    s=s.replace(archive_nav,'',1)

# 2) Remove the customer archive page.
archive_page='<section id="archivePage" class="page"><div class="pageTitle"><h1>📦 ארכיון משחקים</h1><p>סשנים שהמשחקים בהם כבר התחילו נשמרים כאן עם התוצאות</p></div><div class="myBetsWrap"><div id="sessionArchive"><div class="muted">טוען ארכיון...</div></div></div></section>\n'
if archive_page in s:
    s=s.replace(archive_page,'',1)
else:
    raise SystemExit('customer archive page anchor not found')

# 3) Add an Archive tab inside betting admin.
old_tabs='<button class="adminTabBtn" type="button" data-admin-tab="games">משחקים קיימים</button><button class="adminTabBtn" type="button" data-admin-tab="bets">כל ההימורים</button></div>'
new_tabs='<button class="adminTabBtn" type="button" data-admin-tab="games">משחקים קיימים</button><button class="adminTabBtn" type="button" data-admin-tab="bets">כל ההימורים</button><button class="adminTabBtn" type="button" data-admin-tab="archive">📦 ארכיון משחקים</button></div>'
if old_tabs not in s:
    raise SystemExit('admin tabs anchor not found')
s=s.replace(old_tabs,new_tabs,1)
s=s.replace('.adminTabs{display:grid;grid-template-columns:repeat(4,1fr);', '.adminTabs{display:grid;grid-template-columns:repeat(5,1fr);', 1)

# 4) Add admin archive pane after All Bets.
anchor='</section></div></section>\n<footer class="footer">'
archive_pane='''<section id="adminTabArchive" class="adminTabPane panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><div><h2 style="margin:0">📦 ארכיון משחקים</h2><div class="small" style="margin-top:5px">סשנים שכל המשחקים בהם כבר התחילו נשמרים כאן לצפייה ניהולית.</div></div><button id="refreshGameArchive" class="ghost" type="button">🔄 רענן</button></div><div id="adminSessionArchive" style="margin-top:14px"><div class="muted">טוען ארכיון...</div></div></section>'''
if anchor not in s:
    raise SystemExit('admin page end anchor not found')
s=s.replace(anchor,archive_pane+anchor,1)

# 5) Customer page navigation no longer loads archive.
s=s.replace(';if(name==="mine")loadMyBets();if(name==="archive")loadArchive()}', ';if(name==="mine")loadMyBets()}', 1)

# 6) Repoint existing archive loader to admin pane and make it admin-tab driven.
old='async function loadArchive(){const box=$("#sessionArchive");if(!box)return;'
new='async function loadArchive(){const box=$("#adminSessionArchive");if(!box)return;'
if old not in s:
    raise SystemExit('loadArchive target anchor not found')
s=s.replace(old,new,1)

old_show='async function showAdminTab(name){document.querySelectorAll(".adminTabBtn").forEach(b=>b.classList.toggle("active",b.dataset.adminTab===name));document.querySelectorAll(".adminTabPane").forEach(p=>p.classList.remove("active"));const pane=$("#adminTab"+name.charAt(0).toUpperCase()+name.slice(1));if(pane)pane.classList.add("active");if(name==="rounds")await adminRounds();if(name==="games")await adminGames();if(name==="bets")await adminAllBets()}'
new_show='async function showAdminTab(name){document.querySelectorAll(".adminTabBtn").forEach(b=>b.classList.toggle("active",b.dataset.adminTab===name));document.querySelectorAll(".adminTabPane").forEach(p=>p.classList.remove("active"));const pane=$("#adminTab"+name.charAt(0).toUpperCase()+name.slice(1));if(pane)pane.classList.add("active");if(name==="rounds")await adminRounds();if(name==="games")await adminGames();if(name==="bets")await adminAllBets();if(name==="archive")await loadArchive()}'
if old_show not in s:
    raise SystemExit('showAdminTab anchor not found')
s=s.replace(old_show,new_show,1)

# 7) Manual refresh in admin archive.
insert='document.querySelectorAll(".adminTabBtn").forEach(b=>b.onclick=()=>showAdminTab(b.dataset.adminTab));'
if insert not in s:
    raise SystemExit('admin tab binding anchor not found')
s=s.replace(insert,insert+'const archiveRefresh=$("#refreshGameArchive");if(archiveRefresh)archiveRefresh.onclick=()=>loadArchive();',1)

# 8) Safety checks: customer My Bets stays untouched and archive is no longer public navigation.
for required in ['id="adminTabArchive"','id="adminSessionArchive"','data-admin-tab="archive"','if(name==="archive")await loadArchive()','function myBetCard(b)']:
    if required not in s:
        raise SystemExit('missing expected token: '+required)
if 'data-page="archive"' in s or 'id="archivePage"' in s or 'id="sessionArchive"' in s:
    raise SystemExit('customer archive remnants still present')

p.write_text(s,encoding='utf-8')
print('moved game archive to betting admin; customer My Bets preserved')
