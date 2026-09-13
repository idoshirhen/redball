from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

bad = 'alert("ההזמנה הועתקה, אבל המכירה לא נשמרה:\n" + error.message);'
# The previous patch accidentally wrote a real newline inside the JS string.
bad_real = 'alert("ההזמנה הועתקה, אבל המכירה לא נשמרה:\n" + error.message);'.replace('\\n', '\n')
good = 'alert("ההזמנה הועתקה, אבל המכירה לא נשמרה:\\n" + error.message);'

if bad_real in s:
    s = s.replace(bad_real, good, 1)
elif bad not in s and good not in s:
    raise SystemExit('Could not find save-error alert to verify')

path.write_text(s, encoding='utf-8')
print('Security syntax verified/fixed.')
