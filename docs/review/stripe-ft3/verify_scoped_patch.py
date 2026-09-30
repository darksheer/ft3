import csv,io,json,subprocess,sys
kind,base,head=sys.argv[1:]
J='FT3_Techniques.json'; C='Fraud Tools Tactics and Techniques - FT3 - Techniques.csv'
def blob(ref,p):return subprocess.check_output(['git','show',ref+':'+p])
def records(ref):return json.loads(blob(ref,J)),list(csv.DictReader(io.StringIO(blob(ref,C).decode(),newline='')))
bj,bc=records(base);hj,hc=records(head)
assert len(bj)==len(bc)==len(hj)==len(hc)==137
assert len({r['id'] for r in hj})==137
changed=subprocess.check_output(['git','diff','--name-only',base,head]).decode().splitlines()
if kind=='parity':
 assert hj==hc,'CSV still differs from JSON'
 assert changed==[C],changed
 expected={('Credential Scanning','is_sub-technique'),('Credential Scanning','sub-technique of'),('Credential Scanning: Github','is_sub-technique'),('No Shipping: Shipping of Incorrect Goods','is_sub-technique'),('No Shipping: Fabricating shipping evidence','is_sub-technique'),('3DS Bypass','id')}
 actual={(a['name'],k) for a,b in zip(bc,hc) for k in a if a[k]!=b[k]}
 assert actual==expected,actual
elif kind=='vps':
 assert set(changed)=={J,C}
 expected={'FT007.005':'Acquire Access: Hijacked VPS','FT007.007':'Acquire Access: Rented VPS'}
 for before,after in zip(bj,hj):
  fields={k for k in before if before[k]!=after[k]}
  if before['id'] in expected:
   assert fields=={'name','description','detection','last_modified'},fields
   assert after['name']==expected[before['id']]
   assert next(r for r in hc if r['id']==after['id'])==after
  else:assert before==after
 assert [r['id'] for r in bj]==[r['id'] for r in hj]
 before_m=[(i,k) for i,(a,b) in enumerate(zip(bj,bc)) for k in a if a[k]!=b[k]]
 after_m=[(i,k) for i,(a,b) in enumerate(zip(hj,hc)) for k in a if a[k]!=b[k]]
 assert before_m==after_m
elif kind=='social':
 targets={'FT007.010','FT008.003','FT018','FT021'}
 assert set(changed)=={J,C,'docs/review/social-media-boundaries.md','docs/review/social-media-clause-dispositions.csv'}
 for old,new,row in zip(bj,hj,hc):
  if old['id'] in targets:
   assert new==row
   assert all(old[k]==new[k] for k in old if k not in {'name','description','detection','last_modified'})
  else:assert old==new
 assert [r['id'] for r in bj]==[r['id'] for r in hj]
 assert next(r for r in hj if r['id']=='FT018')['name']=='Social Media Phishing for Initial Access'
 assert next(r for r in hj if r['id']=='FT021')['name']=='Social Media Impersonation'
elif kind=='uuid':
 assert hj==hc
 assert all({k:v for k,v in r.items() if k!='uuid'}==o for o,r in zip(bj,hj))
 import uuid
 assert len({r['uuid'] for r in hj})==137
 assert all(str(uuid.UUID(r['uuid']))==r['uuid'] and uuid.UUID(r['uuid']).version==4 for r in hj)
elif kind=='dates':
 assert changed==['README.md']
 for p in [J,C,'FT3_Tactics.json','Fraud Tools Tactics and Techniques - FT3 - Tactics.csv']:assert blob(base,p)==blob(head,p)
subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--check',base,head],check=True)
print('PASS',kind,'137 technique records; scoped changes and preserved data verified',base,head)
