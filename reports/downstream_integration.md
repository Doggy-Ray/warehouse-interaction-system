# 下一阶段接入

本地应用提供只读语义接口，前端与导出共用适配结果。新增功能继续保留 source_mode / run / split / plan_id 主上下文与 nullable 语义。

## 真正的本体约束 RAG

可复用 metadata 中的来源片段和方法版本、event_explanation 中的精确证据链、evidence_fragment 中的页码与哈希、knowledge_question 的固定问题以及 paired_event 中的新几何证据包。当前未接LLM、向量索引、生成式检索或聊天。后续索引真实 fragments 时保留source_kind、content_type、验证状态与方法边界；候选布局事实以新回放事件为准。检索失败和证据不足须明确返回，不用原始事件旧数值解释SIM事件。

RAG只能在明确的证据和方法范围内解释；原措施verification_status不被改为现场已验证。新模拟用plan_verifications单独关联。正式LI、时间模型及吞吐积压限制继续作为生成输出的约束。

## 视频与答辩材料

按 README 八步演示即可录制。建议先以 LOC03L051 与首事件查证，再展示unknown空值、S1负向权衡、冻结折中与R03未评估服务能力，最后导出。当前只交付真实截图，不声称已录制视频。

截图直接复用artifacts/screenshots；指标及移动清单使用export接口，答辩数字以导出精确值为依据。录制路线时说明逐边示意不代表实际速度。

## 稳定入口

backend/adapter.py集中维护数据契约；frontend/app.js不拼接任意路径/SQL。新增数据版本在config及适配器切换，并建立新哈希基线。不要覆盖正式上游输出，也不在当前应用自动触发search/evaluate。

本阶段尚无完整调度、在线优化、现场健康验证、真正RAG或视频制作；这些不是隐藏按钮，后续实现需另行验证。
