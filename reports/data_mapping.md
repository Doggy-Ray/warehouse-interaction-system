# 数据映射与语义契约

所有路径相对工作区；运行时配置集中在 config/paths.json。正式数据均从 Parquet / JSON / JSONL 读取，不从报告摘数字注入组件。

|界面/指标|真实来源|口径与单位|
|---|---|---|
|原始事件、任意过滤、库位排名|仓储风险分析/outputs/baseline_v1/event_assessments/R01-R04/*.parquet|全量匹配；按 start_at 的 Asia/Shanghai 执行日期、worker_id、shift_id 筛选|
|原始事件数|上述文件 COUNT(*)|含 unknown，不用样例行数|
|可评估/覆盖率|COUNT(fili) / COUNT(*)|沿用上游状态约定；已评估且非空，完整主集状态一致；0/0返回null|
|FILI>1占比|COUNT WHERE fili>1 / COUNT(fili)|分母为可评估事件；原始小数到百分数仅在显示层乘100|
|库位超额代理量|SUM(max(fili-1,0))|阈值超额的无量纲和，不是超阈值计数、概率或正式LI|
|原始路程|仓储实验数据/v1/execution/run_id=Rxx/activities.parquet|相同执行日期/人/班次过滤，SUM(distance_m)，含local距离，显示除1000为km|
|SKU、480库位、通道图|仓储实验数据/v1/master/*.parquet|左右侧、单元、四层承载面、DEPOT、实际图边坐标|
|原始商品分配|master/layout_assignments.parquet|R02用L02，其余用L01|
|原始批次路线|activities JOIN activity_route_edges USING(activity_id)|按活动sequence_no和edge_sequence；有方向的真实边；播放不使用伪物理时标|
|方案注册表|candidate_layouts + frozen_plans.json + comparisons/frozen_comparisons.parquet + replay_results/*/*/summary.json|candidate/frozen/evaluated分开；支持组合来自保存指标行，不能只看文件夹|
|方案指标|comparisons/frozen_comparisons.parquet，非冻结summary.json|严格 run/split/plan；source_mode=fixed_workload_replay|
|方案主基线|相同run/split的S0_K0指标|不使用原始全期统计拼接|
|超额/千共同事件|excess_per_1000_common|共同可评估事件common_events作分母；独立 paired.parquet 对账|
|占比变化|gt1_fraction差×100|百分点与相对百分比同时注明，正负都展示|
|新布局|candidate_layouts/plan/layout.parquet|按SKU映射到新库位，不能把目标库位原SKU冒充新商品|
|移动清单及约束|move_lists/plan/moves.parquet、candidate metadata、master/skus和locations|预算budget_count按SKU；静态可行性读取上游metadata与原依据，展示尺寸/目标容量|
|配对事件|replay_results/plan/run/events.parquet 与 S0 同run的events.parquet|当前split、SKU或精确lift_key查候选；同lift_key取基线，载荷/源ID/新几何保留|
|原始事件证据|原 KnowledgeService.explain_event/get_subgraph|服务单实例，独立namespace导入；任意精确事件可用，图≤18节点，浏览器显示≤12，不用图计数替代统计|
|候选证据包|新事件行 + plan_verifications.jsonl + 原知识片段/措施|不向旧服务传SIM ID。verification_status原值保持，模拟记录另列|
|固定知识问题|KnowledgeService Q05 / Q06|正式LI原因与原run全期库位贡献；不冒充聊天/RAG|
|文档片段|knowledge_v1/knowledge/fragments.jsonl|来源性质、内容类型、印刷页、PDF物理页、哈希及限制|
|历史记录|上游manifest和固定白名单报告|仅历史结果，不称实时性能|

## API

只读 GET `/api/metadata`, `/overview`, `/warehouse_geometry`, `/locations`, `/location_detail`, `/events`, `/event_explanation`, `/batch_route`, `/plans`, `/plan_metrics`, `/plan_moves`, `/paired_event`, `/evidence_fragment`, `/knowledge_question`, `/export`。

通用参数：run、split、plan_id、source_mode。原始模式要求 source_mode=original、split=all、plan_id=S0_K0，另接受date/worker/shift。前端的原始页面覆盖对应上下文，URL中的方案上下文在切回方案页时保留。事件列表limit最多100、默认50，响应total来自全量匹配。

库位location_id、事件event_id、批次batch_id、配对sku_id/lift_key均精确查询。路径白名单由服务生成，用户不能传SQL、SPARQL或磁盘路径。SQL条件参数化。json保留null、不输出NaN/Infinity，响应包含filters、data_version、method_version、source_mode及必要分母。

`status=not_evaluated`表示当前组合无已保存评价；`not_found`表示精确对象不存在。非法来源/run/split返回400，不静默回退。

## 导出与完整性

`/api/export?kind=moves|metrics|print` 产生移动CSV、指标JSON、可打印HTML，并写入本应用exports；所有导出携带当前方案过滤、方法、共同/可评估/全部分母及模拟边界。

初始输入哈希：upstream_hashes_before.json；新增只读报告在接入前记录到upstream_new_inputs_before.json；结束由verify_integrity.py对实际注册读取范围逐文件复核。这里保守记录了可能被页面读取的正式表和代码，不记录独立性能集或1.99GB证据JSONL。缓存、导出、日志、截图仅写本成果目录。
