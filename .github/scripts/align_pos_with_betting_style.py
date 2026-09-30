from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='"מבצעים":[{name:"מבצע שתיה קלה (10)",price:1000},{name:"מבצע נקניקיה (10)",price:1000},{name:"נרגילה טבק+גחל",price:1800}]'
new='"מבצעים":[{name:"מבצע שתיה קלה (10)",price:1000},{name:"מבצע נקניקיה (10)",price:1000},{name:"מבצע אוכל+שתיה (10+10)",price:2000},{name:"נרגילה טבק+גחל",price:1800}]'
if old not in s:
    raise SystemExit('promotions anchor not found')
s=s.replace(old,new,1)

marker='</style></head>'
if marker not in s:
    raise SystemExit('style marker not found')

css=r'''

/* REDBALL-POS-BETTING-STYLE-ALIGN-V1 */
body{font-family:"Rubik",Arial,sans-serif;color:#fff;background:linear-gradient(rgba(0,0,0,.9),rgba(0,0,0,.95)),url("https://images.unsplash.com/photo-1511512578047-dfb367046420");background-size:cover;background-position:center;background-attachment:fixed}
#posScreen>h1{font-size:38px;line-height:1;font-weight:800;letter-spacing:1px;color:#6ed8ff;text-shadow:0 0 18px rgba(110,216,255,.42),0 0 28px rgba(255,77,225,.18);margin:24px 0 18px}
.topBar{background:rgba(10,10,10,.92);border-bottom:1px solid #353535;box-shadow:0 8px 30px rgba(0,0,0,.28);backdrop-filter:blur(8px)}
.employeeBadge{color:#6ed8ff;font-weight:800}
.secondary,.categoryTab,.btn{background:#191919;color:#fff;border:1px solid #444;transition:.18s}
.secondary:hover,.categoryTab:hover,.btn:hover{color:#fff;background:#222;border-color:#666;filter:none}
.main{background:#ff4de1;border:1px solid #ff4de1;color:#fff;border-radius:9px;font-weight:800;box-shadow:0 0 16px rgba(255,77,225,.12)}
.categoryTabs{max-width:760px;margin:0 auto 18px;display:flex;justify-content:flex-start;gap:6px;padding:6px;background:rgba(10,10,10,.9);border:1px solid #353535;border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,.35)}
.categoryTab{border:1px solid transparent;background:transparent;color:#aaa;padding:11px 13px;border-radius:11px;font-weight:700}
.categoryTab.active{color:#fff;background:linear-gradient(180deg,rgba(255,77,225,.28),rgba(110,216,255,.13));border-color:#ff4de1;box-shadow:0 0 16px rgba(255,77,225,.16)}
.sections-wrapper{max-width:1180px;padding:18px}
.section{margin:18px 0 28px;padding:14px;background:rgba(17,17,17,.94);border:1px solid #333;border-radius:14px}
.section h2{margin:2px 0 12px;font-size:23px}
.grid{gap:12px;padding:4px}
.card{width:180px;background:rgba(23,23,23,.97);border:1px solid #333;border-radius:12px;padding:14px;min-height:126px;transition:.18s}
.card:hover{border-color:#4a4a4a;transform:translateY(-1px)}
.card.active{border-color:#6ed8ff;background:#16313a;box-shadow:0 0 0 1px #6ed8ff inset,0 0 16px rgba(110,216,255,.14)}
.title{font-size:15px;font-weight:700}
.price{color:#6ed8ff;background:#0c1d22;border:1px solid #24515f;padding:4px 9px}
.qty{color:#6ed8ff;font-weight:800}
#orderPanel{background:rgba(17,17,17,.96);border:1px solid #333;border-radius:14px;box-shadow:0 12px 34px rgba(0,0,0,.38)}
#orderSummary b{background:#0c1d22;border:1px solid #24515f;color:#6ed8ff}
.total{color:#6ed8ff;font-weight:800}
.loginBox{background:rgba(17,17,17,.96);border:1px solid #333;border-radius:16px;box-shadow:0 20px 70px rgba(0,0,0,.55)}
.loginBox h1{font-size:38px;line-height:1;font-weight:800;color:#6ed8ff;text-shadow:0 0 18px rgba(110,216,255,.42),0 0 28px rgba(255,77,225,.18)}
.workerSelect,.workerPin{background:#181818;border:1px solid #444;border-radius:9px}
@media(max-width:700px){.categoryTabs{max-width:calc(100% - 24px);justify-content:flex-start}.sections-wrapper{padding:10px}.section{padding:10px}.grid{gap:8px}.card{width:100%}}
'''

s=s.replace(marker,css+'\n'+marker,1)
p.write_text(s,encoding='utf-8')
print('patched index.html')
