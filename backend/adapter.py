"""Read-only semantic adapter. No optimization or assessment execution."""
import sys, json, math, re, hashlib, threading, importlib.util
from pathlib import Path
from functools import lru_cache

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT/'config/paths.json').read_text(encoding='utf-8'))
WORK = (ROOT/CFG['workspace']).resolve()
DATA = WORK/'仓储实验数据/v1'
RISK = WORK/'仓储风险分析/outputs/baseline_v1'
KNOW = WORK/'仓储知识溯源'
OPT = WORK/'仓储布局优化/outputs/optimization_v1'
sys.path.insert(0, str(WORK/'仓储风险分析/vendor'))
sys.path.insert(0, str(KNOW/'vendor'))
sys.path.insert(0, str(ROOT/'vendor'))
import duckdb

METHOD = 'RNLE2021-screen-v1.0'
RUNS = ['R01','R02','R03','R04']
LOCK = threading.RLock()
CON = duckdb.connect(':memory:')
CON.execute("SET TimeZone='Asia/Shanghai'")
CON.execute('SET threads=4')
CON.execute("SET memory_limit='1GB'")
CON.execute("SET temp_directory='"+str(ROOT/'cache').replace('\\','/').replace("'","''")+"'")
CONSUMED = set()

def track(p):
    p = Path(p)
    if '*' in str(p):
        CONSUMED.update(x.resolve() for x in p.parent.glob(p.name))
    elif p.is_file(): CONSUMED.add(p.resolve())
    return str(p)

def js(p):
    return json.loads(Path(track(p)).read_text(encoding='utf-8'))

def rows(sql, args=()):
    with LOCK:
        return [json.loads(x[0]) for x in CON.execute('SELECT to_json(q) FROM ('+sql+') q',list(args)).fetchall()]

def pq(p, clause='', args=()):
    return rows('SELECT * FROM read_parquet(?,hive_partitioning=false) '+clause,[track(p),*args])

def clean(x):
    if isinstance(x,float) and not math.isfinite(x): return None
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [clean(v) for v in x]
    return x

def ctx(q):
    c = {k:q.get(k,d) for k,d in [('run','R01'),('split','test'),('source_mode','fixed_workload_replay'),('plan_id','S0_K0'),('date',''),('worker',''),('shift','')]}
    if c['run'] not in RUNS: raise ValueError('无此 run')
    if c['split'] not in ['train','validation','test','all']: raise ValueError('无此 split')
    if c['source_mode'] not in ['original','fixed_workload_replay']: raise ValueError('无此来源模式')
    if c['source_mode']=='original' and c['split']!='all': raise ValueError('原始作业调查使用 all；train/test 为受控回放的订单到达划分')
    if c['source_mode']=='original' and c['plan_id']!='S0_K0': raise ValueError('原始作业不接受候选方案')
    return c

def envelope(c,**kwargs):
    return clean(dict(status='ok',filters=c,data_version='v1',method_version=METHOD,source_mode=c['source_mode'],**kwargs))

@lru_cache(1)
def registry():
    frozen={p['plan_id']:p for p in js(OPT/'frozen_plans.json')['plans']}
    comparisons=pq(OPT/'comparisons/frozen_comparisons.parquet')
    cards=js(OPT/'plan_cards.json')
    result=[]
    for folder in sorted((OPT/'candidate_layouts').iterdir()):
        if not folder.is_dir(): continue
        pid=folder.name
        meta=js(folder/'metadata.json') if (folder/'metadata.json').exists() else frozen.get(pid,{})
        metrics=[r for r in comparisons if r['plan_id']==pid]
        # Non-frozen evaluation registry comes from saved summaries, never folder presence.
        for summary in (OPT/'replay_results'/pid).glob('*/summary.json'):
            for r in js(summary):
                if not any((x['run'],x['split'])==(r['run'],r['split']) for x in metrics): metrics.append(r)
        strategy=meta.get('strategy',pid.split('_')[0])
        label={'S0':'原布局基线','S1':'效率优先','S2':'筛查代理量优先','S3':'折中方案'}.get(strategy,strategy)
        result.append(dict(plan_id=pid,name=label,K=meta.get('K',frozen.get(pid,{}).get('K',0)),frozen=pid in frozen,stage='frozen' if pid in frozen else 'candidate',evaluated=bool(metrics),metrics=metrics,metadata=meta,supported=[dict(run=r['run'],split=r['split']) for r in metrics]))
    return result

def plan(pid):
    return next((p for p in registry() if p['plan_id']==pid),None)

def metric(c,pid=None):
    p=plan(pid or c['plan_id'])
    return next((r for r in p['metrics'] if r['run']==c['run'] and r['split']==c['split']),None) if p else None

def event_path(c):
    if c['source_mode']=='original': return RISK/'event_assessments'/c['run']/'*.parquet'
    if not metric(c): return None
    return OPT/'replay_results'/c['plan_id']/c['run']/'events.parquet'

def where(c,extra=None):
    terms=[]; args=[]
    if c['source_mode']=='fixed_workload_replay' and c['split']!='all':terms.append('split=?');args.append(c['split'])
    for key,col in [('date',"substr(cast(start_at as varchar),1,10)"),('worker','worker_id'),('shift','shift_id')]:
        if c.get(key): terms.append(col+'=?');args.append(c[key])
    for col,val in (extra or {}).items():
        if val: terms.append(col+'=?');args.append(val)
    return (' WHERE '+' AND '.join(terms) if terms else ''),args

AGG="""count(*) events, count(fili) evaluated_events, count(*) FILTER(WHERE fili>1) gt1_events,
 sum(lifted_units) units, avg(fili) fili_mean, max(fili) fili_max,
 sum(CASE WHEN fili>1 THEN fili-1 ELSE 0 END) excess_sum,
 count(*) FILTER(WHERE coupling_class='unknown') unknown_events, count(li) formal_li_nonnull"""

def derive(r):
    r['coverage']=r['evaluated_events']/r['events'] if r['events'] else None
    r['gt1_fraction']=r['gt1_events']/r['evaluated_events'] if r['evaluated_events'] else None
    r['excess_per_1000_evaluated']=r['excess_sum']*1000/r['evaluated_events'] if r['evaluated_events'] else None
    return r

def missing(c,msg='此 run / split / 方案组合未评估；未借用其他结果。'):
    r=envelope(c,message=msg);r['status']='not_evaluated';return r

def geometry(c):
    layouts=pq(DATA/'master/layout_assignments.parquet','WHERE layout_id=?',['L02' if c['run']=='R02' else 'L01']) if c['source_mode']=='original' else pq(OPT/'candidate_layouts'/c['plan_id']/'layout.parquet') if plan(c['plan_id']) else []
    return envelope(c,locations=pq(DATA/'master/locations.parquet'),nodes=pq(DATA/'master/route_nodes.parquet'),edges=pq(DATA/'master/route_edges.parquet'),assignments=layouts)

def overview(c):
    if c['source_mode']=='fixed_workload_replay':
        m=metric(c)
        return envelope(c,metrics=m,baseline=metric(c,'S0_K0')) if m else missing(c)
    path=event_path(c);w,a=where(c)
    m=derive(rows('SELECT '+AGG+' FROM read_parquet(?,hive_partitioning=false)'+w,[track(path),*a])[0])
    # Activities share precisely the same execution date/worker/shift predicates.
    dist=rows('SELECT sum(distance_m) distance_m FROM read_parquet(?,hive_partitioning=false)'+w,[track(DATA/'execution'/f"run_id={c['run']}"/'activities.parquet'),*a])[0]
    m.update(dist);m['scope']='全量匹配原始事件与活动；日期按执行日'
    return envelope(c,metrics=m)

def locations(c):
    path=event_path(c)
    if path is None:return missing(c)
    w,a=where(c)
    data=rows('SELECT location_id,sku_id,'+AGG+' FROM read_parquet(?,hive_partitioning=false)'+w+' GROUP BY location_id,sku_id ORDER BY gt1_events DESC,location_id',[track(path),*a])
    return envelope(c,items=[derive(r) for r in data],denominator='全部匹配事件；阈值占比以各库位可评估事件为分母')

def events(c,q):
    path=event_path(c)
    if path is None:return missing(c)
    w,a=where(c,{k:q.get(k) for k in ['location_id','sku_id','batch_id']})
    offset=max(0,int(q.get('offset',0)));limit=min(100,max(1,int(q.get('limit',50))))
    n=rows('SELECT count(*) total FROM read_parquet(?,hive_partitioning=false)'+w,[track(path),*a])[0]['total']
    cols='event_id,lift_key,sku_id,location_id,lifted_units,fili,firwl_kg,li,coupling_class,controlling_endpoint,start_at,batch_id,single_lift_scope_status'
    if c['source_mode']!='original':cols+=',source_event_id'
    data=rows('SELECT '+cols+' FROM read_parquet(?,hive_partitioning=false)'+w+' ORDER BY event_id LIMIT ? OFFSET ?',[track(path),*a,limit,offset])
    return envelope(c,items=data,total=n,limit=limit,offset=offset,selection={k:q.get(k) for k in ['location_id','sku_id','batch_id']})

@lru_cache(1)
def knowledge():
    # Load upstream src under a distinct package namespace without modifying it.
    name='warehouse_readonly_knowledge'
    spec=importlib.util.spec_from_file_location(name,KNOW/'src/__init__.py',submodule_search_locations=[str(KNOW/'src')])
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    service=__import__(name+'.service',fromlist=['KnowledgeService'])
    for folder in ['src','config','queries','ontology']:
        for f in (KNOW/folder).rglob('*'):
            if f.is_file() and '__pycache__' not in str(f):track(f)
    for f in (KNOW/'outputs/knowledge_v1').glob('*.json'):track(f)
    for f in (KNOW/'outputs/knowledge_v1/knowledge').glob('*.jsonl'):track(f)
    track(KNOW/'outputs/knowledge_v1/graph.ttl')
    return service.KnowledgeService(workspace=WORK)

def verifications(pid):
    return [json.loads(x) for x in Path(track(OPT/'plan_verifications.jsonl')).read_text(encoding='utf-8').splitlines() if json.loads(x)['plan_id']==pid]

def explanation(c,eid):
    if c['source_mode']!='original':return missing(c,'候选证据请使用同一 lift_key 的前后配对入口，不能向原服务传 SIM ID。')
    k=knowledge();pkg=k.explain_event(c['run'],eid)
    if pkg['status']!='ok':
        r=envelope(c,message=pkg['message']);r['status']='not_found';return r
    row=pkg['facts']['saved_assessment'];track(pkg['lineage']['assessment_source']);track(DATA/'demand/orders.parquet');track(DATA/'demand/order_lines.parquet')
    graph=k.get_subgraph(pkg['entity_ids']['event_uri'],max_nodes=18)
    return envelope(c,evidence=pkg,graph=graph,simulation_links=[v for p in registry() if p['frozen'] for v in verifications(p['plan_id']) if set(v.get('source_intervention_ids',[])) & {x['intervention_id'] for x in pkg['candidate_interventions']}])

def location_detail(c,loc):
    g=geometry(c);locrow=next((x for x in g['locations'] if x['location_id']==loc),None)
    if not locrow:
        r=envelope(c,message='精确库位不存在');r['status']='not_found';return r
    groups=locations(c)
    return envelope(c,location=locrow,assignments=[x for x in g['assignments'] if x['location_id']==loc],statistics=[x for x in groups.get('items',[]) if x['location_id']==loc],events=events(c,dict(location_id=loc,limit=50)),sku=pq(DATA/'master/skus.parquet'),contribution_scope='当前过滤的库位统计；知识措施的触发依据是原 run 全期 SKU-库位聚合')

def moves(c):
    p=plan(c['plan_id'])
    if not p:return missing(c)
    path=OPT/'move_lists'/c['plan_id']/'moves.parquet'
    items=pq(path) if path.exists() else []
    skus={s['sku_id']:s for s in pq(DATA/'master/skus.parquet')}
    locs={l['location_id']:l for l in pq(DATA/'master/locations.parquet')}
    for item in items:
        item['sku_dimensions_and_stock']=skus[item['sku_id']]
        item['target_capacity']=locs[item['to_location_id']]
    return envelope(c,items=items,K=p['K'],verification=verifications(c['plan_id']),metadata=p['metadata'])

def paired(c,q):
    if c['source_mode']!='fixed_workload_replay' or not metric(c):return missing(c)
    w,a=where(c,{k:q.get(k) for k in ['sku_id','lift_key']})
    if not q.get('sku_id') and not q.get('lift_key'):raise ValueError('配对需要精确 SKU 或 lift_key')
    after=pq(event_path(c),w+' ORDER BY lift_key LIMIT 1',a)
    if not after:
        r=envelope(c,message='该筛选下没有配对事件');r['status']='not_found';return r
    row=after[0];base={**c,'plan_id':'S0_K0'}
    before=pq(event_path(base),'WHERE lift_key=?',[row['lift_key']])
    return envelope(c,before=before[0] if before else None,after=row,lift_key=row['lift_key'],verification=verifications(c['plan_id']),evidence_source='候选新几何及保存计算；方法片段独立关联，不向旧知识服务传 SIM ID',fragments=knowledge().fragments,original_interventions=[i for i in knowledge().interventions if i['run_id']==c['run'] and i['sku_id']==row['sku_id']])

def route(c,q):
    if c['source_mode']!='original':return missing(c,'路线示意当前仅浏览原始作业；不混用候选近似时间。')
    w,a=where(c)
    batch=q.get('batch_id')
    batchrows=rows('SELECT DISTINCT batch_id FROM read_parquet(?,hive_partitioning=false)'+w+' ORDER BY batch_id LIMIT 50',[track(event_path(c)),*a])
    if not batch: batch=batchrows[0]['batch_id'] if batchrows else None
    valid=rows('SELECT count(*) n FROM read_parquet(?,hive_partitioning=false)'+w+(' AND ' if w else ' WHERE ')+'batch_id=?',[track(event_path(c)),*a,batch])[0]['n']
    if not valid:return envelope(c,batches=batchrows,batch_id=batch,segments=[],events=[],message='当前过滤条件内没有此批次')
    base=DATA/'execution'/f"run_id={c['run']}"
    seg=rows('SELECT a.activity_id,a.sequence_no,a.start_at,a.end_at,e.edge_sequence,e.edge_id,e.traversal_direction FROM read_parquet(?,hive_partitioning=false) a JOIN read_parquet(?,hive_partitioning=false) e USING(activity_id) WHERE a.batch_id=? ORDER BY a.sequence_no,e.edge_sequence',[track(base/'activities.parquet'),track(base/'activity_route_edges.parquet'),batch])
    ev=events(c,dict(batch_id=batch,limit=100))
    return envelope(c,batches=batchrows,batch_id=batch,segments=seg,events=ev['items'],matching_events=ev['total'],playback='按真实边逐段示意，无真实速度或耗时含义；批次含完整路线，统计仍按过滤的全部事件')

def metadata(c):
    k=knowledge()
    report_paths=[('原始基线分析',WORK/'仓储风险分析/reports/baseline_analysis.md'),('知识覆盖',KNOW/'reports/knowledge_coverage.md'),('布局实验结果',OPT/'reports/experiment_results.md'),('上游布局测试记录',OPT/'reports/test_report.md')]
    reports=[dict(title=title,source=str(p),text=Path(track(p)).read_text(encoding='utf-8')) for title,p in report_paths]
    return envelope(c,reports=reports,runs=RUNS,scale=dict(locations=len(pq(DATA/'master/locations.parquet')),skus=len(pq(DATA/'master/skus.parquet'))),run_summaries=pq(RISK/'aggregates/run_summary.parquet'),reason_codes=js(RISK/'reason_codes.json'),fragments=k.fragments,knowledge_manifest=k.manifest,optimization_manifest=js(OPT/'manifest.json'),method_config=js(RISK/'method_config.json'),frozen=js(OPT/'frozen_plans.json'),profiles=js(DATA/'profiles.json'),schema_version=js(DATA/'schema.json')['schema_version'])

def dispatch(name,q):
    c=ctx(q)
    with LOCK:
        if name=='metadata':return metadata(c)
        if name=='overview':return overview(c)
        if name=='warehouse_geometry':return geometry(c)
        if name=='locations':return locations(c)
        if name=='location_detail':return location_detail(c,q.get('location_id',''))
        if name=='events':return events(c,q)
        if name=='event_explanation':return explanation(c,q.get('event_id',''))
        if name=='batch_route':return route(c,q)
        if name=='plans':return envelope(c,items=registry())
        if name=='plan_metrics':return envelope(c,metrics=metric(c),baseline=metric(c,'S0_K0')) if metric(c) else missing(c)
        if name=='plan_moves':return moves(c)
        if name=='paired_event':return paired(c,q)
        if name=='evidence_fragment':
            found=next((x for x in knowledge().fragments if x['fragment_id']==q.get('fragment_id')),None)
            r=envelope(c,fragment=found);r['status']='ok' if found else 'not_found';return r
        if name=='knowledge_question':
            if q.get('question_id') not in ['Q05','Q06']:raise ValueError('仅开放正式LI说明和库位贡献固定查询')
            return envelope(c,result=knowledge().query_knowledge(q['question_id'],dict(run_id=c['run'],location_id=q.get('location_id'))))
        raise ValueError('未知接口')

def snapshot():
    result={}
    for p in sorted(CONSUMED):
        h=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
        result[str(p.relative_to(WORK))]=h.hexdigest()
    return result
