# 仓储拣选设计实验室
<!-- impeccable:product-schema 1 -->

## Platform
web

## Stack
任务书授权依据当前环境调整技术栈。采用 Python 标准库本地 HTTP 服务、上游只读 DuckDB / KnowledgeService，以及原生 JavaScript 模块与 SVG；避免引入编译和网络运行依赖。

## Users
工业设计课程展示者、教师与观众，在本机浏览器中查证仓储实验并比较既有方案。

## Product Purpose
完成查看问题→点击库位调查→核对事件证据→筛选预算与方案→比较同源结果→导出。

## Capabilities and Constraints
五页：项目总览、仓库调查、风险与证据、方案实验、方法记录。真实 Parquet 全量查询、分页返回；上游全部只读，不生成数据、不重算优化。新增上下文证据助手，复用真实语义检索和受累计预算约束的DeepSeek生成；未配置或额度用尽时仍保留五页与证据查看。
原始作业与 fixed_workload_replay 分离；方案比较严格绑定 run/split/plan。FILI 为有条件单次筛查；正式 LI 为 null。时间模型未验证；吞吐及积压改善未评估，R03 原始积压保留。
unknown 保留于事件总量；FILI>1 分母为可评估事件。仅一次实际主实验重复。预算筛选已计算方案。

## Evidence on Hand
../仓储实验数据/v1、../仓储风险分析/outputs/baseline_v1、../仓储知识溯源/outputs/knowledge_v1、../仓储布局优化/outputs/optimization_v1。

## Product Principles
数值可追溯；先准确再修饰；缺失明确；同源比较；交互优先于装饰。

## Accessibility & Inclusion
中文标签、键盘可达、颜色同时配文字；1280 宽无横向页面溢出。地图提供库位输入及排行表替代入口。
