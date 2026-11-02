const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let controller=null,sequence=0,getContext=null,lastFocus=null;
const labels={answered:'已生成 · 自动格式校验通过',partially_answered:'部分回答',insufficient_evidence:'证据不足 / 未通过校验',context_required:'需要明确上下文',not_found:'精确对象不存在',model_unavailable:'生成模型不可用'};
export function resetAssistant(){controller?.abort();sequence++;const el=document.querySelector('#rag-assistant');if(el)el.remove();document.querySelector('#rag-open')?.remove();}
export function mountAssistant(contextGetter,page){
 getContext=contextGetter;if(!['evidence','plans','warehouse'].includes(page))return;
 const button=document.createElement('button');button.type='button';button.id='rag-open';button.className='assistant-trigger';button.setAttribute('data-open','false');button.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h12v14H4zM7 8h6M7 11h4M14 14a3 3 0 1 0 6 0 3 3 0 0 0-6 0m5 2 3 3"/></svg><span>上下文证据助手</span>';button.onclick=open;
 document.querySelector('#heading .heading').append(button);
}
function open(){
 lastFocus=document.activeElement;document.querySelector('#rag-assistant')?.remove();const c=getContext();
 const el=document.createElement('aside');el.id='rag-assistant';el.setAttribute('role','dialog');el.setAttribute('aria-labelledby','rag-title');
 el.innerHTML=`<div class="rag-head"><div><h2 id="rag-title">上下文证据助手</h2><p class="small">围绕当前对象提问，沿引用返回依据。</p></div><button id="rag-close" aria-label="关闭上下文证据助手">关闭</button></div><div class="rag-body"><section class="rag-context" aria-label="当前查证范围"><div class="rag-context-line"><strong>当前查证范围</strong><span class="tag">${c.source_mode==='original'?'原始作业':'受控回放'}</span></div><p>${esc(c.run)} <span class="muted">/</span> ${esc(c.split)} <span class="muted">/</span> <strong>${esc(c.plan_id)}</strong></p><p class="mono">${esc(c.source_mode)}${c.event_id||c.sku_id?' · '+esc(c.event_id||c.sku_id):''}</p></section><p id="rag-model" class="rag-model-status" data-state="loading" role="status">正在核对模型与语义索引…</p><form id="rag-form"><div class="rag-fields"><div><label for="rag-group">证据组织方式</label><select id="rag-group"><option value="B2">B2 · 本体约束混合检索</option><option value="B1">B1 · 普通语义向量检索</option></select></div><div><label for="rag-object">${c.source_mode==='original'?'精确事件 ID':'配对 SKU ID'}</label><input id="rag-object" value="${esc(c.event_id||c.sku_id||'')}" autocomplete="off"></div></div><p class="small rag-form-hint">${c.source_mode==='original'?'可清空事件 ID，询问通用定义。':'可清空 SKU ID，询问当前方案。'} 切换页面、方案或对象后，请重新查证。</p><label for="rag-question">关于当前对象的问题</label><textarea id="rag-question" rows="4" maxlength="2000" required placeholder="例如：为什么 FILI 可算而正式 LI 为空？"></textarea><div class="actions rag-submit-row"><button id="rag-submit" type="submit" class="primary">检索证据并提问</button><button id="rag-cancel" type="button" disabled>取消请求</button></div></form><div id="rag-result" tabindex="-1" aria-live="polite" aria-busy="false"><div class="rag-empty"><h3>回答与依据将在这里展开</h3><p>先确认上方查证范围。提交后可核对精确事实、来源片段与检索过程。</p></div></div></div>`;
 document.body.append(el);document.querySelector('#rag-question').focus();
 document.querySelector('#rag-open')?.setAttribute('data-open','true');
 document.querySelector('#rag-close').onclick=()=>{controller?.abort();sequence++;el.remove();document.querySelector('#rag-open')?.setAttribute('data-open','false');lastFocus?.focus();};
 document.querySelector('#rag-cancel').onclick=()=>{controller?.abort();sequence++;finish();document.querySelector('#rag-result').innerHTML='<p role="status">已取消。迟到结果不会覆盖当前内容。</p>';};
 el.onkeydown=e=>{if(e.key==='Escape')document.querySelector('#rag-close').click();};
 document.querySelector('#rag-form').onsubmit=submit;
 document.querySelector('#rag-group').onchange=()=>{controller?.abort();sequence++;finish();document.querySelector('#rag-result').innerHTML='<p class="muted">检索方式已切换，请重新提交。</p>';};
 document.querySelector('#rag-object').oninput=()=>{controller?.abort();sequence++;finish();document.querySelector('#rag-result').innerHTML='<p class="muted">对象已修改，请重新提交问题以读取对应事实。</p>';};
 fetch('/api/rag/status').then(r=>r.json()).then(s=>{if(!el.isConnected)return;const status=document.querySelector('#rag-model');status.dataset.state=s.generation_configured&&s.project_data_authorized&&s.embedding_index_ready?'ready':'limited';status.textContent=(s.generation_configured?('生成模型：'+s.generation_model+(s.project_data_authorized?'':' · 项目数据外发授权待确认')):'生成模型尚未配置 · 仅检索与事实查看')+'；'+(s.embedding_index_ready?'BGE 中文语义索引已就绪 · '+s.fragments+' 个真实片段':'仅稀疏检索，语义索引未就绪');}).catch(()=>{if(el.isConnected){document.querySelector('#rag-model').dataset.state='error';document.querySelector('#rag-model').textContent='助手状态暂不可用；原有数据浏览可继续。';}});
}
function finish(){const b=document.querySelector('#rag-submit');if(b){b.disabled=false;b.textContent='检索证据并提问';}const c=document.querySelector('#rag-cancel');if(c)c.disabled=true;document.querySelector('#rag-result')?.setAttribute('aria-busy','false');}
async function submit(e){
 e.preventDefault();controller?.abort();controller=new AbortController();const mine=++sequence;
 const context={...getContext()},object=document.querySelector('#rag-object').value.trim();delete context.event_id;delete context.sku_id;
 if(object)context[context.source_mode==='original'?'event_id':'sku_id']=object;
 document.querySelector('#rag-submit').disabled=true;document.querySelector('#rag-submit').textContent='正在查证…';document.querySelector('#rag-cancel').disabled=false;
 document.querySelector('#rag-result').setAttribute('aria-busy','true');document.querySelector('#rag-result').innerHTML='<div class="rag-progress" role="status"><strong>正在查证当前对象</strong><p>读取精确事实、检索核验片段，并检查生成配置…</p></div>';
 const timeout=setTimeout(()=>controller.abort('timeout'),115000);
 try{
  const response=await fetch('/api/rag/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:document.querySelector('#rag-question').value,context,group:document.querySelector('#rag-group').value}),signal:controller.signal});
  const d=await response.json();if(mine!==sequence)return;if(!response.ok)throw Error(d.message||'助手请求失败');
  const citations=d.citations||[];
  document.querySelector('#rag-result').innerHTML=`<div class="rag-result-heading"><h3>查证结果</h3><span class="tag ${d.answer_status==='answered'?'':'gray'}">${esc(labels[d.answer_status]||d.answer_status)}</span></div><p class="rag-answer">${esc(d.answer||d.message||'没有可显示回答。')}</p>${d.generation_metadata?.cache_hit?`<p class="note">缓存命中 · 原始模型 ${esc(d.generation_metadata.returned_model||d.generation_metadata.model)} · ${esc(d.generation_metadata.generated_at)}</p>`:''}${d.answer?'<p class="small">自动校验仅检查格式、引用身份与数值锚点；引用是否支持全部措辞仍需核对。</p>':''}<div class="rag-claims">${(d.claims||[]).map(cl=>`<p>${esc(cl.text)} ${(cl.citations||[]).map(id=>`<a href="#cite-${esc(id)}">[${esc(id)}]</a>`).join(' ')}</p>`).join('')}</div><h3>可核对的证据 · ${citations.length}</h3>${citations.map(c=>citation(c,context)).join('')}<section class="rag-limitations"><h3>解释边界</h3><ul>${(d.limitations||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</ul></section><details class="rag-trace"><summary>检索过程与生成状态</summary><pre>${esc(JSON.stringify({trace_id:d.retrieval_trace_id,retrieval:d.retrieval,generation:d.generation_metadata,validation_errors:d.validation_errors},null,2))}</pre></details>`;
  document.querySelectorAll('#rag-result a[href^="#cite-"]').forEach(link=>link.onclick=event=>{event.preventDefault();const target=document.getElementById(link.getAttribute('href').slice(1));if(target){target.open=true;target.scrollIntoView({block:'start'});}});
 }catch(err){if(mine!==sequence)return;document.querySelector('#rag-result').innerHTML=`<p class="error" role="alert">${esc(err.name==='AbortError'||controller.signal.aborted?'请求已超时或取消；可重新提交。':err.message)} 原有页面仍可使用。</p>`;}
 finally{clearTimeout(timeout);if(mine===sequence)finish();}
}
function citation(c,context){
 if(c.kind==='structured_fact'){
  const q=new URLSearchParams(context);q.set('page',c.id==='F_EVENT'?'evidence':'plans');
  return `<details class="rag-citation" id="cite-${esc(c.id)}"><summary>${esc(c.id)} · 精确结构化事实</summary><p class="small">${esc(c.api)} · ${esc(c.method_version)}</p><p class="mono">${esc(c.source)}</p><a href="/?${esc(q)}">回到对应${c.id==='F_EVENT'?'事件证据':'方案对比'}</a><pre>${esc(JSON.stringify(c.fact,null,2))}</pre></details>`;
 }
 return `<details class="rag-citation" id="cite-${esc(c.id)}"><summary>${esc(c.fragment_id)} · ${c.source_kind==='external_method'?'外部方法忠实摘要':'项目说明'}</summary><p>${esc(c.text)}</p><dl class="kv"><dt>印刷页 / PDF页</dt><dd>${esc(c.printed_page||'无')} / ${esc(c.pdf_physical_page||'无')}</dd><dt>章节 / 文档</dt><dd>${esc(c.section)} / ${esc(c.document_id)}</dd><dt>核验状态</dt><dd>${esc(c.verification_status)}</dd><dt>内容类型</dt><dd>${esc(c.content_type)}</dd></dl><p class="small">${esc(c.limitations)}</p><p class="mono">来源 SHA-256：${esc(c.sha256)}</p><pre>${esc(JSON.stringify(c,null,2))}</pre></details>`;
}
