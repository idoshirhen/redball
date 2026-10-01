from pathlib import Path

p=Path('betting.html')
s=p.read_text(encoding='utf-8')
old='''const visibleRounds=rounds.filter(r=>r.customer_visible!==false&&(byRound.get(Number(r.round_no))||[]).length);const hasFuture=r=>(byRound.get(Number(r.round_no))||[]).some(g=>!g.starts_at||new Date(g.starts_at).getTime()>now);if(!visibleRounds.some(r=>r.round_no===activeRound)){const preferred=visibleRounds.find(r=>r.is_open&&hasFuture(r))||visibleRounds.find(r=>hasFuture(r))||visibleRounds[visibleRounds.length-1];activeRound=preferred?.round_no||activeRound}$("#roundNav").innerHTML=visibleRounds.length?visibleRounds.map(r=>'''
new='''const hasFuture=r=>(byRound.get(Number(r.round_no))||[]).some(g=>!g.starts_at||new Date(g.starts_at).getTime()>now);const visibleRounds=rounds.filter(r=>r.customer_visible!==false&&(byRound.get(Number(r.round_no))||[]).length).sort((a,b)=>{const ao=a.is_open?0:1,bo=b.is_open?0:1;if(ao!==bo)return ao-bo;const af=hasFuture(a)?0:1,bf=hasFuture(b)?0:1;if(af!==bf)return af-bf;return Number(a.round_no)-Number(b.round_no)});const activeSessionCandidate=visibleRounds.find(r=>Number(r.round_no)===Number(activeRound));if(!activeSessionCandidate||!activeSessionCandidate.is_open){const preferred=visibleRounds.find(r=>r.is_open&&hasFuture(r))||visibleRounds.find(r=>r.is_open)||visibleRounds.find(r=>hasFuture(r))||visibleRounds[0];activeRound=preferred?.round_no||activeRound}$("#roundNav").innerHTML=visibleRounds.length?visibleRounds.map(r=>'''
if old not in s:
    raise SystemExit('target block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
