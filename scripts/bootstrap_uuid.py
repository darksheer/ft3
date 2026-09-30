"""Guarded one-time assignment preparation; committed UUIDs are never recomputed."""
import hashlib,json,uuid
def fingerprint(row):
 return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def prepare_assignments(rows,fingerprints,existing):
 codes=[r['id'] for r in rows]
 if len(set(codes))!=len(codes):raise ValueError('ambiguous duplicate technique codes')
 if set(codes)!=set(fingerprints):raise ValueError('input coverage changed')
 if set(existing)-set(codes):raise ValueError('existing assignment absent from input')
 for r in rows:
  if fingerprint(r)!=fingerprints[r['id']]:raise ValueError('input fingerprint changed: '+r['id'])
 assigned=[{'id':r['id'],'name':r['name'],'fingerprint':fingerprints[r['id']],'uuid':existing.get(r['id']) or str(uuid.uuid4())} for r in rows]
 if len({r['uuid'] for r in assigned})!=len(assigned):raise ValueError('duplicate UUID claims')
 for r in assigned:
  u=uuid.UUID(r['uuid'])
  if str(u)!=r['uuid'] or u.variant!=uuid.RFC_4122:raise ValueError('invalid existing assignment')
 return assigned
