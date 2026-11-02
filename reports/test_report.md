# 测试报告

实际日期：2026-10-31（Asia/Shanghai）。本地应用已启动并完成前后端真实浏览器验收。测试不执行上游优化search/evaluate，也不重新评价正式test。

## 自动化集成结果

`python -B tests/test_api.py`：12项测试，失败0、错误0。最近完整结果及实际耗时保存在api_test_results.json，不把历史耗时称为页面实时速度。

1. 四个原始run全量计数与独立Parquet SQL一致，总799,384；正式LI非空计数0。
2. 日期/操作员过滤、完整分母和分页独立核验，空过滤不静默回退。
3. 480库位/360SKU及真实LOC03L051商品、12,134次事件。
4. 首事件精确FIRWL/FILI、unknown null与不存在ID。
5. S0和九个冻结方案R01/test指标逐字段与原Parquet精确一致。
6. 独立paired.parquet求共同分母与超额算术。
7. 非冻结候选只有validation、缺R03组合、R03原始pending及时间/服务能力边界。
8. 20个移动SKU与新映射逐项相同；同lift_key、源目标、载荷及知识verification_status保持。
9. 原始批次路线边存在、顺序方向连通，过滤为空时不借其他批次。
10. CSV/JSON/打印HTML导出与页面和来源逐项一致，带分母及限制。
11. 非法run、来源、路径样式plan、SQL注入样式库位不产生回退或任意查询。
12. E_FILI真实PDF物理页43、任意事件局部图上限、没有重新计算。

初次测试发现代码把知识字段误写为status；已按真实verification_status修正前端和测试。未用修改上游数据或放宽数值容差的方法消除失败。

## 浏览器与视觉

核心10项流程实际结果详见interaction_verification.md；九方案浏览器读数在browser_plan_values.json。1280/1440/1920及390宽检查、路线播放与空结果记录在browser_layout_checks.json。所有截图为实际浏览器画面，不是原型。

Impeccable 4.8.0项目级安装及实际context/Operate/audit/polish工作流有记录。源码检测发现一个彩色阴影警告，已改中性有偏移柔影；未伪称检测器零警告，也未反复扫描。独立完工审查在重拍unknown证据后disposition: ship，范围为所供截图、前端源码和验证记录，见finish_review.md。

Windows启动、指定PID停止和重启实际成功。停止脚本首版依赖WMI时遭遇本环境访问限制，已改为本机health的项目路径/PID核验，不使用杀全部Python/Node进程方式。当前服务信息以server.pid和/api/health为准。

## 上游完整性

verify_integrity.py对393个登记输入完成前后SHA-256核验：变化0、缺失0、未登记0，status=passed。包含正式Parquet、冻结/候选元数据、知识图与规则/源代码和接入报告；不消费独立性能集、evaluation_only或1.99GB证据JSONL。详细清单为upstream_hashes_before.json、upstream_new_inputs_before.json、upstream_hashes_after.json与integrity_result.json。

缓存、前端、日志、导出与截图仅写本成果目录；上游源代码和冻结方案没有修改。

## 已知限制

- 产品语义限制：正式LI未评估；近似回放不能推出吞吐、积压或健康改善；只有一次实际主实验replicate。
- 性能：知识服务首次装载需要数秒；服务复用单实例和DuckDB连接，采用锁串行化查询，适合本机课程展示，并未宣称并发生产服务。
- 浏览：批次选择器前50项、事件分页50条；统计是全量过滤。SKU配对默认当前划分首个真实lift_key，接口可精确输入key。
- 验证覆盖：实际内置Chromium及模拟尺寸；未做读屏器、实体触屏及多浏览器全套测试。小屏保留阅读和基本操作。
- 当前无在线优化、完整调度、现场健康验证、真正RAG和视频录制；这些能力没有假按钮，也没有宣称完成。

任务书要求的五个页面、主要真实数据流程、导出、启动说明、浏览器与多尺寸截图已实现；上述专项未测范围明确保留。
