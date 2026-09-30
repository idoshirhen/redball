import { createClient } from 'npm:@supabase/supabase-js@2'
const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"content-type, apikey, x-client-info","Access-Control-Allow-Methods":"GET, OPTIONS"}
const json=(b:any,s=200)=>new Response(JSON.stringify(b),{status:s,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})
Deno.serve(async(req)=>{
 if(req.method==='OPTIONS') return new Response('ok',{headers:cors})
 if(req.method!=='GET') return json({error:'Method not allowed'},405)
 try{
  const key=Deno.env.get('API_FOOTBALL_KEY')
  if(!key) return json({error:'API_FOOTBALL_KEY secret is missing'},500)
  const s=createClient(Deno.env.get('SUPABASE_URL')!,Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,{auth:{persistSession:false,autoRefreshToken:false}})
  const localDate=(value:string|Date)=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Jerusalem',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(value))
  const u=new URL(req.url),requestedDate=u.searchParams.get('date'),date=requestedDate||localDate(new Date())
  if(requestedDate&&!/^\d{4}-\d{2}-\d{2}$/.test(requestedDate))return json({error:'Invalid date'},400)
  const {data:games,error:ge}=await s.from('betting_games').select('id,home_team,away_team,starts_at,api_fixture_id,api_provider,result').eq('api_provider','api-football').not('api_fixture_id','is',null)
  if(ge) throw ge
  // Keep unfinished games from previous dates in the normal cron run after midnight.
  const target=(games||[]).filter((g:any)=>{if(!g.starts_at)return false;const d=localDate(g.starts_at);return requestedDate?d===date:d===date||(d<date&&g.result==null)})
  if(!target.length) return json({ok:true,date,count:0,updated:[]})
  const dates=[...new Set(target.map((g:any)=>localDate(g.starts_at)))]
  const updated=[],errors=[]
  let apiResults=0
  for(const fixtureDate of dates){
  const r=await fetch(`https://v3.football.api-sports.io/fixtures?date=${encodeURIComponent(fixtureDate)}&timezone=${encodeURIComponent('Asia/Jerusalem')}`,{headers:{'x-apisports-key':key}})
  const d=await r.json().catch(()=>({}))
  if(!r.ok||Object.keys(d.errors||{}).length){errors.push({date:fixtureDate,status:r.status,error:'API-Football request failed'});continue}
  apiResults+=Number(d.results||0)
  const byId=new Map((Array.isArray(d.response)?d.response:[]).map((x:any)=>[Number(x.fixture?.id),x]))
  for(const g of target.filter((g:any)=>localDate(g.starts_at)===fixtureDate) as any[]){
   const x:any=byId.get(Number(g.api_fixture_id))
   if(!x){updated.push({id:g.id,home_team:g.home_team,away_team:g.away_team,fixture_id:g.api_fixture_id,found:false});continue}
   const status=String(x.fixture?.status?.short||'')
   const hg=x.goals?.home==null?null:Number(x.goals.home),ag=x.goals?.away==null?null:Number(x.goals.away)
   let suggested:string|null=null
   if(status==='FT'&&hg!==null&&ag!==null&&Number.isInteger(hg)&&Number.isInteger(ag)&&hg>=0&&ag>=0)suggested=hg>ag?'1':hg<ag?'2':'X'
   const now=new Date().toISOString()
   const patch:any={api_status:status,api_home_goals:hg,api_away_goals:ag,api_suggested_result:suggested,api_last_synced_at:now,api_home_name:x.teams?.home?.name||null,api_away_name:x.teams?.away?.name||null}
   let auto_settled=false
   const {error:metadataError}=await s.from('betting_games').update(patch).eq('id',g.id)
   if(metadataError)throw metadataError
   if(status==='FT'&&suggested&&g.result==null){
    // Atomic guard: a manual result written while the provider request ran wins.
    const {data:settled,error}=await s.from('betting_games').update({result:suggested,result_set_at:now,result_set_by:'API_FOOTBALL'}).eq('id',g.id).is('result',null).select('id')
    if(error)throw error
    auto_settled=!!settled?.length
   }
   updated.push({id:g.id,home_team:g.home_team,away_team:g.away_team,fixture_id:g.api_fixture_id,found:true,status,status_long:x.fixture?.status?.long||'',score:hg==null||ag==null?null:`${hg}-${ag}`,suggested_result:suggested,auto_settled,provider_home:x.teams?.home?.name,provider_away:x.teams?.away?.name})
  }
  }
  return json({ok:errors.length===0,date,dates,api_results:apiResults,count:updated.length,updated,errors},errors.length?502:200)
 }catch(e:any){console.error(e);return json({error:e?.message||'Server error'},500)}
})
