import { createClient } from 'npm:@supabase/supabase-js@2'
const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"content-type, apikey, x-client-info, x-admin-token","Access-Control-Allow-Methods":"GET, POST, OPTIONS"}
const json=(b:any,s=200)=>new Response(JSON.stringify(b),{status:s,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})
const sha256=async(value:string)=>{const d=new TextEncoder().encode(value);const h=await crypto.subtle.digest('SHA-256',d);return Array.from(new Uint8Array(h)).map(b=>b.toString(16).padStart(2,'0')).join('')}
const uaOf=(req:Request)=>String(req.headers.get('user-agent')||'unknown').slice(0,400)

type TeamMap={country:string,aliases:string[]}
const teams:Record<string,TeamMap>={
'לאנס':{country:'FRA',aliases:['RC Lens','Lens']},'ספורטינג ליסבון':{country:'PRT',aliases:['Sporting CP','Sporting Clube de Portugal']},'סבאח':{country:'AZE',aliases:['Sabah FK']},'סלביה פראג':{country:'CZE',aliases:['Slavia Praha','SK Slavia Praha']},'ארסנל':{country:'ENG',aliases:['Arsenal FC','Arsenal']},'ליל':{country:'FRA',aliases:['LOSC Lille','Lille OSC','Lille']},'גלאטסראיי':{country:'TUR',aliases:['Galatasaray']},'ברצלונה':{country:'ESP',aliases:['FC Barcelona','Barcelona']},'ר.ב לייפציג':{country:'DEU',aliases:['RB Leipzig']},'ר.ב. לייפציג':{country:'DEU',aliases:['RB Leipzig']},'פ.ס.וו איינדהובן':{country:'NLD',aliases:['PSV Eindhoven','PSV']},'ויקינג':{country:'NOR',aliases:['Viking FK','Viking']},'באיירן מינכן':{country:'DEU',aliases:['Bayern München','Bayern Munich']},'אינטר':{country:'ITA',aliases:['Inter','Inter Milan']},"ברוז'":{country:'BEL',aliases:['Club Brugge KV','Club Brugge']},"קלאב ברוז'":{country:'BEL',aliases:['Club Brugge KV','Club Brugge']},'אתלטיקו מדריד':{country:'ESP',aliases:['Atlético Madrid','Atletico Madrid']},"מנצ'סטר יונייטד":{country:'ENG',aliases:['Manchester United']},'ויאריאל':{country:'ESP',aliases:['Villarreal CF','Villarreal']},'נאפולי':{country:'ITA',aliases:['SSC Napoli','Napoli']},"פנרבחצ'ה":{country:'TUR',aliases:['Fenerbahçe','Fenerbahce']},'דורטמונד':{country:'DEU',aliases:['Borussia Dortmund']},'בורוסיה דורטמונד':{country:'DEU',aliases:['Borussia Dortmund']},'שטוטגרט':{country:'DEU',aliases:['VfB Stuttgart','Stuttgart']},"פריז סן ז'רמן":{country:'FRA',aliases:['Paris Saint-Germain','Paris SG','PSG']},'בודו גלימט':{country:'NOR',aliases:['FK Bodø/Glimt','Bodø/Glimt','Bodo/Glimt']},'בודה/גלימט':{country:'NOR',aliases:['FK Bodø/Glimt','Bodø/Glimt','Bodo/Glimt']},'ליברפול':{country:'ENG',aliases:['Liverpool FC','Liverpool']},'פורטו':{country:'PRT',aliases:['FC Porto','Porto']},'רומא':{country:'ITA',aliases:['AS Roma','Roma']},'סלובן ברטיסלבה':{country:'SVK',aliases:['Slovan Bratislava','ŠK Slovan Bratislava']},"מנצ'סטר סיטי":{country:'ENG',aliases:['Manchester City']},'א.א.ק אתונה':{country:'GRC',aliases:['AEK Athens','AEK Athens FC']},'קומו':{country:'ITA',aliases:['Como 1907','Como']},'לאסק':{country:'AUT',aliases:['LASK Linz','LASK']},'לאסק לינץ':{country:'AUT',aliases:['LASK Linz','LASK']},'אסטון וילה':{country:'ENG',aliases:['Aston Villa']},'ריאל מדריד':{country:'ESP',aliases:['Real Madrid']},'שחטאר דונייצק':{country:'UKR',aliases:['Shakhtar Donetsk','FC Shakhtar Donetsk']},'ריאל בטיס':{country:'ESP',aliases:['Real Betis']},'פיינורד':{country:'NLD',aliases:['Feyenoord Rotterdam','Feyenoord']},'אויפן':{country:'BEL',aliases:['KAS Eupen','AS Eupen','Eupen']},'אלמניה אאכן':{country:'DEU',aliases:['Alemannia Aachen']},'יאן רגנסבורג':{country:'DEU',aliases:['SSV Jahn Regensburg','Jahn Regensburg']},'WSG טירול':{country:'AUT',aliases:['WSG Tirol','WSG Wattens']},'גרויטר פירת':{country:'DEU',aliases:['SpVgg Greuther Fürth','Greuther Fürth','Greuther Furth']},'סאוטה':{country:'ESP',aliases:['AD Ceuta FC','Ceuta']}
,'ורדר ברמן':{country:'DEU',aliases:['Werder','Werder Bremen','SV Werder Bremen']},'ליון':{country:'FRA',aliases:['Olympique Lyon','Olympique Lyonnais','Lyon']},'מלאגה':{country:'ESP',aliases:['Malaga CF','Málaga CF','Malaga']},'אספניול':{country:'ESP',aliases:['Espanyol Barcelona','RCD Espanyol','Espanyol']},'לידס':{country:'ENG',aliases:['Leeds','Leeds United','Leeds United FC']},'טוטנהאם':{country:'ENG',aliases:['Tottenham Hotspur','Tottenham']},'צ\'לסי':{country:'ENG',aliases:['Chelsea FC','Chelsea']},'בורנמות\'':{country:'ENG',aliases:['AFC Bournemouth','Bournemouth']},'אוגסבורג':{country:'DEU',aliases:['FC Augsburg','Augsburg']},'חטאפה':{country:'ESP',aliases:['Getafe CF','Getafe']},'פארמה':{country:'ITA',aliases:['Parma Calcio','Parma']},'פרוזינונה':{country:'ITA',aliases:['Frosinone Calcio','Frosinone']},'לה מאן':{country:'FRA',aliases:['Le Mans FC','Le Mans']},'ססואולו':{country:'ITA',aliases:['Sassuolo Calcio','US Sassuolo','Sassuolo']},'מילאן':{country:'ITA',aliases:['AC Milan','Milan']},'קליארי':{country:'ITA',aliases:['Cagliari Calcio','Cagliari']},'יובנטוס':{country:'ITA',aliases:['Juventus Turin','Juventus FC','Juventus']},'טרואה':{country:'FRA',aliases:['ESTAC Troyes','Troyes']},'מארסיי':{country:'FRA',aliases:['Olympique Marseille','Olympique de Marseille','Marseille']},'אוסאסונה':{country:'ESP',aliases:['CA Osasuna','Osasuna']},'ראסינג סנטנדר':{country:'ESP',aliases:['Racing Santander','Racing de Santander']},'ולנסיה':{country:'ESP',aliases:['Valencia CF','Valencia']}}

Object.assign(teams,{
'הפועל באר שבע':{country:'ISR',aliases:['Beer-Sheva','Hapoel Beer Sheva','Hapoel Beersheba']},
'מכבי תל אביב':{country:'ISR',aliases:['Maccabi Tel Aviv']},
'מכבי חיפה':{country:'ISR',aliases:['Maccabi Haifa']},
'בית"ר ירושלים':{country:'ISR',aliases:['Beitar','Beitar Jerusalem']},
'הפועל תל אביב':{country:'ISR',aliases:['Hapoel Tel Aviv']},
'הפועל חיפה':{country:'ISR',aliases:['Hapoel Haifa']},
'מכבי נתניה':{country:'ISR',aliases:['Netanya','Maccabi Netanya']},
'הפועל ירושלים':{country:'ISR',aliases:['Hapoel Jerusalem']},
'הפועל פתח תקווה':{country:'ISR',aliases:['H Petach Tikva','Hapoel Petah Tikva','Hapoel Petach Tikva']},
'עירוני טבריה':{country:'ISR',aliases:['Ironi Tiberias']},
'עירוני קריית שמונה':{country:'ISR',aliases:['Kiryat Shmona','Ironi Kiryat Shmona']},
'בני סכנין':{country:'ISR',aliases:['Bnei Sakhinin','Bnei Sakhnin']},
'מכבי פתח תקווה':{country:'ISR',aliases:['M Petach Tikva','Maccabi Petah Tikva','Maccabi Petach Tikva']},
'הפועל רמת גן':{country:'ISR',aliases:['Hapoel Ramat Gan']}
})

Object.assign(teams,{
'ברייטון':{country:'ENG',aliases:['Brighton','Brighton & Hove Albion','Brighton and Hove Albion']},
'איינטרכט פרנקפורט':{country:'DEU',aliases:['Eintracht Frankfurt','Frankfurt']},
'המבורג':{country:'DEU',aliases:['Hamburger SV','Hamburg','HSV']},
'פיורנטינה':{country:'ITA',aliases:['Fiorentina','ACF Fiorentina']},
'אודינזה':{country:'ITA',aliases:['Udinese','Udinese Calcio']},
'פרייבורג':{country:'DEU',aliases:['Freiburg','SC Freiburg']},
'מונאקו':{country:'FRA',aliases:['Monaco','AS Monaco']}
})

const nationalTeams:Record<string,{country:string,aliases:string[]}>={
'ישראל':{country:'ISR',aliases:['Israel']},'ספרד':{country:'ESP',aliases:['Spain']},'צרפת':{country:'FRA',aliases:['France']},'גרמניה':{country:'DEU',aliases:['Germany']},'איטליה':{country:'ITA',aliases:['Italy']},'אנגליה':{country:'ENG',aliases:['England']},'פורטוגל':{country:'PRT',aliases:['Portugal']},'הולנד':{country:'NLD',aliases:['Netherlands']},'בלגיה':{country:'BEL',aliases:['Belgium']},'קרואטיה':{country:'HRV',aliases:['Croatia']},'דנמרק':{country:'DNK',aliases:['Denmark']},'שוויץ':{country:'CHE',aliases:['Switzerland']},'אוסטריה':{country:'AUT',aliases:['Austria']},'נורווגיה':{country:'NOR',aliases:['Norway']},'שוודיה':{country:'SWE',aliases:['Sweden']},'פולין':{country:'POL',aliases:['Poland']},'יוון':{country:'GRC',aliases:['Greece']},'טורקיה':{country:'TUR',aliases:['Turkey','Türkiye']},'סרביה':{country:'SRB',aliases:['Serbia']},'אוקראינה':{country:'UKR',aliases:['Ukraine']},'צכיה':{country:'CZE',aliases:['Czech Republic','Czechia']},'אירלנד':{country:'IRL',aliases:['Republic of Ireland','Ireland']},'סקוטלנד':{country:'SCO',aliases:['Scotland']},'ויילס':{country:'WAL',aliases:['Wales']},'ארגנטינה':{country:'ARG',aliases:['Argentina']},'ברזיל':{country:'BRA',aliases:['Brazil']},'אורוגוואי':{country:'URY',aliases:['Uruguay']},'קולומביה':{country:'COL',aliases:['Colombia']},'ארה"ב':{country:'USA',aliases:['USA','United States']},'מקסיקו':{country:'MEX',aliases:['Mexico']},'יפן':{country:'JPN',aliases:['Japan']},'דרום קוריאה':{country:'KOR',aliases:['Korea Republic','South Korea']},'מרוקו':{country:'MAR',aliases:['Morocco']},'מצרים':{country:'EGY',aliases:['Egypt']},'ניגריה':{country:'NGA',aliases:['Nigeria']},'גאנה':{country:'GHA',aliases:['Ghana']},'סלובניה':{country:'SVN',aliases:['Slovenia']},'צפון מקדוניה':{country:'MKD',aliases:['North Macedonia','North Macedonia FYR','FYR Macedonia']},'אלבניה':{country:'ALB',aliases:['Albania']},'סן מרינו':{country:'SMR',aliases:['San Marino']},'בלארוס':{country:'BLR',aliases:['Belarus']},'פינלנד':{country:'FIN',aliases:['Finland']},'קזחסטן':{country:'KAZ',aliases:['Kazakhstan']},'איי פארו':{country:'FRO',aliases:['Faroe Islands','Faroe Islands']},'מולדובה':{country:'MDA',aliases:['Moldova']},'סלובקיה':{country:'SVK',aliases:['Slovakia']},'אסטוניה':{country:'EST',aliases:['Estonia']},'איסלנד':{country:'ISL',aliases:['Iceland']},'לוקסמבורג':{country:'LUX',aliases:['Luxembourg']},'בולגריה':{country:'BGR',aliases:['Bulgaria']}
}

const normName=(v:string)=>String(v||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9\u0590-\u05ff]+/g,' ').replace(/\b(fc|cf|fk|sc|afc|ac|ssc|sv|vfb|spvgg|kv)\b/g,' ').replace(/\s+/g,' ').trim()
const aliasesFor=(name:string)=>[name,...(teams[name]?.aliases||[]),...(nationalTeams[name]?.aliases||[])].map(normName).filter(Boolean)
const nameScore=(wanted:string,actual:string)=>{const a=normName(actual);let best=0;for(const w of aliasesFor(wanted)){if(w===a)best=Math.max(best,3);else if(a.includes(w)||w.includes(a))best=Math.max(best,2);else{const wt=new Set(w.split(' ')),at=new Set(a.split(' '));let common=0;wt.forEach(x=>{if(x&&at.has(x))common++});if(common>=2)best=Math.max(best,1)}}return best}
function findFixture(home:string,away:string,starts:Date,fixtures:any[]){const timed=(fixtures||[]).filter((x:any)=>{const d=x?.fixture?.date?new Date(x.fixture.date):null;return d&&!Number.isNaN(d.getTime())&&Math.abs(d.getTime()-starts.getTime())<=30*60*1000});const ranked=timed.map((x:any)=>({x,hs:nameScore(home,x?.teams?.home?.name||''),as:nameScore(away,x?.teams?.away?.name||''),dt:Math.abs(new Date(x.fixture.date).getTime()-starts.getTime())})).sort((a:any,b:any)=>(b.hs+b.as)-(a.hs+a.as)||a.dt-b.dt);const best=ranked[0];if(best&&best.hs>=2&&best.as>=2)return best.x;if(timed.length===1&&best&&best.dt<=2*60*1000&&(best.hs>=2||best.as>=2))return best.x;return null}
Deno.serve(async(req)=>{
 if(req.method==='OPTIONS') return new Response('ok',{headers:cors})
 if(req.method!=='GET'&&req.method!=='POST') return json({error:'Method not allowed'},405)
 try{
  const s=createClient(Deno.env.get('SUPABASE_URL')!,Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,{auth:{persistSession:false,autoRefreshToken:false}})
  let manualRole=''
  if(req.method==='POST'){
   const token=req.headers.get('x-admin-token')||''
   if(!token||token.length<60)return json({error:'Unauthorized'},401)
   const tokenHash=await sha256(token),userAgentHash=await sha256(uaOf(req)),now=new Date(),nowIso=now.toISOString(),idleCutoff=new Date(now.getTime()-12*60*60*1000).toISOString()
   const {data:session,error:sessionError}=await s.from('admin_sessions').select('token_hash,user_agent_hash,last_seen_at,expires_at,scope,admin_role').eq('token_hash',tokenHash).eq('scope','betting').gt('expires_at',nowIso).gt('last_seen_at',idleCutoff).maybeSingle()
   if(sessionError)throw sessionError
   if(!session||session.user_agent_hash!==userAgentHash)return json({error:'Session expired'},401)
   manualRole=String(session.admin_role||'sani')
   if(!['sani','vladi'].includes(manualRole))return json({error:'אין הרשאה למשיכת תוצאות'},403)
   await s.from('admin_sessions').update({last_seen_at:nowIso}).eq('token_hash',tokenHash).eq('scope','betting')
  }
  const key=Deno.env.get('API_FOOTBALL_KEY')
  if(!key) return json({error:'API_FOOTBALL_KEY secret is missing'},500)
  const AUTO_ARCHIVE_DELAY_MS=3*60*60*1000
  const autoArchiveCompletedSessions=async()=>{
    const {data:roundRows,error:re}=await s.from('betting_rounds').select('round_no,name,archived_at').is('archived_at',null)
    if(re)throw re
    const archived:any[]=[]
    for(const r of roundRows||[]){
      const {data:gs,error:ge}=await s.from('betting_games').select('id,result,result_set_at').eq('round_no',r.round_no)
      if(ge)throw ge
      if(!(gs||[]).length)continue
      if(!(gs||[]).every((g:any)=>g.result!=null))continue
      const stamps=(gs||[]).map((g:any)=>g.result_set_at?new Date(g.result_set_at).getTime():NaN).filter((x:number)=>Number.isFinite(x))
      if(stamps.length!==(gs||[]).length)continue
      const completedAt=Math.max(...stamps)
      if(Date.now()-completedAt<AUTO_ARCHIVE_DELAY_MS)continue
      const nowIso=new Date().toISOString()
      const {error:ue}=await s.from('betting_rounds').update({is_open:false,customer_visible:false,archived_at:nowIso,updated_at:nowIso}).eq('round_no',r.round_no).is('archived_at',null)
      if(!ue)archived.push({round_no:r.round_no,name:r.name,completed_at:new Date(completedAt).toISOString()})
    }
    return archived
  }

  const expireUnpaidBets=async()=>{
    const {data:bets,error:be}=await s.from('bets').select('id,bet_code,picks,payment_status,result_status').eq('payment_status','pending').eq('result_status','pending')
    if(be)throw be
    const rows=bets||[]
    const ids=[...new Set(rows.flatMap((b:any)=>Array.isArray(b.picks)?b.picks.map((p:any)=>String(p?.game_id||'')).filter(Boolean):[]))]
    if(!ids.length)return []
    const {data:games,error:ge}=await s.from('betting_games').select('id,starts_at').in('id',ids)
    if(ge)throw ge
    const starts=new Map((games||[]).map((g:any)=>[String(g.id),g.starts_at?new Date(g.starts_at).getTime():Number.POSITIVE_INFINITY]))
    const nowMs=Date.now(),expired:any[]=[]
    for(const b of rows){
      const first=Math.min(...(Array.isArray(b.picks)?b.picks.map((p:any)=>starts.get(String(p?.game_id||''))??Number.POSITIVE_INFINITY):[Number.POSITIVE_INFINITY]))
      if(!Number.isFinite(first)||first>nowMs)continue
      const nowIso=new Date().toISOString()
      const {data:updated,error:ue}=await s.from('bets').update({result_status:'cancelled',cancelled_from_status:'pending',cancelled_at:nowIso,cancel_reason:'unpaid_before_kickoff',prize_paid:false,prize_paid_at:null,prize_paid_by:null}).eq('id',b.id).eq('payment_status','pending').eq('result_status','pending').select('id,bet_code')
      if(ue)throw ue
      if(updated?.length)expired.push({id:b.id,bet_code:b.bet_code})
    }
    return expired
  }
  const localDate=(value:string|Date)=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Jerusalem',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(value))
  const u=new URL(req.url),requestedDate=u.searchParams.get('date'),date=requestedDate||localDate(new Date())
  if(requestedDate&&!/^\d{4}-\d{2}-\d{2}$/.test(requestedDate))return json({error:'Invalid date'},400)
  // First, automatically attach missing API-Football Fixture IDs for games whose date is today or tomorrow.
  const today=localDate(new Date()),tomorrow=localDate(new Date(Date.now()+24*60*60*1000))
  const localClock=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Jerusalem',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date()),[localHour,localMinute]=localClock.split(':').map(Number)
  let linkCandidates:any[]=[]
  {
    let q=s.from('betting_games').select('id,home_team,away_team,starts_at,elo_status,api_link_status,api_fixture_id,result,league_name').is('result',null).neq('league_name','UFC').or('api_fixture_id.is.null,api_link_status.neq.verified')
    if(!requestedDate)q=q.gte('starts_at',new Date(Date.now()-12*60*60*1000).toISOString())
    const {data:missingLinks,error:mle}=await q
    if(mle)throw mle
    linkCandidates=(missingLinks||[]).filter((g:any)=>{
      if(!g.starts_at)return false
      const d=localDate(g.starts_at)
      return requestedDate?d===date:[today,tomorrow].includes(d)
    })
  }
  const linkDates=[...new Set(linkCandidates.map((g:any)=>localDate(g.starts_at)))]
  const linked:any[]=[];const link_debug:any[]=[]
  for(const linkDate of linkDates){
    const lr=await fetch('https://v3.football.api-sports.io/fixtures?date='+encodeURIComponent(linkDate)+'&timezone='+encodeURIComponent('Asia/Jerusalem'),{headers:{'x-apisports-key':key}})
    const ld=await lr.json().catch(()=>({}))
    const headerRemaining=Number(lr.headers.get('x-ratelimit-requests-remaining')),headerLimit=Number(lr.headers.get('x-ratelimit-requests-limit'))
    await s.from('football_api_quota_state').upsert({provider:'api-football',quota_day:new Date().toISOString().slice(0,10),quota_limit:Number.isFinite(headerLimit)?headerLimit:null,remaining:Number.isFinite(headerRemaining)?headerRemaining:null,last_call_at:new Date().toISOString(),updated_at:new Date().toISOString()},{onConflict:'provider'})
    const fixtures=Array.isArray(ld.response)?ld.response:[]
    if(requestedDate)link_debug.push({date:linkDate,status:lr.status,error:ld.errors||null,message:ld.message||null,fixtures_count:fixtures.length,sample:fixtures.slice(0,25).map((x:any)=>({id:x?.fixture?.id,date:x?.fixture?.date,status:x?.fixture?.status?.short,league:x?.league?.name,home:x?.teams?.home?.name,away:x?.teams?.away?.name,home_goals:x?.goals?.home,away_goals:x?.goals?.away}))})
    if(!lr.ok||Object.keys(ld.errors||{}).length)continue
    for(const g of linkCandidates.filter((x:any)=>localDate(x.starts_at)===linkDate)){
      const fx=findFixture(g.home_team,g.away_team,new Date(g.starts_at),fixtures);if(!fx)continue
      const fid=Number(fx.fixture?.id);if(!fid)continue
      const {error:ue}=await s.from('betting_games').update({api_provider:'api-football',api_fixture_id:fid,api_link_status:'verified',api_home_name:fx.teams?.home?.name||null,api_away_name:fx.teams?.away?.name||null,api_status:String(fx.fixture?.status?.short||'NS'),league_name:fx.league?.name||null,verification_note:g.elo_status==='verified'?'Elo מאומת + API-Football מאומתים':'API-Football מאומת; ממתין ל-Elo'}).eq('id',g.id)
      if(!ue)linked.push({id:g.id,home_team:g.home_team,away_team:g.away_team,fixture_id:fid})
    }
  }
  // Fallback for Israeli Premier League final results when API-Football is unavailable/suspended.
  const fallback_updated:any[]=[]
  try{
    const {data:isrGames,error:ise}=await s.from('betting_games')
      .select('id,home_team,away_team,starts_at,result,league_name')
      .eq('league_name','Israeli Premier League')
      .is('result',null)
      .not('starts_at','is',null)
    if(ise)throw ise
    const nowFallback=Date.now(),isrTargets=(isrGames||[]).filter((g:any)=>{
      const t=new Date(g.starts_at).getTime()
      return Number.isFinite(t)&&t<=nowFallback&&t>=nowFallback-30*60*60*1000
    })
    if(isrTargets.length){
      const fr=await fetch('https://www.thefishy.net/football-results.php?table=326',{headers:{'user-agent':'Mozilla/5.0 RedBallResultsBot/1.0'}})
      if(fr.ok){
        const html=await fr.text()
        const strip=(v:string)=>v.replace(/<[^>]*>/g,'').replace(/&amp;/g,'&').replace(/&#39;/g,"'").replace(/&quot;/g,'"').replace(/&nbsp;/g,' ').replace(/&#8209;/g,'-').replace(/\s+/g,' ').trim()
        for(const g of isrTargets){
          const d=new Date(g.starts_at)
          const localParts=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Jerusalem',weekday:'short',day:'2-digit',month:'short',year:'numeric'}).formatToParts(d)
          const part=(type:string)=>localParts.find((x:any)=>x.type===type)?.value||''
          const label=part('weekday')+' '+part('day')+'-'+part('month')+'-'+part('year')
          const head="<tr class='success'><th colspan='5'>"+label+"</th></tr>"
          const start=html.indexOf(head)
          if(start<0)continue
          const next=html.indexOf("<tr class='success'>",start+head.length)
          const section=html.slice(start,next>start?next:Math.min(html.length,start+12000))
          const rowRe=/<tr class='cats'><td>[^<]*<\/td><td class='home'>([\s\S]*?)<\/td><td class='catsc'>([\s\S]*?)<\/td><td>([\s\S]*?)<\/td><td/gi
          let m:any
          while((m=rowRe.exec(section))){
            const home=strip(m[1]),scoreText=strip(m[2]),away=strip(m[3])
            const sm=scoreText.match(/(\d+)\s*-\s*(\d+)/)
            if(!sm)continue
            if(nameScore(g.home_team,home)<2||nameScore(g.away_team,away)<2)continue
            const hg=Number(sm[1]),ag=Number(sm[2]),res=hg>ag?'1':hg<ag?'2':'X',nowIso=new Date().toISOString()
            const {data:upd,error:ufe}=await s.from('betting_games').update({
              result:res,api_home_goals:hg,api_away_goals:ag,api_status:'FT',api_last_synced_at:nowIso,result_set_at:nowIso,
              needs_review:false,review_reason:null,verification_note:'Fallback result source verified: TheFishy'
            }).eq('id',g.id).is('result',null).select('id,home_team,away_team,result,api_home_goals,api_away_goals')
            if(ufe)throw ufe
            if(upd?.length)fallback_updated.push(...upd)
            break
          }
        }
      }
    }
  }catch(e){console.error('Israeli fallback sync failed',e)}

  // Official UEFA fallback for Champions League finals.
  // This keeps results working even if API-Football is suspended or unavailable.
  const uefa_fallback_updated:any[]=[]
  try{
    const {data:uclGames,error:ucle}=await s.from('betting_games')
      .select('id,home_team,away_team,starts_at,result,league_name')
      .eq('league_name','UEFA Champions League')
      .is('result',null)
      .not('starts_at','is',null)
    if(ucle)throw ucle
    const nowUefa=Date.now(),uclTargets=(uclGames||[]).filter((g:any)=>{
      const t=new Date(g.starts_at).getTime()
      return Number.isFinite(t)&&t<=nowUefa&&t>=nowUefa-36*60*60*1000
    })
    if(uclTargets.length){
      const ur=await fetch('https://fr.uefa.com/uefachampionsleague/news/02a8-217680c70b8d-878c5efa7b92-1000--ligue-des-champions-2026-27-calendrier-et-resultats-de-la/',{
        headers:{'user-agent':'Mozilla/5.0 RedBallResultsBot/1.0','accept':'text/html,application/xhtml+xml'}
      })
      if(ur.ok){
        const html=await ur.text()
        const decode=(v:string)=>v
          .replace(/<[^>]*>/g,' ')
          .replace(/&nbsp;|&#xA0;|&#160;/gi,' ')
          .replace(/&amp;/gi,'&')
          .replace(/&quot;/gi,'"')
          .replace(/&#39;|&apos;/gi,"'")
          .replace(/&#x([0-9a-f]+);/gi,(_m,h)=>String.fromCodePoint(parseInt(h,16)))
          .replace(/&#([0-9]+);/g,(_m,d)=>String.fromCodePoint(parseInt(d,10)))
          .replace(/\s+/g,' ').trim()
        const scored:any[]=[]
        const anchorRe=/<a\b[^>]*>([\s\S]*?)<\/a>/gi
        let am:any
        while((am=anchorRe.exec(html))){
          const text=decode(am[1])
          const sm=text.match(/^(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+?)$/)
          if(!sm)continue
          scored.push({home:sm[1].trim(),hg:Number(sm[2]),ag:Number(sm[3]),away:sm[4].trim()})
        }
        for(const g of uclTargets){
          const matches=scored
            .map((x:any)=>({...x,hs:nameScore(g.home_team,x.home),as:nameScore(g.away_team,x.away)}))
            .filter((x:any)=>x.hs>=2&&x.as>=2)
            .sort((a:any,b:any)=>(b.hs+b.as)-(a.hs+a.as))
          const best=matches[0]
          if(!best)continue
          const res=best.hg>best.ag?'1':best.hg<best.ag?'2':'X',nowIso=new Date().toISOString()
          const {data:upd,error:ue}=await s.from('betting_games').update({
            result:res,api_home_goals:best.hg,api_away_goals:best.ag,api_status:'FT',
            api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'UEFA_FALLBACK',
            needs_review:false,review_reason:null,
            verification_note:'Final result verified via official UEFA fallback'
          }).eq('id',g.id).is('result',null)
            .select('id,home_team,away_team,result,api_home_goals,api_away_goals')
          if(ue)throw ue
          if(upd?.length)uefa_fallback_updated.push(...upd)
        }
      }
    }
  }catch(e){console.error('UEFA fallback sync failed',e)}

  // Generic ESPN fallback: covers Champions League, Nations League, top European leagues and UFC.
  // It is intentionally independent from API-Football and only settles completed events with strong name matching.
  const espn_fallback_updated:any[]=[]
  try{
    const soccerSlug:Record<string,string>={
      'UEFA Champions League':'uefa.champions',
      'UEFA Nations League':'uefa.nations',
      'Premier League':'eng.1',
      'LaLiga':'esp.1',
      'La Liga':'esp.1',
      'Serie A':'ita.1',
      'Bundesliga':'ger.1',
      'Ligue 1':'fra.1',
      'EFL Cup':'eng.league_cup',
      'Carabao Cup':'eng.league_cup',
      'גביע הליגה האנגלי':'eng.league_cup',
      'DFB-Pokal':'ger.dfb_pokal',
      'גביע גרמני':'ger.dfb_pokal',
      'FIFA World Cup Qualifying - UEFA':'fifa.worldq.uefa',
      'International Friendly':'fifa.friendly',
      'UEFA European Championship Qualifying':'uefa.euro.qualifying'
    }
    const {data:pendingGames,error:pge}=await s.from('betting_games')
      .select('id,home_team,away_team,starts_at,result,league_name')
      .is('result',null)
      .not('starts_at','is',null)
    if(pge)throw pge

    const nowEspn=Date.now()
    const pending=(pendingGames||[]).filter((g:any)=>{
      const t=new Date(g.starts_at).getTime()
      return Number.isFinite(t)&&t<=nowEspn&&t>=nowEspn-36*60*60*1000
    })

    const dateKey=(v:string)=>localDate(v).replace(/-/g,'')
    const groups=new Map<string,any[]>()
    for(const g of pending){
      const league=String(g.league_name||'')
      let endpoint=''
      if(soccerSlug[league])endpoint='https://site.api.espn.com/apis/site/v2/sports/soccer/'+soccerSlug[league]+'/scoreboard?dates='+dateKey(g.starts_at)
      else if(league.toUpperCase()==='UFC')endpoint='https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard?dates='+dateKey(g.starts_at)
      else continue
      if(!groups.has(endpoint))groups.set(endpoint,[])
      groups.get(endpoint)!.push(g)
    }

    for(const [endpoint,group] of groups){
      const er=await fetch(endpoint,{headers:{'user-agent':'Mozilla/5.0 RedBallResultsBot/2.0','accept':'application/json'}})
      if(!er.ok)continue
      const ed=await er.json().catch(()=>({}))
      const events=Array.isArray(ed.events)?ed.events:[]

      const soccerCandidates:any[]=[]
      const combatCandidates:any[]=[]
      for(const ev of events){
        for(const comp of (Array.isArray(ev?.competitions)?ev.competitions:[])){
          const completed=!!comp?.status?.type?.completed
          const competitors=Array.isArray(comp?.competitors)?comp.competitors:[]
          if(competitors.length<2)continue
          const home=competitors.find((x:any)=>x?.homeAway==='home')
          const away=competitors.find((x:any)=>x?.homeAway==='away')
          if(home&&away){
            soccerCandidates.push({
              completed,
              date:comp?.date||ev?.date||null,
              home:String(home?.team?.displayName||home?.team?.name||''),
              away:String(away?.team?.displayName||away?.team?.name||''),
              hg:Number(home?.score),ag:Number(away?.score)
            })
          }else{
            const a=competitors[0],b=competitors[1]
            combatCandidates.push({
              completed,
              date:comp?.date||ev?.date||null,
              a:String(a?.athlete?.fullName||a?.athlete?.displayName||''),
              b:String(b?.athlete?.fullName||b?.athlete?.displayName||''),
              awin:!!a?.winner,bwin:!!b?.winner
            })
          }
        }
      }

      for(const g of group){
        const isCombat=String(g.league_name||'').toUpperCase()==='UFC'
        if(isCombat){
          let best:any=null,bestScore=0,bestFlip=false
          for(const x of combatCandidates){
            if(!x.completed)continue
            const direct=nameScore(g.home_team,x.a)+nameScore(g.away_team,x.b)
            const flip=nameScore(g.home_team,x.b)+nameScore(g.away_team,x.a)
            if(direct>bestScore){best=x;bestScore=direct;bestFlip=false}
            if(flip>bestScore){best=x;bestScore=flip;bestFlip=true}
          }
          if(!best||bestScore<4)continue
          const firstWins=bestFlip?best.bwin:best.awin
          const secondWins=bestFlip?best.awin:best.bwin
          if(firstWins===secondWins)continue
          const res=firstWins?'1':'2',nowIso=new Date().toISOString()
          const {data:upd,error:ue}=await s.from('betting_games').update({
            result:res,api_status:'FT',api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'ESPN_FALLBACK',
            needs_review:false,review_reason:null,verification_note:'Final result verified via ESPN fallback'
          }).eq('id',g.id).is('result',null).select('id,home_team,away_team,result')
          if(ue)throw ue
          if(upd?.length)espn_fallback_updated.push(...upd)
        }else{
          let best:any=null,bestScore=0
          for(const x of soccerCandidates){
            if(!x.completed||!Number.isFinite(x.hg)||!Number.isFinite(x.ag))continue
            const score=nameScore(g.home_team,x.home)+nameScore(g.away_team,x.away)
            if(score>bestScore){best=x;bestScore=score}
          }
          if(!best||bestScore<4)continue
          const hg=Number(best.hg),ag=Number(best.ag),res=hg>ag?'1':hg<ag?'2':'X',nowIso=new Date().toISOString()
          const {data:upd,error:ue}=await s.from('betting_games').update({
            result:res,api_home_goals:hg,api_away_goals:ag,api_status:'FT',
            api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'ESPN_FALLBACK',
            needs_review:false,review_reason:null,verification_note:'Final result verified via ESPN fallback'
          }).eq('id',g.id).is('result',null).select('id,home_team,away_team,result,api_home_goals,api_away_goals')
          if(ue)throw ue
          if(upd?.length)espn_fallback_updated.push(...upd)
        }
      }
    }
  }catch(e){console.error('ESPN fallback sync failed',e)}

  // TheSportsDB fallback: independent secondary source for football/UFC final results.
  // Free V1 is intentionally used only as a fallback; premium can later expand coverage without changing this flow.
  const sportsdb_fallback_updated:any[]=[]
  try{
    const {data:pendingSports,error:pse}=await s.from('betting_games')
      .select('id,home_team,away_team,starts_at,result,league_name')
      .is('result',null)
      .not('starts_at','is',null)
    if(pse)throw pse
    const nowSports=Date.now()
    const pending=(pendingSports||[]).filter((g:any)=>{
      const t=new Date(g.starts_at).getTime()
      return Number.isFinite(t)&&t<=nowSports&&t>=nowSports-36*60*60*1000
    })
    const byDateSport=new Map<string,any[]>()
    for(const g of pending){
      const sport=String(g.league_name||'').toUpperCase()==='UFC'?'MMA':'Soccer'
      const key=localDate(g.starts_at)+'|'+sport
      if(!byDateSport.has(key))byDateSport.set(key,[])
      byDateSport.get(key)!.push(g)
    }
    for(const [key,group] of byDateSport){
      const [day,sport]=key.split('|')
      const tr=await fetch('https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d='+encodeURIComponent(day)+'&s='+encodeURIComponent(sport),{
        headers:{'user-agent':'Mozilla/5.0 RedBallResultsBot/3.0','accept':'application/json'}
      })
      if(!tr.ok)continue
      const td=await tr.json().catch(()=>({}))
      const events=Array.isArray(td?.events)?td.events:[]
      for(const g of group){
        let best:any=null,bestScore=0,bestFlip=false
        for(const ev of events){
          const h=String(ev?.strHomeTeam||ev?.strEvent?.split(' vs ')?.[0]||'')
          const a=String(ev?.strAwayTeam||ev?.strEvent?.split(' vs ')?.[1]||'')
          const direct=nameScore(g.home_team,h)+nameScore(g.away_team,a)
          const flip=nameScore(g.home_team,a)+nameScore(g.away_team,h)
          if(direct>bestScore){best=ev;bestScore=direct;bestFlip=false}
          if(flip>bestScore){best=ev;bestScore=flip;bestFlip=true}
        }
        if(!best||bestScore<4)continue
        const status=String(best?.strStatus||best?.strProgress||'').toLowerCase()
        const isFinal=/final|finished|ft|match finished/.test(status) || (!!best?.intHomeScore||best?.intHomeScore===0) && (!!best?.intAwayScore||best?.intAwayScore===0) && new Date(g.starts_at).getTime()<Date.now()-90*60*1000
        if(!isFinal)continue
        const isCombat=String(g.league_name||'').toUpperCase()==='UFC'
        const nowIso=new Date().toISOString()
        if(isCombat){
          const winner=String(best?.strResult||best?.strEventStatus||best?.strStatus||'')
          let res:any=null
          const homeName=bestFlip?String(best?.strAwayTeam||''):String(best?.strHomeTeam||'')
          const awayName=bestFlip?String(best?.strHomeTeam||''):String(best?.strAwayTeam||'')
          if(winner && nameScore(g.home_team,winner)>=2)res='1'
          else if(winner && nameScore(g.away_team,winner)>=2)res='2'
          else if(best?.intHomeScore!=null&&best?.intAwayScore!=null){
            const hs=Number(best.intHomeScore),as=Number(best.intAwayScore)
            if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as){
              const apiWinner=hs>as?'home':'away'
              res=(bestFlip?(apiWinner==='home'?'2':'1'):(apiWinner==='home'?'1':'2'))
            }
          }
          if(!res)continue
          const {data:upd,error:ue}=await s.from('betting_games').update({
            result:res,api_status:'FT',api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'SPORTSDB_FALLBACK',
            needs_review:false,review_reason:null,review_marked_at:null,verification_note:'Final result verified via TheSportsDB fallback'
          }).eq('id',g.id).is('result',null).select('id,home_team,away_team,result')
          if(ue)throw ue
          if(upd?.length)sportsdb_fallback_updated.push(...upd)
        }else{
          let hg=Number(best?.intHomeScore),ag=Number(best?.intAwayScore)
          if(!Number.isFinite(hg)||!Number.isFinite(ag))continue
          if(bestFlip){const tmp=hg;hg=ag;ag=tmp}
          const res=hg>ag?'1':hg<ag?'2':'X'
          const {data:upd,error:ue}=await s.from('betting_games').update({
            result:res,api_home_goals:hg,api_away_goals:ag,api_status:'FT',
            api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'SPORTSDB_FALLBACK',
            needs_review:false,review_reason:null,review_marked_at:null,verification_note:'Final result verified via TheSportsDB fallback'
          }).eq('id',g.id).is('result',null).select('id,home_team,away_team,result,api_home_goals,api_away_goals')
          if(ue)throw ue
          if(upd?.length)sportsdb_fallback_updated.push(...upd)
        }
      }
    }
  }catch(e){console.error('TheSportsDB fallback sync failed',e)}

  const markStaleUnresolved=async()=>{
    const cutoff=new Date(Date.now()-3*60*60*1000).toISOString()
    const {data:stale,error:se}=await s.from('betting_games')
      .select('id,home_team,away_team,starts_at,league_name,needs_review')
      .is('result',null)
      .lt('starts_at',cutoff)
      .not('starts_at','is',null)
      .limit(200)
    if(se)throw se
    const marked:any[]=[]
    for(const g of stale||[]){
      if(g.needs_review)continue
      const nowIso=new Date().toISOString()
      const {data:upd,error:ue}=await s.from('betting_games').update({
        needs_review:true,
        review_reason:'עברו מעל 3 שעות מתחילת האירוע ללא תוצאה סופית מכל מקורות הסנכרון',
        review_marked_at:nowIso
      }).eq('id',g.id).is('result',null).select('id,home_team,away_team,league_name')
      if(ue)throw ue
      if(upd?.length)marked.push(...upd)
    }
    if(marked.length){
      await s.from('security_audit_log').insert({
        severity:'high',
        event_type:'result_sync_stale',
        source:'redball-results',
        actor_type:'system',
        actor_identifier:'results-watchdog',
        success:false,
        details:{count:marked.length,games:marked.slice(0,20)}
      })
    }
    return marked
  }

  const {data:games,error:ge}=await s.from('betting_games').select('id,home_team,away_team,starts_at,api_fixture_id,api_provider,result,needs_review').eq('api_provider','api-football').not('api_fixture_id','is',null)
  if(ge) throw ge
  // Poll only games close to kickoff / already started and still without a final result.
  // This avoids burning the API quota all day on future fixtures.
  const nowMs=Date.now(),leadMs=20*60*1000,staleMs=12*60*60*1000
  const target=(games||[]).filter((g:any)=>{
    if(!g.starts_at||g.result!=null)return false
    const t=new Date(g.starts_at).getTime()
    if(!Number.isFinite(t))return false
    const d=localDate(g.starts_at)
    if(requestedDate&&d!==date)return false
    return t<=nowMs && t>=nowMs-staleMs
  })
  if(!target.length){const [auto_archived,auto_cancelled_unpaid,stale_unresolved]=await Promise.all([autoArchiveCompletedSessions(),expireUnpaidBets(),markStaleUnresolved()]);return json({ok:true,date,count:0,updated:[],linked,linked_count:linked.length,fallback_updated,uefa_fallback_updated,espn_fallback_updated,sportsdb_fallback_updated,stale_unresolved,auto_archived,auto_cancelled_unpaid,quota_guard:{skipped:true,reason:'no_target_games'}})}

  const utcDay=new Date().toISOString().slice(0,10)
  const {data:quotaState}=await s.from('football_api_quota_state').select('*').eq('provider','api-football').maybeSingle()
  const stateIsToday=quotaState?.quota_day===utcDay
  const remaining=stateIsToday&&Number.isFinite(Number(quotaState?.remaining))?Number(quotaState.remaining):null
  const lastCallMs=stateIsToday&&quotaState?.last_call_at?new Date(quotaState.last_call_at).getTime():0
  const started=target.length>0
  const sinceLast=lastCallMs?nowMs-lastCallMs:Number.POSITIVE_INFINITY

  let minGap=0
  if(remaining!==null&&remaining<=20)minGap=10*60*1000
  if(remaining!==null&&remaining<=10)minGap=20*60*1000
  if(remaining!==null&&remaining<=5)minGap=30*60*1000

  if(remaining===0&&sinceLast<60*60*1000)return json({ok:true,date,count:0,updated:[],quota_guard:{skipped:true,reason:'daily_quota_exhausted_probe_later',remaining,quota_limit:quotaState?.quota_limit??null,retry_after_seconds:Math.ceil((60*60*1000-sinceLast)/1000)}})
  if(remaining!==null&&remaining<=20&&!started)return json({ok:true,date,count:0,updated:[],quota_guard:{skipped:true,reason:'reserve_quota_for_live_games',remaining,quota_limit:quotaState?.quota_limit??null}})
  if(minGap&&sinceLast<minGap)return json({ok:true,date,count:0,updated:[],quota_guard:{skipped:true,reason:'low_quota_backoff',remaining,quota_limit:quotaState?.quota_limit??null,retry_after_seconds:Math.ceil((minGap-sinceLast)/1000)}})

  const dates=[...new Set(target.map((g:any)=>localDate(g.starts_at)))]
  const updated=[],errors=[]
  let apiResults=0,lastRemaining=remaining,lastLimit=stateIsToday?quotaState?.quota_limit??null:null
  for(const fixtureDate of dates){
  const r=await fetch(`https://v3.football.api-sports.io/fixtures?date=${encodeURIComponent(fixtureDate)}&timezone=${encodeURIComponent('Asia/Jerusalem')}`,{headers:{'x-apisports-key':key}})
  const d=await r.json().catch(()=>({}))
  const headerRemaining=Number(r.headers.get('x-ratelimit-requests-remaining'))
  const headerLimit=Number(r.headers.get('x-ratelimit-requests-limit'))
  if(Number.isFinite(headerRemaining))lastRemaining=headerRemaining
  if(Number.isFinite(headerLimit))lastLimit=headerLimit
  const limitReached=String(d?.errors?.requests||'').toLowerCase().includes('request limit')
  if(limitReached)lastRemaining=0
  await s.from('football_api_quota_state').upsert({provider:'api-football',quota_day:utcDay,quota_limit:Number.isFinite(Number(lastLimit))?Number(lastLimit):null,remaining:Number.isFinite(Number(lastRemaining))?Number(lastRemaining):null,last_call_at:new Date().toISOString(),updated_at:new Date().toISOString()},{onConflict:'provider'})
  if(!r.ok||Object.keys(d.errors||{}).length){for(const g of target.filter((g:any)=>localDate(g.starts_at)===fixtureDate)){if(nowMs-new Date(g.starts_at).getTime()>=3*60*60*1000)await s.from('betting_games').update({needs_review:true,review_reason:'לא ניתן לקבל תוצאה מ-API-Football',review_marked_at:new Date().toISOString()}).eq('id',g.id)}errors.push({date:fixtureDate,status:r.status,error:'API-Football request failed',provider_errors:d.errors||null,remaining:lastRemaining,quota_limit:lastLimit});if(lastRemaining===0)break;continue}
  apiResults+=Number(d.results||0)
  const byId=new Map((Array.isArray(d.response)?d.response:[]).map((x:any)=>[Number(x.fixture?.id),x]))
  for(const g of target.filter((g:any)=>localDate(g.starts_at)===fixtureDate) as any[]){
   const x:any=byId.get(Number(g.api_fixture_id))
   if(!x){const elapsed=nowMs-new Date(g.starts_at).getTime();if(elapsed>=3*60*60*1000)await s.from('betting_games').update({needs_review:true,review_reason:'המשחק לא נמצא בתשובת API-Football',review_marked_at:new Date().toISOString()}).eq('id',g.id);updated.push({id:g.id,home_team:g.home_team,away_team:g.away_team,fixture_id:g.api_fixture_id,found:false});continue}
   const status=String(x.fixture?.status?.short||'')
   const hg=x.goals?.home==null?null:Number(x.goals.home),ag=x.goals?.away==null?null:Number(x.goals.away)
   const finalStatuses=new Set(['FT','AET','PEN'])
   let suggested:string|null=null
   if(finalStatuses.has(status)&&hg!==null&&ag!==null&&Number.isInteger(hg)&&Number.isInteger(ag)&&hg>=0&&ag>=0)suggested=hg>ag?'1':hg<ag?'2':'X'
   const now=new Date().toISOString(),startedAt=new Date(g.starts_at).getTime(),elapsed=nowMs-startedAt
   const exceptional=['PST','CANC','ABD','AWD','WO'].includes(status)
   const needsReview=!suggested&&(exceptional||elapsed>=3*60*60*1000)
   const reviewReason=exceptional?('סטטוס חריג מהספק: '+status):(needsReview?'עברו מעל 3 שעות מתחילת המשחק ללא תוצאה סופית':null)
   const patch:any={api_status:status,api_home_goals:hg,api_away_goals:ag,api_suggested_result:suggested,api_last_synced_at:now,api_home_name:x.teams?.home?.name||null,api_away_name:x.teams?.away?.name||null,league_name:x.league?.name||null,needs_review:needsReview,review_reason:reviewReason,review_marked_at:needsReview?now:null}
   let auto_settled=false
   const {error:metadataError}=await s.from('betting_games').update(patch).eq('id',g.id)
   if(metadataError)throw metadataError
   if(finalStatuses.has(status)&&suggested&&g.result==null){
    // Atomic guard: a manual result written while the provider request ran wins.
    const {data:settled,error}=await s.from('betting_games').update({result:suggested,result_set_at:now,result_set_by:'API_FOOTBALL'}).eq('id',g.id).is('result',null).select('id')
    if(error)throw error
    auto_settled=!!settled?.length
   }
   updated.push({id:g.id,home_team:g.home_team,away_team:g.away_team,fixture_id:g.api_fixture_id,found:true,status,status_long:x.fixture?.status?.long||'',score:hg==null||ag==null?null:`${hg}-${ag}`,suggested_result:suggested,auto_settled,provider_home:x.teams?.home?.name,provider_away:x.teams?.away?.name})
  }
  }
  let auto_archived:any[]=[],auto_cancelled_unpaid:any[]=[],stale_unresolved:any[]=[]
  // Keep cron maintenance on GET. A manual button press only pulls and settles results.
  if(req.method==='GET')[auto_archived,auto_cancelled_unpaid,stale_unresolved]=await Promise.all([autoArchiveCompletedSessions(),expireUnpaidBets(),markStaleUnresolved()])
  return json({ok:errors.length===0,date,dates,api_results:apiResults,count:updated.length,updated,linked,linked_count:linked.length,fallback_updated,uefa_fallback_updated,espn_fallback_updated,sportsdb_fallback_updated,stale_unresolved,auto_archived,auto_cancelled_unpaid,errors,quota_guard:{remaining:lastRemaining,quota_limit:lastLimit,protected:true},manual_triggered_by:manualRole||null},errors.length?502:200)
 }catch(e:any){console.error(e);return json({error:e?.message||'Server error'},500)}
})
