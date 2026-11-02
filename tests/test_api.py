"""Reproducible integration checks against running localhost and independent Parquet SQL."""
import unittest, json, sys, csv, io, time, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT.parent/'仓储风险分析/vendor'))
import duckdb
BASE='http://127.0.0.1:8765/api/'
CON=duckdb.connect(':memory:')
OPT=ROOT.parent/'仓储布局优化/outputs/optimization_v1'
RISK=ROOT.parent/'仓储风险分析/outputs/baseline_v1'
def req(name,**q):
    with urllib.request.urlopen(BASE+name+'?'+urllib.parse.urlencode(q),timeout=120) as r:return r.read()
def api(name,**q):return json.loads(req(name,**q))
ORIG=dict(source_mode='original',split='all',run='R01',plan_id='S0_K0')
class Integration(unittest.TestCase):
    def test_01_full_original_counts(self):
        total=0
        for run in ['R01','R02','R03','R04']:
            m=api('overview',**{**ORIG,'run':run})['metrics']
            counts=CON.execute('select count(*),count(fili),count(li) from read_parquet(?,hive_partitioning=false)',[str(RISK/'event_assessments'/run/'*.parquet')]).fetchone()
            self.assertEqual((m['events'],m['evaluated_events'],m['formal_li_nonnull']),counts);total+=m['events']
        self.assertEqual(total,799384)
    def test_02_filtered_full_aggregate_and_paging(self):
        q={**ORIG,'date':'2026-09-01','worker':'W01'}
        m=api('overview',**q)['metrics'];e=api('events',**q,limit=3)
        n=CON.execute("select count(*) from read_parquet(?,hive_partitioning=false) where worker_id=? and cast(start_at as date)=?",[str(RISK/'event_assessments/R01/*.parquet'),'W01','2026-09-01']).fetchone()[0]
        self.assertEqual(m['events'],n);self.assertEqual(e['total'],n);self.assertEqual(len(e['items']),3)
        self.assertEqual(api('overview',**{**q,'worker':'W999'})['metrics']['events'],0)
    def test_03_location_and_geometry(self):
        d=api('location_detail',**ORIG,location_id='LOC03L051')
        self.assertEqual(d['assignments'][0]['sku_id'],'SKU0001');self.assertEqual(d['statistics'][0]['events'],12134)
        g=api('warehouse_geometry',**ORIG)
        self.assertEqual(len(g['locations']),480);self.assertEqual(len(g['assignments']),360)
        self.assertIn('DEPOT',[n['node_id'] for n in g['nodes']])
    def test_04_exact_event_and_unknown(self):
        first=api('event_explanation',**ORIG,event_id='R01_E0000000001')['evidence']
        self.assertAlmostEqual(first['numeric_results']['firwl_kg'],10.405195227141066,places=10)
        self.assertAlmostEqual(first['numeric_results']['fili'],1.235091107816998,places=12)
        self.assertEqual(first['facts']['saved_assessment']['controlling_endpoint'],'origin')
        unknown=api('event_explanation',**ORIG,event_id='R01_E0000000224')['evidence']
        self.assertIsNone(unknown['numeric_results']['fili']);self.assertIsNone(unknown['numeric_results']['li'])
        self.assertEqual(unknown['assessment_statuses']['single_lift_scope_status'],'missing_information')
        self.assertEqual(api('event_explanation',**ORIG,event_id='R01_E9999999999')['status'],'not_found')
    def test_05_all_nine_frozen_values_exact(self):
        frozen=json.loads((OPT/'frozen_plans.json').read_text(encoding='utf-8'))['plans']
        for p in frozen:
            pid=p['plan_id'];r=api('plan_metrics',run='R01',split='test',plan_id=pid)
            source=json.loads(CON.execute("select to_json(t) from read_parquet(?) t where plan_id=? and run='R01' and split='test'",[str(OPT/'comparisons/frozen_comparisons.parquet'),pid]).fetchone()[0])
            for key in ['excess_per_1000_common','distance_m','common_events','events','gt1_events','coverage']:
                self.assertEqual(r['metrics'][key],source[key],(pid,key))
            self.assertEqual(r['baseline']['plan_id'],'S0_K0');self.assertEqual(r['baseline']['run'],r['metrics']['run']);self.assertEqual(r['baseline']['split'],r['metrics']['split'])
        s1=api('plan_metrics',plan_id='S1_K20')['metrics'];self.assertGreater(s1['excess_relative_change'],0);self.assertLess(s1['distance_relative_change'],0)
    def test_06_common_denominators_independent(self):
        pid='S3_K20_w50_s51003';r=api('plan_metrics',plan_id=pid)['metrics']
        p=OPT/'replay_results'/pid/'R01/paired.parquet'
        n,ex=CON.execute("select count(*),sum(greatest(candidate_fili-1,0)) from read_parquet(?) where common and split='test'",[str(p)]).fetchone()
        self.assertEqual(n,r['common_events']);self.assertAlmostEqual(ex*1000/n,r['excess_per_1000_common'],places=9)
        self.assertAlmostEqual(r['gt1_fraction'],r['gt1_events']/r['evaluated_events'],places=12)
    def test_07_candidate_and_stress_isolation(self):
        reg=api('plans')['items'];p=next(p for p in reg if not p['frozen'])
        self.assertEqual(api('plan_metrics',plan_id=p['plan_id'],split='test')['status'],'not_evaluated')
        self.assertEqual(api('plan_metrics',plan_id=p['plan_id'],split='validation')['status'],'ok')
        self.assertEqual(api('plan_metrics',plan_id='S1_K5',run='R03',split='all')['status'],'not_evaluated')
        r=api('plan_metrics',plan_id='S3_K20_w50_s51003',run='R03',split='all')['metrics']
        self.assertEqual(r['original_pending_units'],17757);self.assertFalse(r['time_model_verified']);self.assertEqual(r['backlog_change'],'not_evaluated');self.assertEqual(r['service_throughput'],'not_evaluated')
    def test_08_move_layout_and_paired_identity(self):
        c=dict(plan_id='S3_K20_w50_s51003',run='R01',split='test')
        moves=api('plan_moves',**c)['items'];g=api('warehouse_geometry',**c)
        self.assertEqual(len(moves),20)
        for move in moves:
            self.assertEqual(next(a for a in g['assignments'] if a['sku_id']==move['sku_id'])['location_id'],move['to_location_id'])
        move=moves[0];r=api('paired_event',**c,sku_id=move['sku_id'])
        self.assertEqual(r['before']['lift_key'],r['after']['lift_key']);self.assertEqual(r['before']['sku_id'],r['after']['sku_id'])
        self.assertEqual(r['before']['location_id'],move['from_location_id']);self.assertEqual(r['after']['location_id'],move['to_location_id'])
        self.assertNotEqual(r['before']['fili'],r['after']['fili']);self.assertTrue(r['original_interventions'])
        self.assertTrue(all(i['verification_status'] in ['not_simulated','needs_measurement'] for i in r['original_interventions']))
    def test_09_routes_real_edges_and_filter(self):
        r=api('batch_route',**ORIG);g=api('warehouse_geometry',**ORIG);edges={x['edge_id']:x for x in g['edges']}
        self.assertGreater(len(r['segments']),0)
        last=None;activity=None
        for s in r['segments']:
            e=edges[s['edge_id']];ends=(e['from_node_id'],e['to_node_id']) if s['traversal_direction']=='forward' else (e['to_node_id'],e['from_node_id'])
            if activity==s['activity_id']:self.assertEqual(last,ends[0])
            last=ends[1];activity=s['activity_id']
        self.assertEqual(api('batch_route',**{**ORIG,'worker':'W999'})['segments'],[])
    def test_10_export_matches_pages_and_source(self):
        c=dict(plan_id='S3_K20_w50_s51003',run='R01',split='test')
        metrics=api('export',**c,kind='metrics');page=api('plan_metrics',**c)
        self.assertEqual(metrics['metrics'],page['metrics']);self.assertEqual(metrics['denominators']['common_events'],page['metrics']['common_events'])
        text=req('export',**c,kind='moves').decode('utf-8-sig');out=list(csv.DictReader(io.StringIO(text)));moves=api('plan_moves',**c)['items']
        self.assertEqual(len(out),len(moves))
        for a,b in zip(out,moves):
            for k in ['sku_id','from_location_id','to_location_id']:self.assertEqual(a[k],b[k])
            self.assertEqual(a['source_mode'],'fixed_workload_replay');self.assertEqual(a['split'],'test')
        self.assertIn('time_model_verified=false',req('export',**c,kind='print').decode('utf-8'))
    def test_11_invalid_parameters_no_fallback(self):
        for q in [dict(run="R01' OR 1=1 --"),dict(source_mode='original',split='test'),dict(plan_id='../../secret')]:
            if 'plan_id' in q:self.assertEqual(api('plan_metrics',**q)['status'],'not_evaluated')
            else:
                with self.assertRaises(urllib.error.HTTPError):api('overview',**q)
        r=api('events',**ORIG,location_id="LOC' OR 1=1 --")
        self.assertEqual(r['total'],0)
    def test_12_fragment_real_locator_and_bounded_graph(self):
        f=api('evidence_fragment',fragment_id='E_FILI')['fragment'];self.assertEqual(f['pdf_physical_page'],43)
        d=api('event_explanation',**ORIG,event_id='R01_E0000000500')
        self.assertLessEqual(len(d['graph']['nodes']),18)
        self.assertEqual(d['evidence']['lineage']['recalculated'],False)

if __name__=='__main__':
    start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Integration);out=io.StringIO();result=unittest.TextTestRunner(stream=out,verbosity=2).run(suite)
    (ROOT/'reports').mkdir(exist_ok=True)
    report=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),seconds=time.perf_counter()-start,success=result.wasSuccessful(),output=out.getvalue())
    (ROOT/'reports/api_test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(out.getvalue());sys.exit(not result.wasSuccessful())
