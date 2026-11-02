const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=(x,n=3)=>x==null?'未评估':Number(x).toLocaleString('zh-CN',{maximumFractionDigits:n,minimumFractionDigits:n});

export async function mountLIDemo(host){
 if(!host)return;
 host.innerHTML='<p role="status">正在读取标准化演示配置…</p>';
 try{
  const response=await fetch('/api/li_demo');if(!response.ok)throw Error();const cfg=await response.json();
  if(!host.isConnected)return;
  host.innerHTML=`<div class="note">${esc(cfg.label)}。独立于上方仓储 FILI 分析，不代表整个仓库已完成正式 LI 评估。</div><form id="li-demo-form" class="li-demo-form" novalidate><div class="field"><label for="li-scenario">预设情景</label><select id="li-scenario">${cfg.cases.map(c=>`<option value="${esc(c.id)}">${esc(c.title)}</option>`).join('')}</select></div><div class="field"><label for="li-load">搬运重量（kg）</label><input id="li-load" type="number" step="any" min="0" inputmode="decimal"></div><div class="field"><label for="li-frequency">提举频率（次/分钟）</label><input id="li-frequency" type="number" step="any" min="0" inputmode="decimal"></div><button class="primary" id="li-calculate" type="submit">计算 RWL / LI</button></form><p id="li-condition-summary" class="small"></p><details class="li-demo-details"><summary>明确设定的适用条件与来源</summary><p>${esc(cfg.scope_explanation)}</p><p id="li-geometry" class="small"></p><p id="li-reference" class="small"></p><p class="small">复用原 RNLE 引擎的公制连续乘数与频率查表；与手册英制舍入工作表可能略有差异。新字段和 scope_verified 标志均不能单独证明现场适用性。</p></details><div id="li-result" class="section-gap" role="status" aria-live="polite"></div>`;
  const get=id=>host.querySelector('#'+id);let serial=0;
  const stale=()=>{serial++;get('li-result').innerHTML='<p class="muted">输入已改变，请点击计算更新结果。</p>';};
  function preset(){
   const c=cfg.cases.find(c=>c.id===get('li-scenario').value),e=c.event;
   get('li-load').value=e.load_mass_kg;get('li-frequency').value=c.frequency_per_min;
   get('li-condition-summary').textContent=`工作 ${c.work_minutes} 分钟 → 完全休息 ${c.recovery_minutes} 分钟 · 单一工作段 · 短时（恢复比 1.0） · 频率在整个工作段保持恒定。`;
   get('li-geometry').textContent=`起点 H/V：${num(e.origin_h_m*100,2)} / ${num(e.origin_v_m*100,2)} cm；终点 H/V：${num(e.destination_h_m*100,2)} / ${num(e.destination_v_m*100,2)} cm；D：${num(e.vertical_travel_m*100,2)} cm；不对称角：${e.origin_a_deg}°；抓握：${e.coupling_class}；终点显著控制：${e.destination_control_required?'需要':'不需要'}。`;
   get('li-reference').textContent=c.reference+'。几何与抓握复用例题，工作恢复安排为本演示明确设定。';stale();
  }
  get('li-scenario').onchange=preset;get('li-load').oninput=stale;get('li-frequency').oninput=stale;
  get('li-demo-form').onsubmit=async event=>{
   event.preventDefault();const mine=++serial;const button=get('li-calculate');button.disabled=true;button.textContent='正在计算…';get('li-result').setAttribute('aria-busy','true');
   get('li-result').innerHTML='<p>正在调用原 RNLE 引擎…</p>';
   try{
    const params=new URLSearchParams({calculate:'1',scenario_id:get('li-scenario').value,load_mass_kg:get('li-load').value,frequency_per_min:get('li-frequency').value});
    const res=await fetch('/api/li_demo?'+params);if(!res.ok)throw Error();const r=await res.json();if(mine!==serial||!host.isConnected)return;
    get('li-result').innerHTML=`<div class="evidence-summary"><div class="evidence-metric"><span>推荐重量限值 RWL</span><strong>${num(r.rwl_kg)}</strong><small>kg</small></div><div class="evidence-metric"><span>提举指数 LI</span><strong>${num(r.li)}</strong><small>无量纲 · 标准化情景</small></div><div class="evidence-metric"><span>频率乘数 FM</span><strong>${num(r.fm)}</strong><small>${r.status==='evaluated'?'原引擎查表 / 插值':'未获得有效结果'}</small></div></div><p class="note ${r.status==='evaluated'?'':'warn'}">${esc(r.reason)}</p><p class="small">${r.status==='evaluated'?'计算完成 · '+esc(r.method_version)+' · '+(r.controlling_endpoint==='destination'?'终点控制':'起点控制'):'未评估 · '+esc(r.status)}。仅用于上述设定任务，不并入仓储主数据、方案比较或 RAG。</p>`;
   }catch{if(mine===serial&&host.isConnected)get('li-result').innerHTML='<p class="note warn">计算服务暂不可用，请重试；未填充数值。</p>';}
   finally{if(host.isConnected){button.disabled=false;button.textContent='计算 RWL / LI';get('li-result').setAttribute('aria-busy','false');}}
  };
  preset();
 }catch{if(host.isConnected)host.innerHTML='<p class="note warn">演示配置未能读取；原始事件查询仍可使用。</p>';}
}
