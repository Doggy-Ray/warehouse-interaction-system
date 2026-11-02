"""Small, isolated standardized scenarios; existing upstream engine is read-only."""
import importlib.util
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent


@lru_cache(maxsize=1)
def engine():
    sys.path.insert(0, str(WORK / '仓储风险分析/vendor'))
    spec = importlib.util.spec_from_file_location('li_demo_rnle_engine', WORK / '仓储风险分析/src/engine.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def settings():
    return json.loads((ROOT / 'config/li_demo.json').read_text(encoding='utf-8'))


def evaluate(payload):
    cfg = settings()
    case = next((c for c in cfg['cases'] if c['id'] == payload.get('scenario_id')), None)
    result = dict(status='missing_information', rwl_kg=None, li=None, fm=None,
                  label=cfg['label'], field_verified=False)
    if case is None:
        return dict(result, reason='请选择有效的预设情景。')
    result.update(scenario_id=case['id'], work_minutes=case['work_minutes'], recovery_minutes=case['recovery_minutes'])
    values = {}
    for key, label in [('load_mass_kg', '搬运重量'), ('frequency_per_min', '提举频率')]:
        value = payload.get(key)
        if value is None or value == '':
            return dict(result, reason=label + '缺失；未计算 RWL / LI。')
        try:
            if isinstance(value, bool): raise ValueError()
            value = float(value)
            if not math.isfinite(value) or value <= 0: raise ValueError()
        except (ValueError, TypeError, OverflowError):
            return dict(result, status='invalid_input', reason=label + '必须为有限正数；未计算 RWL / LI。')
        values[key] = value
    # Accept only the documented demonstration contract, never warehouse records.
    expected_scope = {'single_task':True,'two_hands':True,'standing':True,'stable_load':True,
        'unrestricted_space':True,'carry_distance_m':0.15,'lift_motion_seconds':2,
        'temperature_c':20,'relative_humidity_pct':40,'shoe_floor_static_friction':0.5,
        'no_push_pull_climb_or_other_work':True,'smooth_controlled_motion':True,
        'recovery_is_rest':True,'one_bout_only':True,'field_verified':False}
    if cfg['scope'] != expected_scope or case['work_minutes'] != 30 or case['recovery_minutes'] != 30:
        return dict(result, reason='预设条件已改变，需重新核对适用性与工作恢复安排。')
    e = dict(case['event'])
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    e.update(event_id=case['id'], sku_id='STANDARD_DEMO', start_at=start,
             end_at=start+timedelta(seconds=cfg['scope']['lift_motion_seconds']),
             load_mass_kg=values['load_mass_kg'], unit_mass_kg=values['load_mass_kg'],
             handled_container_mass_kg=0, lifted_units=1, hands_used=2, load_stable=True,
             standing=True, space_restricted=False, carry_distance_m=0.15)
    conditions = dict(scope_verified=True, frequency_evidence_id=case['id']+'_explicit_assumptions',
                      frequency_per_min=values['frequency_per_min'], work_minutes=30, recovery_minutes=30)
    assessed = engine().assess_lift(e, conditions, known_skus={'STANDARD_DEMO'})
    status = assessed['rnle_scope_status']
    result.update(status=status, **values, method_version=assessed['method_version'],
                  duration_class=assessed['duration_class'], controlling_endpoint=assessed['controlling_endpoint'],
                  reason_codes=assessed['reason_codes'], reference=case['reference'])
    if status != 'evaluated':
        return dict(result, reason=engine().REASONS.get(assessed['reason_codes'], '输入或适用条件不满足；未计算 RWL / LI。'))
    result.update(rwl_kg=assessed['rwl_kg'], li=assessed['li'], fm=assessed['fm'],
                  reason='LI = 搬运重量 ÷ RWL；大于1提示超过该设定任务的推荐限值，不是伤病概率。'
                         if assessed['li'] > 1 else 'LI = 搬运重量 ÷ RWL；未超过该设定任务的推荐限值，不等于无风险。')
    return result


def handle(query):
    if query.get('calculate') == '1':
        return evaluate(query)
    return settings()
