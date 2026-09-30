from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')
old='ADMIN_URL=SB_URL+"/functions/v1/redball-admin"'
new='ADMIN_URL=SB_URL+"/functions/v1/redball-betting-admin"'
if old not in s:
    raise SystemExit('admin url anchor not found')
s=s.replace(old,new,1)
s=s.replace('redball_betting_admin','redball_betting_admin_v2')
p.write_text(s,encoding='utf-8')
print('betting admin auth separated')
