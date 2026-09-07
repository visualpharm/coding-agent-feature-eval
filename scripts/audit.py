import json,glob,collections,sqlite3
from pathlib import Path
OUT=Path(__file__).parent
original=json.loads((OUT.parent/'data'/'experiment-data.json').read_text())  # Published dataset; local logs are required to re-extract usage
d=json.loads(json.dumps(original));audit={}
prices=d['experiment']['prices_per_million']
prices['claude-opus-4-7']={'input':5,'output':25,'cache_read':.5,'cache_write':6.25}
keys={'input':'input_tokens','output':'output_tokens','cache_read':'cache_read_input_tokens','cache_write':'cache_creation_input_tokens'}
for r in d['runs']:
 old=r['sub_usd']
 if r['id'] in ['sonnet-medium','fable-low','opus-low','glm-claude-code']:
  name='glm' if r['id']=='glm-claude-code' else r['id']
  base=Path.home()/('.claude-glm' if name=='glm' else '.claude')/'projects'/('-Users-<user>-projects-<repo>-eval-'+name)  # Set this to the local Claude project directory
  unique={};duplicates=0;counts=collections.Counter()
  for p in base.glob('*.jsonl'):
   for line in p.open():
    try:row=json.loads(line)
    except ValueError:continue
    m=row.get('message') or {};u=m.get('usage') or {}
    if row.get('type')!='assistant' or not u or m.get('model') in [None,'<synthetic>']:continue
    mid=m.get('id') or row.get('uuid')
    if mid in unique:
     assert unique[mid]['usage']==u
     duplicates+=1
    unique[mid]=m
  assert unique, f'No usage records at {base}; adapt local log paths before running the audit'
  bymodel={}
  for model in {m['model'] for m in unique.values()}:
   tokens=collections.Counter();h1=0;n=0
   for m in unique.values():
    if m['model']!=model:continue
    n+=1;u=m['usage']
    for k,v in keys.items():tokens[k]+=u.get(v,0)
    h1+=(u.get('cache_creation') or {}).get('ephemeral_1h_input_tokens',0)
   p=prices[model]
   api=sum(tokens[k]*(p[k] or 0)/1e6 for k in keys)+h1*(p['input']*2-p['cache_write'])/1e6
   allowance=d['experiment']['allowances'][r['plan']]
   capacity=allowance.get('fable_monthly_api_equiv_usd') if model=='claude-fable-5-1' else allowance['monthly_api_equiv_usd']
   bymodel[model]={'unique_requests':n,'tokens':dict(tokens),'one_hour_cache_write_tokens':h1,'api_usd':api,'sub_usd':api*allowance['fee_usd']/capacity}
  r['api_usd']=sum(v['api_usd'] for v in bymodel.values());r['sub_usd']=sum(v['sub_usd'] for v in bymodel.values())
  r['tokens']={k:sum(v['tokens'][k] for v in bymodel.values()) for k in keys}
  r['cost_components']=bymodel
  audit[r['id']]={'duplicate_records_removed':duplicates,'model_breakdown':bymodel,'old_sub_usd':old,'corrected_sub_usd':r['sub_usd']}
 elif r['id']=='glm-zcode':
  db=sqlite3.connect('file:'+str(Path.home()/'.zcode/cli/db/db.sqlite')+'?mode=ro',uri=True)
  sessions=['sess_4ef71c9f-c51b-4b38-9410-cdd52a4fc8d5','sess_d2baabb1-061d-44a8-b539-df1a131d5f4a']
  observations=[]
  for i,session in enumerate(sessions,1):
   vals=db.execute('select sum(input_tokens-cache_read_input_tokens),sum(output_tokens),sum(cache_read_input_tokens),sum(cache_creation_input_tokens),count(*) from model_usage where session_id=?',(session,)).fetchone()
   assert vals[-1]>0, 'No provider usage records for session'
   tokens=dict(zip(['input','output','cache_read','cache_write'],vals[:4]))
   api=sum(tokens[k]*(prices[r['model']][k] or 0)/1e6 for k in keys)
   observations.append({'label':f'session {i}','tokens':tokens,'api_usd':api,'sub_usd':api*56/1300,'unique_requests':vals[-1]})
  n=len(observations)
  r['tokens']={k:sum(o['tokens'][k] for o in observations)/n for k in keys}
  r['api_usd']=sum(o['api_usd'] for o in observations)/n
  r['sub_usd']=sum(o['sub_usd'] for o in observations)/n
  r['session_observations']=observations
  r['cost_basis']='mean_per_session'
  r['cost_components']={'glm-5.3':{'tokens':r['tokens'],'api_usd':r['api_usd'],'sub_usd':r['sub_usd'],'source':'Arithmetic mean of the two provider-recorded session totals','unique_requests':sum(o['unique_requests'] for o in observations)/n}}
  audit[r['id']]={'source':'ZCode model_usage unique request records','cost_basis':'mean_per_session','verified_tokens':r['tokens'],'corrected_api_usd':r['api_usd'],'corrected_sub_usd':r['sub_usd'],'individual_sessions':observations,'comparability':r['comparison_scope']}

 else:
  # Codex terminal event is a cumulative total, counted once.
  p=Path.home()/'.claude/artifacts/bruno/model-eval-20260907/result-codex.jsonl'
  usage=[json.loads(l)['usage'] for l in p.read_text().splitlines() if '"turn.completed"' in l][0]
  assert usage['input_tokens']-usage['cached_input_tokens']==r['tokens']['input']
  assert usage['output_tokens']==r['tokens']['output']
  r['api_usd']=sum(r['tokens'][k]*(prices[r['model']][k] or 0)/1e6 for k in keys)
  r['sub_usd']=r['api_usd']*200/7000
  audit[r['id']]={'source':'Codex turn.completed cumulative usage','corrected_sub_usd':r['sub_usd']}
 if r['id']=='glm-claude-code':
  summary=json.loads((Path.home()/'.claude/artifacts/bruno/model-eval-20260907/result-glm.json').read_text())['modelUsage']['glm-5.3']
  tokens={'input':summary['inputTokens'],'output':summary['outputTokens'],'cache_read':summary['cacheReadInputTokens'],'cache_write':summary['cacheCreationInputTokens']}
  r['tokens']=tokens
  r['api_usd']=sum(tokens[k]*(prices['glm-5.3'][k] or 0)/1e6 for k in keys)
  r['sub_usd']=r['api_usd']*56/1300
  audit[r['id']]['final_modelUsage_crosscheck']={'tokens':tokens,'api_usd':r['api_usd'],'sub_usd':r['sub_usd'],'reason':'Final modelUsage includes aggregate overhead beyond assistant-visible usage. Preferred for complete run cost.'}
  audit[r['id']]['corrected_sub_usd']=r['sub_usd']
  r['cost_components']={'glm-5.3':{'tokens':tokens,'api_usd':r['api_usd'],'sub_usd':r['sub_usd'],'source':'Final modelUsage aggregate'}}
 r['weekly_share_pct']=r['sub_usd']/d['experiment']['allowances'][r['plan']]['fee_usd']*4.33*100
 assert sum(r['rubric'])==r['score']
(OUT/'corrected-data.json').write_text(json.dumps(d,indent=2))
(OUT/'cost-audit.json').write_text(json.dumps({'method':'Unique message IDs; each actual model priced separately; correct one-hour cache rate; includes automatic security review calls; preserves published plan allowance assumptions. ZCode cost and tokens are the arithmetic mean of the two sessions whose shared branch was graded. The shared grade is not an average of independently graded attempts.','pricing_source':'https://platform.claude.com/docs/en/about-claude/pricing','allowance_caveat':'Plan capacities are inherited estimates, not independently remeasured here.','runs':audit},indent=2))
for r in d['runs']:print(r['id'],round(r['api_usd'],4),round(r['sub_usd'],4),r['score']/2)
