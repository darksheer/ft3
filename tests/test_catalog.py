import copy,csv,io,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_catalog import audit_catalog, identity_errors, parse_csv
U1='6e2c1a18-5da4-4af7-88f3-d84550c6880d'
U2='a507a5b9-34cf-431b-81ab-16755261338a'
def record(code='FT001'):
 return {'id':code,'name':'Example','created':'1/30/24','last_modified':'1/30/24','tactics':'Reconnaissance','is_sub-technique':'TRUE' if '.' in code else 'FALSE','sub-technique of':code.split('.')[0] if '.' in code else ''}
def tactic():return {'ID':'FTA001','name':'Reconnaissance','domain':'ft3','created':'01/30/2024','last_modified':'01/30/2024'}
def issues(rows):return audit_catalog(rows,[tactic()],copy.deepcopy(rows),[tactic()])
class CatalogTests(unittest.TestCase):
 def test_duplicate_codes_are_rejected(self):self.assertIn('duplicate_id',{e['rule'] for e in issues([record(),record()])})
 def test_missing_and_conflicting_parents(self):
  r=record('FT001.001');r['sub-technique of']='FT002'
  self.assertTrue({'parent_prefix','parent_missing'} <= {e['rule'] for e in issues([record(),r])})
 def test_flags_and_unknown_tactic(self):
  r=record();r.update(tactics='Missing',**{'is_sub-technique':'TRUE'})
  self.assertTrue({'flag','tactic_missing'} <= {e['rule'] for e in issues([r])})
 def test_csv_field_difference_is_reported(self):
  a=record();b=copy.deepcopy(a);b['name']='Other'
  self.assertIn('parity',{e['rule'] for e in audit_catalog([a],[tactic()],[b],[tactic()])})
 def test_invalid_and_reversed_dates(self):
  a=record();a['created']='2/30/24';self.assertIn('date_invalid',{e['rule'] for e in issues([a])})
  a['created']='2/2/25';self.assertIn('chronology',{e['rule'] for e in issues([a])})
 def test_multiline_csv_roundtrip(self):
  a=record();a['name']='Comma, quote " and\nnewline';s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(a));w.writeheader();w.writerow(a)
  self.assertEqual(parse_csv(s.getvalue()),[a])
 def test_malformed_csv_is_rejected(self):
  with self.assertRaises(ValueError):parse_csv('id,name\nFT001,too,many\n')
 def test_duplicate_headers_are_rejected(self):
  with self.assertRaises(ValueError):parse_csv('id,id\nFT001,FT002\n')
 def test_missing_csv_record_is_reported(self):self.assertIn('parity_coverage',{e['rule'] for e in audit_catalog([record()],[tactic()],[],[tactic()])})
 def test_good_catalog(self):self.assertEqual(issues([record()]),[])
 def test_uuid_missing_and_duplicate(self):
  a=record();a['uuid']=U1;b=record('FT002');b['uuid']=U1
  self.assertIn('uuid_duplicate',{e['rule'] for e in issues([a,b])})
  b.pop('uuid');self.assertIn('uuid_invalid',{e['rule'] for e in issues([a,b])})
 def test_rename_reorder_retains_identity(self):
  a=record();a['uuid']=U1;b=record('FT002');b['uuid']=U2
  head=[copy.deepcopy(b),copy.deepcopy(a)];head[1]['name']='Renamed'
  self.assertEqual(identity_errors([a,b],head,[a,b]),[])
 def test_regeneration_fails_even_with_valid_unique_uuids(self):
  a=record();a['uuid']=U1;b=copy.deepcopy(a);b['uuid']=U2
  self.assertTrue(identity_errors([a],[b],[a]))
 def test_removal_and_uuid_reuse_are_rejected(self):
  a=record();a['uuid']=U1;b=record('FT002');b['uuid']=U1
  self.assertTrue(identity_errors([a],[],[a]));self.assertTrue(identity_errors([a],[b],[a]))
 def test_explicit_code_correction_preserves_uuid(self):
  a=record();a['uuid']=U1;b=copy.deepcopy(a);b['id']='FT056'
  self.assertEqual(identity_errors([a],[b],[a],[{'uuid':U1,'from':'FT001','to':'FT056'}]),[])
 def test_initial_mapping_still_blocks_regeneration_when_previous_changed(self):
  a=record();a['uuid']=U1;b=copy.deepcopy(a);b['uuid']=U2
  self.assertTrue(identity_errors([b],[b],[a]))
if __name__=='__main__':unittest.main()

class BootstrapTests(unittest.TestCase):
 def test_changed_fingerprint_cannot_bootstrap(self):
  from bootstrap_uuid import prepare_assignments
  with self.assertRaises(ValueError):prepare_assignments([record()],{'FT001':'wrong'}, {})
 def test_duplicate_codes_cannot_bootstrap(self):
  from bootstrap_uuid import prepare_assignments
  with self.assertRaises(ValueError):prepare_assignments([record(),record()],{}, {})
 def test_existing_assignment_is_preserved(self):
  from bootstrap_uuid import prepare_assignments,fingerprint
  r=record();self.assertEqual(prepare_assignments([r],{'FT001':fingerprint(r)},{'FT001':U1})[0]['uuid'],U1)

class ImmutablePinCLITests(unittest.TestCase):
 def test_replacing_all_uuids_and_manifest_pin_is_rejected(self):
  import json,subprocess,tempfile,uuid
  root=Path(__file__).resolve().parents[1]
  anchor='7b7fc1a140235d1adb0f4a6ad21169d7753bed50'
  base='48f74e1b94815305e22c70a9ba8462738bbc6a26'
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'repo'
   def git(*args):return subprocess.check_output(['git',*args],cwd=p,stderr=subprocess.DEVNULL)
   subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(root),str(p)],check=True)
   git('checkout','--quiet','--detach',anchor)
   # Exercise current checker implementation on a real, committed adversarial Git revision.
   (p/'scripts/check_catalog.py').write_bytes((root/'scripts/check_catalog.py').read_bytes())
   j=p/'FT3_Techniques.json';c=p/'Fraud Tools Tactics and Techniques - FT3 - Techniques.csv'
   rows=json.loads(j.read_text());mapping={r['id']:str(uuid.uuid4()) for r in rows}
   for r in rows:r['uuid']=mapping[r['id']]
   j.write_text(json.dumps(rows)+'\n')
   with c.open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;cr=list(reader)
   for r in cr:r['uuid']=mapping[r['id']]
   with c.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cr)
   mp=p/'docs/review/stripe-ft3/execution-manifest.json';m=json.loads(mp.read_text());ip=p/m['uuid_initial']['path'];initial=json.loads(ip.read_text())
   for r in initial['assignments']:r['uuid']=mapping[r['id']]
   ip.write_text(json.dumps(initial)+'\n');m['uuid_initial']['blob']=git('hash-object','-w',m['uuid_initial']['path']).decode().strip();mp.write_text(json.dumps(m)+'\n')
   git('add','.');git('-c','user.name=Regression Test','-c','user.email=test@example.invalid','commit','--quiet','-m','replace UUIDs and expected mapping')
   result=subprocess.run([sys.executable,'-B','scripts/check_catalog.py','--base-ref',base,'--head-ref','HEAD','--findings','docs/review/stripe-ft3/findings.csv','--manifest',str(mp),'--identity-anchor-ref',anchor],cwd=p,text=True,capture_output=True)
   report=json.loads(result.stdout)
   self.assertFalse(report['contribution_ready'],'Replacing UUIDs plus their expected fixture must not bless regeneration')
   self.assertIn('uuid_anchor_pin_changed',{r['rule'] for r in report['blocking']})
