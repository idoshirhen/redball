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
const localDate=(value:string|Date)=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Jerusalem',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(value))
const dateKey=(v:string)=>localDate(v).replace(/-/g,'')
const resultFromScore=(h:number,a:number)=>h>a?'1':h<a?'2':'X'

async function fetchJson(url:string,timeout=7000){
  const c=new AbortController();const t=setTimeout(()=>c.abort(),timeout)
  try{
    const r=await fetch(url,{headers:{'user-agent':'Mozilla/5.0 RedBallResultsWatchdog/1.0','accept':'application/json'},signal:c.signal})
    const d=await r.json().catch(()=>({}))
    return {ok:r.ok,status:r.status,data:d}
  }catch(e:any){return {ok:false,status:0,error:String(e?.message||e),data:{}}}
  finally{clearTimeout(t)}
}
function extractEspn(events:any[]){
  const soccer:any[]=[],combat:any[]=[]
  for(const ev of events||[])for(const comp of (Array.isArray(ev?.competitions)?ev.competitions:[])){
    const completed=!!comp?.status?.type?.completed
    const competitors=Array.isArray(comp?.competitors)?comp.competitors:[]
    if(competitors.length<2)continue
    const home=competitors.find((x:any)=>x?.homeAway==='home'),away=competitors.find((x:any)=>x?.homeAway==='away')
    if(home&&away){
      soccer.push({completed,date:comp?.date||ev?.date||null,home:String(home?.team?.displayName||home?.team?.name||''),away:String(away?.team?.displayName||away?.team?.name||''),hg:Number(home?.score),ag:Number(away?.score)})
    }else{
      const a=competitors[0],b=competitors[1]
      combat.push({completed,date:comp?.date||ev?.date||null,a:String(a?.athlete?.fullName||a?.athlete?.displayName||''),b:String(b?.athlete?.fullName||b?.athlete?.displayName||''),awin:!!a?.winner,bwin:!!b?.winner})
    }
  }
  return {soccer,combat}
}
function matchSoccer(g:any,cands:any[]){
  let best:any=null,bestScore=0
  for(const x of cands){if(!x.completed||!Number.isFinite(x.hg)||!Number.isFinite(x.ag))continue
    const s=nameScore(g.home_team,x.home)+nameScore(g.away_team,x.away)
    if(s>bestScore){best=x;bestScore=s}
  }
  return bestScore>=4?best:null
}
function matchCombat(g:any,cands:any[]){
  let best:any=null,bestScore=0,bestFlip=false
  for(const x of cands){if(!x.completed)continue
    const d=nameScore(g.home_team,x.a)+nameScore(g.away_team,x.b),f=nameScore(g.home_team,x.b)+nameScore(g.away_team,x.a)
    if(d>bestScore){best=x;bestScore=d;bestFlip=false}
    if(f>bestScore){best=x;bestScore=f;bestFlip=true}
  }
  if(!best||bestScore<4)return null
  const firstWins=bestFlip?best.bwin:best.awin,secondWins=bestFlip?best.awin:best.bwin
  if(firstWins===secondWins)return null
  return {result:firstWins?'1':'2',raw:best}
}
function runSelfTests(){
  const tests:any[]=[]
  const check=(name:string,ok:boolean,detail?:any)=>tests.push({name,ok,detail})
  check('alias Aston Villa',nameScore('אסטון וילה','Aston Villa')>=2)
  check('alias Man City',nameScore("מנצ'סטר סיטי",'Manchester City')>=2)
  check('alias Dortmund',nameScore('דורטמונד','Borussia Dortmund')>=2)
  check('alias Valencia',nameScore('ולנסיה','Valencia CF')>=2)
  check('alias Villarreal',nameScore('ויאריאל','Villarreal CF')>=2)
  check('score home',resultFromScore(2,1)==='1')
  check('score draw',resultFromScore(1,1)==='X')
  check('score away',resultFromScore(1,2)==='2')
  check('negative mismatch',nameScore('דורטמונד','Valencia CF')<2)
  check('normalization accents',normName('Atlético Madrid')===normName('Atletico Madrid'))
  return {ok:tests.every(x=>x.ok),tests,passed:tests.filter(x=>x.ok).length,total:tests.length}
}

Deno.serve(async(req)=>{
 if(req.method==='OPTIONS')return new Response('ok',{headers:cors})
 if(req.method!=='GET'&&req.method!=='POST')return json({error:'Method not allowed'},405)
 const u=new URL(req.url),mode=u.searchParams.get('mode')||'run'
 if(mode==='selftest'&&req.method==='POST')return json({error:'Method not allowed'},405)
 if(mode==='selftest')return json(runSelfTests())
 const s=createClient(Deno.env.get('SUPABASE_URL')!,Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,{auth:{persistSession:false,autoRefreshToken:false}})
 if(req.method==='POST'){
   const token=req.headers.get('x-admin-token')||''
   if(!token||token.length<60)return json({error:'Unauthorized'},401)
   const tokenHash=await sha256(token),userAgentHash=await sha256(uaOf(req)),nowIso=new Date().toISOString(),idleCutoff=new Date(Date.now()-12*60*60*1000).toISOString()
   const {data:session,error:sessionError}=await s.from('admin_sessions').select('token_hash,user_agent_hash,last_seen_at,expires_at,scope,admin_role').eq('token_hash',tokenHash).eq('scope','betting').gt('expires_at',nowIso).gt('last_seen_at',idleCutoff).maybeSingle()
   if(sessionError)throw sessionError
   if(!session||session.user_agent_hash!==userAgentHash)return json({error:'Session expired'},401)
   if(!['sani','vladi'].includes(String(session.admin_role||'sani')))return json({error:'אין הרשאה למשיכת תוצאות'},403)
   await s.from('admin_sessions').update({last_seen_at:nowIso}).eq('token_hash',tokenHash).eq('scope','betting')
 }
 const started=new Date().toISOString()
 await s.from('result_sync_health').upsert({id:'watchdog',last_started_at:started,last_ok:false,updated_at:started},{onConflict:'id'})
 try{
   const now=Date.now(),minAge=75*60*1000,maxAge=48*60*60*1000
   const {data:rows,error}=await s.from('betting_games').select('id,home_team,away_team,starts_at,result,league_name').is('result',null).not('starts_at','is',null)
   if(error)throw error
   const pending=(rows||[]).filter((g:any)=>{const t=new Date(g.starts_at).getTime();return Number.isFinite(t)&&t<=now-minAge&&t>=now-maxAge})
   const providerStatus:any={espn:{requests:0,ok:0},sportsdb:{requests:0,ok:0}}
   const resolved:any[]=[]
   const byEndpoint=new Map<string,any[]>()
   for(const g of pending){
     const league=String(g.league_name||'')
     let endpoint=''
     if(soccerSlug[league])endpoint='https://site.api.espn.com/apis/site/v2/sports/soccer/'+soccerSlug[league]+'/scoreboard?dates='+dateKey(g.starts_at)
     else if(league.toUpperCase()==='UFC')endpoint='https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard?dates='+dateKey(g.starts_at)
     if(endpoint){if(!byEndpoint.has(endpoint))byEndpoint.set(endpoint,[]);byEndpoint.get(endpoint)!.push(g)}
   }
   for(const [endpoint,group] of byEndpoint){
     providerStatus.espn.requests++
     const er=await fetchJson(endpoint,7000)
     if(er.ok)providerStatus.espn.ok++
     if(!er.ok)continue
     const ex=extractEspn(Array.isArray(er.data?.events)?er.data.events:[])
     for(const g of group){
       if(String(g.league_name||'').toUpperCase()==='UFC'){
         const m=matchCombat(g,ex.combat);if(!m)continue
         const nowIso=new Date().toISOString()
         const {data:upd}=await s.from('betting_games').update({result:m.result,api_status:'FT',api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'WATCHDOG_ESPN',needs_review:false,review_reason:null,review_marked_at:null,verification_note:'Final result verified by independent watchdog via ESPN'}).eq('id',g.id).is('result',null).select('id,home_team,away_team,result')
         if(upd?.length)resolved.push(...upd)
       }else{
         const m=matchSoccer(g,ex.soccer);if(!m)continue
         const nowIso=new Date().toISOString(),res=resultFromScore(Number(m.hg),Number(m.ag))
         const {data:upd}=await s.from('betting_games').update({result:res,api_home_goals:Number(m.hg),api_away_goals:Number(m.ag),api_status:'FT',api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'WATCHDOG_ESPN',needs_review:false,review_reason:null,review_marked_at:null,verification_note:'Final result verified by independent watchdog via ESPN'}).eq('id',g.id).is('result',null).select('id,home_team,away_team,result,api_home_goals,api_away_goals')
         if(upd?.length)resolved.push(...upd)
       }
     }
   }

   const unresolved=pending.filter((g:any)=>!resolved.some((x:any)=>x.id===g.id))
   const bySports=new Map<string,any[]>()
   for(const g of unresolved){
     const sport=String(g.league_name||'').toUpperCase()==='UFC'?'MMA':'Soccer'
     const key=localDate(g.starts_at)+'|'+sport
     if(!bySports.has(key))bySports.set(key,[])
     bySports.get(key)!.push(g)
   }
   for(const [key,group] of bySports){
     const [day,sport]=key.split('|')
     providerStatus.sportsdb.requests++
     const tr=await fetchJson('https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d='+encodeURIComponent(day)+'&s='+encodeURIComponent(sport),7000)
     if(tr.ok)providerStatus.sportsdb.ok++
     if(!tr.ok)continue
     const events=Array.isArray(tr.data?.events)?tr.data.events:[]
     for(const g of group){
       if(resolved.some((x:any)=>x.id===g.id))continue
       let best:any=null,bestScore=0,bestFlip=false
       for(const ev of events){
         const h=String(ev?.strHomeTeam||String(ev?.strEvent||'').split(' vs ')[0]||''),a=String(ev?.strAwayTeam||String(ev?.strEvent||'').split(' vs ')[1]||'')
         const d=nameScore(g.home_team,h)+nameScore(g.away_team,a),f=nameScore(g.home_team,a)+nameScore(g.away_team,h)
         if(d>bestScore){best=ev;bestScore=d;bestFlip=false}
         if(f>bestScore){best=ev;bestScore=f;bestFlip=true}
       }
       if(!best||bestScore<4)continue
       const status=String(best?.strStatus||best?.strProgress||'').toLowerCase()
       const final=/final|finished|ft|match finished/.test(status)
       if(!final)continue
       const nowIso=new Date().toISOString()
       if(String(g.league_name||'').toUpperCase()==='UFC'){
         const winner=String(best?.strResult||best?.strEventStatus||'')
         let res:any=null
         if(nameScore(g.home_team,winner)>=2)res='1';else if(nameScore(g.away_team,winner)>=2)res='2'
         if(!res)continue
         const {data:upd}=await s.from('betting_games').update({result:res,api_status:'FT',api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'WATCHDOG_SPORTSDB',needs_review:false,review_reason:null,review_marked_at:null,verification_note:'Final result verified by independent watchdog via TheSportsDB'}).eq('id',g.id).is('result',null).select('id,home_team,away_team,result')
         if(upd?.length)resolved.push(...upd)
       }else{
         let hg=Number(best?.intHomeScore),ag=Number(best?.intAwayScore)
         if(!Number.isFinite(hg)||!Number.isFinite(ag))continue
         if(bestFlip){const t=hg;hg=ag;ag=t}
         const res=resultFromScore(hg,ag)
         const {data:upd}=await s.from('betting_games').update({result:res,api_home_goals:hg,api_away_goals:ag,api_status:'FT',api_last_synced_at:nowIso,result_set_at:nowIso,result_set_by:'WATCHDOG_SPORTSDB',needs_review:false,review_reason:null,review_marked_at:null,verification_note:'Final result verified by independent watchdog via TheSportsDB'}).eq('id',g.id).is('result',null).select('id,home_team,away_team,result,api_home_goals,api_away_goals')
         if(upd?.length)resolved.push(...upd)
       }
     }
   }

   const {data:stillRows}=await s.from('betting_games').select('id,home_team,away_team,starts_at,league_name').is('result',null).not('starts_at','is',null)
   const still=(stillRows||[]).filter((g:any)=>{const t=new Date(g.starts_at).getTime();return Number.isFinite(t)&&t<=Date.now()-minAge&&t>=Date.now()-maxAge})
   const finished=new Date().toISOString()
   await s.from('result_sync_health').upsert({id:'watchdog',last_started_at:started,last_finished_at:finished,last_ok:true,unresolved_count:still.length,resolved_count:resolved.length,provider_status:providerStatus,last_error:null,updated_at:finished},{onConflict:'id'})
   return json({ok:true,pending_count:pending.length,resolved_count:resolved.length,resolved,unresolved_count:still.length,unresolved:still,provider_status:providerStatus})
 }catch(e:any){
   const finished=new Date().toISOString()
   await s.from('result_sync_health').upsert({id:'watchdog',last_started_at:started,last_finished_at:finished,last_ok:false,last_error:String(e?.message||e),updated_at:finished},{onConflict:'id'})
   return json({ok:false,error:String(e?.message||e)},500)
 }
})
