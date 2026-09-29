from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')
marker='RED-BALL-ADMIN-BET-CONTROLS-V1'
if marker in s:
    print('Admin bet controls already applied')
    raise SystemExit(0)

css_marker='.adminBetPicks{margin-top:9px;font-size:12px;color:#bbb;line-height:1.6}'
css_new=css_marker+'''.adminBetControls{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;padding-top:12px;border-top:1px solid #2c2c2c}.adminBetControls button{flex:1;min-width:150px}.adminActionPaid{background:#0c3550;border-color:#2474a6}.adminActionWon{background:#087a4f;border-color:#14b875}.adminActionLost{background:#54191f;border-color:#8c2c36}.adminActionPrize{background:#9a6b00;border-color:#dca500;color:#fff}.adminPrizeDone{display:inline-block;margin-top:12px;padding:9px 12px;border-radius:9px;background:rgba(50,200,120,.12);border:1px solid rgba(98,230,167,.3);color:#62e6a7;font-weight:800}/* RED-BALL-ADMIN-BET-CONTROLS-V1 */'''
if css_marker not in s:
    raise SystemExit('admin bet CSS marker not found')
s=s.replace(css_marker,css_new,1)

start=s.find('async function adminAllBets(){')
end=s.find('$("#refreshAdminBets").onclick=adminAllBets;',start)
if start<0 or end<0:
    raise SystemExit('adminAllBets block not found')
end=end+len('$("#refreshAdminBets").onclick=adminAllBets;')
new_js=r'''function adminBetButtons(b){if(b.payment_status!=="paid")return '<button class="ghost adminActionPaid" type="button" onclick="adminBetAction(\''+b.id+'\',\'paid\')">💵 סמן כשולם</button>';if(b.result_status==="pending")return '<button class="ghost adminActionWon" type="button" onclick="adminBetAction(\''+b.id+'\',\'won\')">🏆 זכה</button><button class="ghost adminActionLost" type="button" onclick="adminBetAction(\''+b.id+'\',\'lost\')">❌ הפסיד</button>';if(b.result_status==="won"&&!b.prize_paid)return '<button class="ghost adminActionPrize" type="button" onclick="adminBetAction(\''+b.id+'\',\'prize_paid\')">✅ הלקוח קיבל את הכסף</button>';if(b.result_status==="won"&&b.prize_paid)return '<span class="adminPrizeDone">✅ הפרס נמסר ללקוח</span>';return '<span class="small">הטיקט נסגר כהפסד</span>'}
async function adminBetAction(id,status){const labels={paid:'לסמן את הטיקט כשולם?',won:'לסמן את הטיקט כזוכה?',lost:'לסמן את הטיקט כמפסיד?',prize_paid:'לאשר שהלקוח קיבל את כספי הזכייה?'};if(!confirm(labels[status]||'לאשר פעולה?'))return;try{await adminReq("admin_update_bet_status",{id,status});await adminAllBets();if($("#minePage").classList.contains("activePage"))await loadMyBets()}catch(e){alert("לא ניתן לעדכן את הטיקט: "+e.message)}}
async function adminAllBets(){const box=$("#adminBets");box.innerHTML='<div class="muted">טוען...</div>';try{const d=await adminReq("list_bets"),rows=d.bets||[];box.innerHTML=rows.length?rows.map(b=>{const st=betStatus(b),picks=Array.isArray(b.picks)?b.picks:[];return '<article class="adminBet"><div class="adminBetTop"><div><b class="betCode">'+esc(b.bet_code)+'</b><div class="small">'+fmtDate(b.created_at)+' • '+esc(b.player_name)+'</div></div><span class="betStatus '+st[1]+'">'+st[0]+'</span></div><div class="adminBetMeta"><div>סכום<b>'+money(b.stake)+'</b></div><div>יחס<b>'+Number(b.total_odd||0).toFixed(2)+'</b></div><div>זכייה<b>'+money(b.potential_win)+'</b></div><div>שולם ע״י<b>'+(b.paid_by?esc(b.paid_by):'-')+'</b></div></div><div class="adminBetPicks">'+picks.map(p=>esc((p.g||'')+' • '+(p.l||''))).join('<br>')+'</div><div class="adminBetControls">'+adminBetButtons(b)+'</div>'+(b.prize_paid_at?'<div class="small" style="margin-top:7px">מסירת פרס: '+fmtDate(b.prize_paid_at)+(b.prize_paid_by?' • '+esc(b.prize_paid_by):'')+'</div>':'')+'</article>'}).join(''):'<div class="muted">אין הימורים במאגר</div>'}catch(e){box.innerHTML='<div class="statusMsg error">'+esc(e.message)+'</div>'}}
$("#refreshAdminBets").onclick=adminAllBets;'''
s=s[:start]+new_js+s[end:]

p.write_text(s,encoding='utf-8')
print('Admin bet controls applied')
