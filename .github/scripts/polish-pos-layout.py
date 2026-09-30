from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Make the POS logo match the betting logo: RedBall, two colors, no gap, keep emojis.
old_heading = '<h1>🎳🎱 Red Ball 🎱🎳</h1><div id="categoryTabs" class="categoryTabs"></div>'
new_heading = '<h1 class="posBrandTitle">🎳🎱 <span class="posBrandRed">Red</span><span class="posBrandBall">Ball</span> 🎱🎳</h1><div id="categoryTabs" class="categoryTabs"></div>'
if old_heading not in s:
    raise SystemExit('POS heading anchor not found')
s = s.replace(old_heading, new_heading, 1)

# 2) Put the food+drink combo first in the Promotions list.
old_promos = '"מבצעים":[{name:"מבצע שתיה קלה (10)",price:1000},{name:"מבצע נקניקיה (10)",price:1000},{name:"מבצע אוכל+שתיה (10+10)",price:2000},{name:"נרגילה טבק+גחל",price:1800}]'
new_promos = '"מבצעים":[{name:"מבצע אוכל+שתיה (10+10)",price:2000},{name:"מבצע שתיה קלה (10)",price:1000},{name:"מבצע נקניקיה (10)",price:1000},{name:"נרגילה טבק+גחל",price:1800}]'
if old_promos not in s:
    raise SystemExit('Promotions anchor not found')
s = s.replace(old_promos, new_promos, 1)

# 3) Softer category panels + wrapped category tabs (no horizontal scrollbar).
marker = '/* REDBALL-POS-POLISH-V2 */'
css = r'''

/* REDBALL-POS-POLISH-V2 */
.categoryTabs{
  max-width:900px;
  width:min(900px,calc(100% - 24px));
  flex-wrap:wrap;
  justify-content:center;
  overflow:visible;
  scrollbar-width:none;
  background:rgba(10,10,10,.62);
  border-color:rgba(255,255,255,.08);
  box-shadow:0 8px 28px rgba(0,0,0,.18);
  backdrop-filter:blur(6px)
}
.categoryTabs::-webkit-scrollbar{display:none}
.categoryTab{flex:0 0 auto}
.section{
  background:linear-gradient(180deg,rgba(17,17,17,.72),rgba(12,12,12,.62));
  border:1px solid rgba(255,255,255,.09);
  box-shadow:0 10px 35px rgba(0,0,0,.14),inset 0 1px 0 rgba(255,255,255,.018);
  backdrop-filter:blur(4px)
}
.section h2{color:#f5f5f5;text-shadow:none}
#posScreen>h1.posBrandTitle{
  font-size:38px;
  line-height:1;
  font-weight:800;
  letter-spacing:1px;
  color:#fff;
  margin:24px 0 18px;
  text-shadow:none
}
.posBrandRed{color:#6ed8ff;text-shadow:0 0 18px rgba(110,216,255,.42)}
.posBrandBall{color:#ff4de1;text-shadow:0 0 18px rgba(255,77,225,.32)}
@media(max-width:700px){
  .categoryTabs{width:calc(100% - 16px);padding:6px 5px;gap:5px}
  .categoryTab{padding:9px 10px;font-size:13px}
  #posScreen>h1.posBrandTitle{font-size:34px}
  .section{background:rgba(15,15,15,.68);border-color:rgba(255,255,255,.075)}
}
'''
if marker not in s:
    if '</style>' not in s:
        raise SystemExit('style closing tag not found')
    s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s, encoding='utf-8')
print('Patched index.html')
