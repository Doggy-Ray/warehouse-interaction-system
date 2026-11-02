import sys
sys.dont_write_bytecode=True
import json, os, csv, io, mimetypes, html, traceback, argparse
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
from adapter import *
sys.path.insert(0,str(WORK/'仓储证据助手/src'))
from rag_service import service as rag_service
from li_demo import handle as li_demo

class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args):
        print(self.log_date_time_string(),fmt%args,flush=True)
    def send(self,body,kind='application/json; charset=utf-8',status=200,filename=None):
        if not isinstance(body,bytes):body=body.encode('utf-8')
        self.send_response(status);self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        if filename:self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        parsed=urlparse(self.path);q={k:v[-1] for k,v in parse_qs(parsed.query).items()}
        try:
            if parsed.path=='/api/li_demo':return self.send(json.dumps(li_demo(q),ensure_ascii=False,allow_nan=False))
            if parsed.path=='/api/rag/status':return self.send(json.dumps(rag_service().status(),ensure_ascii=False))
            if parsed.path=='/api/health':return self.send(json.dumps(dict(status='ok',pid=os.getpid(),application='warehouse-lab',project=str(ROOT),upstream_writes=False)))
            if parsed.path=='/api/hash_snapshot':
                with LOCK:
                    s=snapshot()
                return self.send(json.dumps(s,ensure_ascii=False))
            if parsed.path=='/api/export':return self.export(q)
            if parsed.path.startswith('/api/'):
                result=dispatch(parsed.path[5:],q)
                return self.send(json.dumps(clean(result),ensure_ascii=False,allow_nan=False))
            file=ROOT/'frontend'/parsed.path.lstrip('/') if parsed.path!='/' else ROOT/'frontend/index.html'
            if not file.resolve().is_relative_to(ROOT/'frontend') or not file.is_file():return self.send('未找到','text/plain; charset=utf-8',404)
            self.send(file.read_bytes(),(mimetypes.guess_type(str(file))[0] or 'application/octet-stream')+'; charset=utf-8')
        except (ValueError,KeyError) as exc:self.send(json.dumps(dict(status='invalid_request',message=str(exc)),ensure_ascii=False),status=400)
        except Exception:
            traceback.print_exc();self.send(json.dumps(dict(status='error',message='数据服务未完成请求，请检查本地日志后重试。'),ensure_ascii=False),status=500)
    def do_POST(self):
        try:
            if urlparse(self.path).path!='/api/rag/ask':return self.send('{}',status=404)
            # Local POST requests must come from the same origin when sent by a browser.
            if self.headers.get('Origin') not in [None,'http://'+self.headers.get('Host','')]:return self.send('{}',status=403)
            n=int(self.headers.get('Content-Length',0))
            if not 0<n<=20000:raise ValueError('请求长度不合法')
            payload=json.loads(self.rfile.read(n))
            if not isinstance(payload,dict):raise ValueError('请求必须为对象')
            result=rag_service().ask(payload)
            self.send(json.dumps(clean(result),ensure_ascii=False,allow_nan=False))
        except (BrokenPipeError,ConnectionResetError):pass
        except (ValueError,KeyError,TypeError):self.send(json.dumps(dict(status='invalid_request',message='问题或上下文不合法。'),ensure_ascii=False),status=400)
        except Exception:
            traceback.print_exc();self.send(json.dumps(dict(status='error',message='助手未完成请求；原有数据浏览仍可用。'),ensure_ascii=False),status=500)
    def export(self,q):
        c=ctx(q)
        if c['source_mode']!='fixed_workload_replay':raise ValueError('方案导出需要受控回放上下文')
        m=metric(c)
        if not m:return self.send(json.dumps(missing(c),ensure_ascii=False),status=409)
        kind=q.get('kind','metrics');pid=c['plan_id'];stem=f"{pid}_{c['run']}_{c['split']}"
        note='条件性FILI；fixed_workload_replay；time_model_verified=false；吞吐和积压改善未评估；正式LI未评估；一次主实验replicate'
        payload=envelope(c,metrics=m,baseline=metric(c,'S0_K0'),moves=moves(c),limitations=note,denominators=dict(common_events=m['common_events'],evaluated_events=m['evaluated_events'],all_events=m['events']))
        (ROOT/'exports').mkdir(exist_ok=True)
        if kind=='metrics':
            body=json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False);filename=stem+'_metrics.json';content='application/json; charset=utf-8'
        elif kind=='moves':
            items=payload['moves']['items'];fields=['sku_id','from_location_id','to_location_id','budget_count','feasibility_basis','source_intervention_ids','plan_id','run','split','source_mode','method_version','common_events','limitations']
            out=io.StringIO();writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader()
            for r in items:writer.writerow({**r,**c,'method_version':METHOD,'common_events':m['common_events'],'limitations':note})
            body='\ufeff'+out.getvalue();filename=stem+'_moves.csv';content='text/csv; charset=utf-8'
        elif kind=='print':
            esc=lambda v:html.escape(str(v))
            tr=''.join('<tr><td>'+esc(k)+'</td><td>'+esc(v)+'</td></tr>' for k,v in m.items())
            move_tr=''.join('<tr><td>'+esc(r['sku_id'])+'</td><td>'+esc(r['from_location_id'])+'</td><td>'+esc(r['to_location_id'])+'</td></tr>' for r in payload['moves']['items'])
            body=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>方案摘要 {esc(stem)}</title><style>body{{font:14px Microsoft YaHei,sans-serif;max-width:1000px;margin:40px auto;color:#22364a}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd5dd;padding:8px;text-align:left}}@media print{{button{{display:none}}}}</style><button onclick="print()">打印方案摘要</button><h1>仓储拣选设计实验室 · 方案摘要</h1><p>{esc(stem)} · {esc(c["source_mode"])} · {METHOD}</p><p>{esc(note)}</p><p>共同可评估事件 {m["common_events"]}；全部事件 {m["events"]}；米为路程原始单位。</p><h2>移动清单</h2><table><tr><th>SKU</th><th>源库位</th><th>目标库位</th></tr>{move_tr}</table><h2>精确指标</h2><table>{tr}</table></html>'
            filename=stem+'_summary.html';content='text/html; charset=utf-8'
        else:raise ValueError('未知导出格式')
        (ROOT/'exports'/filename).write_text(body,encoding='utf-8')
        return self.send(body,content,filename=filename if kind!='print' else None)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=CFG['port']);args=parser.parse_args()
    # Register read-only inputs before startup so integrity evidence precedes all API access.
    for base in [DATA/'master',DATA/'demand',RISK/'aggregates',RISK/'event_assessments',OPT/'candidate_layouts',OPT/'move_lists',OPT/'replay_results',OPT/'comparisons']:
        for p in base.rglob('*'):
            if p.is_file() and p.suffix in ['.parquet','.json']:track(p)
    for run in RUNS:
        for p in (DATA/'execution'/f'run_id={run}').glob('*.parquet'):track(p)
    for base in [KNOW/'src',KNOW/'config',KNOW/'queries',KNOW/'ontology',KNOW/'outputs/knowledge_v1/knowledge']:
        for p in base.rglob('*'):
            if p.is_file() and '__pycache__' not in str(p):track(p)
    for p in [DATA/'schema.json',DATA/'profiles.json',RISK/'method_config.json',RISK/'reason_codes.json',OPT/'frozen_plans.json',OPT/'plan_cards.json',OPT/'plan_verifications.jsonl',OPT/'manifest.json',KNOW/'outputs/knowledge_v1/graph.ttl'] :track(p)
    for p in (KNOW/'outputs/knowledge_v1').glob('*.json'):track(p)
    for base in [WORK/'仓储风险分析/reports',KNOW/'reports',OPT/'reports']:
        for p in base.glob('*.md'):track(p)
    (ROOT/'reports').mkdir(exist_ok=True)
    before=ROOT/'reports/upstream_hashes_before.json'
    if not before.exists():
        print('Hashing read-only upstream inputs...',flush=True)
        before.write_text(json.dumps(snapshot(),ensure_ascii=False,indent=2),encoding='utf-8')
    else:
        previous=json.loads(before.read_text(encoding='utf-8'))
        added={str(p.relative_to(WORK)) for p in CONSUMED}-set(previous)
        extra=ROOT/'reports/upstream_new_inputs_before.json'
        if added and not extra.exists():
            extra.write_text(json.dumps({k:v for k,v in snapshot().items() if k in added},ensure_ascii=False,indent=2),encoding='utf-8')
    try:server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    except OSError as exc:
        print(f'端口 {args.port} 被占用或不可用：{exc}。请更换 config/paths.json 中 port。',flush=True);sys.exit(2)
    print(f'仓储拣选设计实验室 http://127.0.0.1:{args.port} PID={os.getpid()}',flush=True)
    server.serve_forever()
