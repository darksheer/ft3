#!/usr/bin/env python3
"""Read-only V1 catalog checks against explicit Git revisions and finding dispositions."""
import argparse,collections,csv,datetime,io,json,pathlib,subprocess,sys,uuid
TECH_JSON='FT3_Techniques.json'
TECH_CSV='Fraud Tools Tactics and Techniques - FT3 - Techniques.csv'
TACT_JSON='FT3_Tactics.json'
TACT_CSV='Fraud Tools Tactics and Techniques - FT3 - Tactics.csv'
def parse_csv(text):
 try:
  rows=list(csv.reader(io.StringIO(text,newline=''),strict=True))
 except csv.Error as exc:raise ValueError(str(exc)) from exc
 if not rows or len(set(rows[0]))!=len(rows[0]):raise ValueError('missing or duplicate CSV headers')
 if any(len(r)!=len(rows[0]) for r in rows[1:]):raise ValueError('CSV row width differs from header')
 return [dict(zip(rows[0],r)) for r in rows[1:]]
def audit_catalog(techniques,tactics,csv_techniques,csv_tactics):
 errors=[]
 def emit(rule,catalog,ident,field,detail):errors.append(dict(rule=rule,catalog=catalog,id=ident,field=field,detail=str(detail)))
 tactic_names={r.get('name') for r in tactics};tech_ids={r.get('id') for r in techniques}
 for catalog,rows,crows,key in [('techniques',techniques,csv_techniques,'id'),('tactics',tactics,csv_tactics,'ID')]:
  for label,rs in [('json',rows),('csv',crows)]:
   for ident,n in collections.Counter(r.get(key) for r in rs).items():
    if n>1:emit('duplicate_id',catalog,ident,label,n)
  ji={r.get(key):r for r in rows};ci={r.get(key):r for r in crows}
  if ji.keys()!=ci.keys():emit('parity_coverage',catalog,'*',key,{'json_only':sorted(ji.keys()-ci.keys()),'csv_only':sorted(ci.keys()-ji.keys())})
  for ident in ji.keys()&ci.keys():
   a,b=ji[ident],ci[ident]
   for field in a.keys()|b.keys():
    if a.get(field)!=b.get(field):emit('parity',catalog,ident,field,[a.get(field),b.get(field)])
  for r in rows:
   ident=r.get(key);dates={}
   for field in ('created','last_modified'):
    value=r.get(field,'')
    try:
     width=len(value.rsplit('/',1)[-1]);fmt='%m/%d/%y' if width==2 else '%m/%d/%Y'
     dates[field]=datetime.datetime.strptime(value,fmt).date()
    except (ValueError,TypeError):emit('date_invalid',catalog,ident,field,value)
   if len(dates)==2 and dates['last_modified']<dates['created']:emit('chronology',catalog,ident,'last_modified',[r['created'],r['last_modified']])
   if catalog=='techniques':
    child='.' in (ident or '')
    if r.get('is_sub-technique')!=('TRUE' if child else 'FALSE'):emit('flag',catalog,ident,'is_sub-technique',r.get('is_sub-technique'))
    parent=r.get('sub-technique of','')
    if child and parent!=ident.split('.')[0]:emit('parent_prefix',catalog,ident,'sub-technique of',parent)
    if child and parent not in tech_ids:emit('parent_missing',catalog,ident,'sub-technique of',parent)
    if not child and parent:emit('parent_top_level',catalog,ident,'sub-technique of',parent)
    if r.get('tactics') not in tactic_names:emit('tactic_missing',catalog,ident,'tactics',r.get('tactics'))
  if catalog=='techniques' and any('uuid' in r for r in rows):
   for r in rows:
    value=r.get('uuid','')
    try:
     u=uuid.UUID(value)
     if str(u)!=value or u.variant!=uuid.RFC_4122:raise ValueError('noncanonical UUID')
    except (ValueError,TypeError,AttributeError):emit('uuid_invalid',catalog,r.get('id'),'uuid',value)
   for value,n in collections.Counter(r.get('uuid') for r in rows).items():
    if n>1:emit('uuid_duplicate',catalog,'*','uuid',[value,n])
 return sorted(errors,key=lambda e:(e['catalog'],str(e['id']),e['rule'],e['field'],e['detail']))
def identity_errors(previous,current,initial,transitions=()):
 errors=[]; current_by_uuid={r.get('uuid'):r for r in current if r.get('uuid')}
 permitted={(t['uuid'],t['from'],t['to']) for t in transitions}
 for baseline in (initial,previous):
  for r in baseline:
   if not r.get('uuid'):continue
   now=current_by_uuid.get(r['uuid'])
   if now is None:errors.append('missing committed UUID '+r['uuid'])
   elif now['id']!=r['id'] and (r['uuid'],r['id'],now['id']) not in permitted:errors.append('UUID moved to another code without transition '+r['uuid'])
 return sorted(set(errors))
def git(*args):return subprocess.check_output(['git',*args])
def load(ref):
 return (json.loads(git('show',ref+':'+TECH_JSON)),json.loads(git('show',ref+':'+TACT_JSON)),parse_csv(git('show',ref+':'+TECH_CSV).decode()),parse_csv(git('show',ref+':'+TACT_CSV).decode()))
def signature(e):return tuple(e[k] for k in ['rule','catalog','id','field','detail'])
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-ref',required=True);p.add_argument('--head-ref',required=True);p.add_argument('--findings',required=True);p.add_argument('--manifest',required=True);a=p.parse_args()
 base=load(a.base_ref);head=load(a.head_ref);manifest=json.loads(pathlib.Path(a.manifest).read_text())
 baseline={signature(e) for e in audit_catalog(*base)};failures=[]
 with open(a.findings,newline='') as f:ledger=list(csv.DictReader(f))
 report=[]
 for e in audit_catalog(*head):
  matches=[r for r in ledger if r.get('rule')==e['rule'] and r.get('catalog')==e['catalog'] and r.get('id')==str(e['id']) and r.get('field')==e['field'] and r.get('disposition') in {'fix_in_pr','intentional','deferred_provenance','needs_owner_decision'} and r.get('rationale') and r.get('next_action')]
  e['status']='disclosed_preexisting' if signature(e) in baseline and matches else 'blocking';report.append(e)
  if e['status']=='blocking':failures.append(e)
 for rows,want in [(head[0],137),(head[1],12)]:
  if len(rows)!=want:failures.append({'rule':'record_count','expected':want,'actual':len(rows)})
 missing=set(r['id'] for r in base[0])-set(r['id'] for r in head[0])
 transitions=manifest.get('code_transitions',[])
 permitted={t['from'] for t in transitions}
 if missing-permitted:failures.append({'rule':'record_loss','ids':sorted(missing-permitted)})
 initial=[]
 pin=manifest.get('uuid_initial')
 if pin:
  fixed=git('cat-file','blob',pin['blob']);initial=json.loads(fixed)['assignments']
  current=git('show',a.head_ref+':'+pin['path'])
  if current!=fixed:failures.append({'rule':'uuid_initial_mapping_changed'})
  try:prior_manifest=json.loads(git('show',a.base_ref+':docs/review/stripe-ft3/execution-manifest.json'))
  except subprocess.CalledProcessError:prior_manifest={}
  if prior_manifest.get('uuid_initial') and prior_manifest['uuid_initial']!=pin:failures.append({'rule':'uuid_pin_changed'})
  if manifest.get('uuid_previous_ref')!=a.base_ref:failures.append({'rule':'uuid_previous_revision_mismatch'})
 if any(r.get('uuid') for r in head[0]) and not pin:failures.append({'rule':'uuid_baseline_missing'})
 for error in identity_errors(base[0],head[0],initial,transitions):failures.append({'rule':'uuid_identity','detail':error})
 if pin:
  adopted=set(manifest.get('adopted_uuid_values',[]))
  for r in initial:
   if r['uuid'] not in adopted and uuid.UUID(r['uuid']).version!=4:failures.append({'rule':'bootstrap_uuid_version','id':r['id']})
 print(json.dumps({'base':git('rev-parse',a.base_ref).decode().strip(),'head':git('rev-parse',a.head_ref).decode().strip(),'catalog_defect_free':not report,'contribution_ready':not failures,'disclosed_defects':report,'blocking':failures},indent=2))
 return bool(failures)
if __name__=='__main__':
 try:sys.exit(main())
 except (ValueError,KeyError,subprocess.CalledProcessError) as exc:print('VALIDATION ERROR:',exc,file=sys.stderr);sys.exit(2)
