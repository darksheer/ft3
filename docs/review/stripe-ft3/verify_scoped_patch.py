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
elif kind=='dates':
 assert changed==['README.md']
 for p in [J,C,'FT3_Tactics.json','Fraud Tools Tactics and Techniques - FT3 - Tactics.csv']:assert blob(base,p)==blob(head,p)
subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--check',base,head],check=True)
print('PASS',kind,'137 technique records; scoped changes and preserved data verified',base,head)
