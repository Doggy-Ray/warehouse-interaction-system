"""Compare startup hashes to end-of-task reads, without any upstream write."""
from pathlib import Path
import json,urllib.request,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
base=json.loads((ROOT/'reports/upstream_hashes_before.json').read_text(encoding='utf-8'))
extra=ROOT/'reports/upstream_new_inputs_before.json'
if extra.exists():base.update(json.loads(extra.read_text(encoding='utf-8')))
health=json.loads((ROOT/'server.pid').read_text(encoding='utf-8-sig'))
after=json.load(urllib.request.urlopen(f"http://127.0.0.1:{health['port']}/api/hash_snapshot",timeout=180))
missing=sorted(set(base)-set(after));unrecorded=sorted(set(after)-set(base));changed=[k for k,v in base.items() if k in after and after[k]!=v]
report=dict(status='passed' if not(missing or unrecorded or changed) else 'failed',before_files=len(base),after_files=len(after),changed=changed,missing=missing,unrecorded=unrecorded,scope='Registered read-only upstream inputs; no performance set or full evidence JSONL')
(ROOT/'reports/upstream_hashes_after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'reports/integrity_result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(report['status']!='passed')
