# Impeccable 设计审查与修改

## 来源与实际配置
官方安装说明：https://impeccable.style/tutorials/getting-started/；官方仓库：https://github.com/pbakaus/impeccable。
2026-10-31 下载官方文档，执行 `npx --yes impeccable install --providers=codex --scope=project --no-hooks --yes`，安装版本 4.8.0 到本项目 `.agents/skills/impeccable`，未覆盖既有全局技能。

实际读取 SKILL.md、reference/init.md、new-work.md、mode-operate.md、operate.md、craft-floor.md、audit.md、polish.md。另读取 critique.md 了解入口，没有把未执行的双代理 critique 工作流记作已执行。

初次 context 启动器因默认全局缓存不可写而失败；随后设置 `IMPECCABLE_HOME` 为本项目 `.impeccable/runtime`，官方 engine-probe 下载引擎 0.1.18，context 成功读取 PRODUCT.md / DESIGN.md。技能通过读取实际说明并执行其工作流使用，不把 `$impeccable` 当 PowerShell 命令，不宣称动态技能菜单已经重载。

## 产品与方向
按任务书直接落地 Operate 模式：地图调查和方案对照为核心，原生筛选、表格、证据抽屉；上下文写入 PRODUCT.md，视觉规范写入 DESIGN.md。任务书已给出受众、五页、颜色语义、布局与授权技术栈选择，并明确无需重新搜索布局，因此未运行概念抽签或布局选择访谈。应用代码直接实现，不使用图片原型。

## 第一轮实际浏览器审查
环境：真实 Codex in-app Chromium，1440×900。

|问题|影响|修改|
|---|---|---|
|总览重复介绍块与比较页顶部较高|首屏地图露出不足|压缩总览介绍和方案比较区间距，保留指标、分母与模型边界|
|原知识措施字段误用 status|状态文本未显示|按真实 verification_status 读取，测试独立核对 not_simulated / needs_measurement|
|库位快速切换存在事件列表晚回可能|同页旧响应可能串库位|追加库位请求代次与精确位置检查，页面请求另有 AbortController 和代次|
|覆盖率地图图例只显示小数|观众难读分母|改为百分数标签并显式说明可评估/全部匹配事件|
|空筛选路程 null 经 JS 除法变0|空值语义错误|先判断 null 再换算 km|
|抽屉查询时可能保留滚动位置|新事件从中段开始读|每次打开重置抽屉滚动，并保留固定关闭按钮|

第二轮复查、检测器与独立完工审查结果见本报告后续记录及关联 JSON。


## 第二轮复查与独立结果

浏览器在1440×900、1280×900、1920×1080和390×844实际检查。关键页无全页横向溢出；1280抽屉关闭位置在视口内，Esc可关闭。覆盖率图例显示0%至100%及分母；空过滤不把null路程显示0。服务实际停机后显示错误与重试，再启动后恢复正确unknown结果。路线实际播放到4/22，暂停再单步到5/22。

按官方引擎执行一次 `detect --json frontend`，原始输出见impeccable_detector.json：一条彩色阴影警告。实际抽屉是有偏移柔影，已统一改为中性 #00000024；不把源码扫描结果当作渲染对比度认证，按技能不重复扫描。

独立finish reviewer首次发现unknown截图抓取了旧事件/加载态。改用精确ID确认后、独立稳定调用保存新文件05_unknown_verified_v2.jpg，并用磁盘图片查看实际内容。最终完整审查disposition: ship，详见finish_review.md，结论限于提供的截图、前端源码和测试证据，不扩张为未运行的读屏/触屏/其他浏览器认证。

独立documenter从当前源码提取规范，完成DESIGN.md的八个标准章节和机器可读tokens，以及.impeccable/design.json v2。校验token引用、25个源码实际颜色、9个组件片段和叙述规则通过。

最后对稳定前后地图截图发现前横通道文字过近于通道6标签，单独将该SVG标签上移14个viewBox单位，保留所有数据与布局；最终截图26_plan_maps_verified_v3.jpg复查对应文字位置。其余规则不变。


## 2026-11-01 后续精修
继续使用现有Impeccable polish流程，依据当前已接入RAG助手的实际实现完成精修；修改、前后截图、约束与真实验证见 [本轮记录](polish_2026-11-01.md)。原审查结论范围与历史记录保持原样。
