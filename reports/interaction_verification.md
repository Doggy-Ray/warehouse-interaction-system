# 实际浏览器验收

2026-10-31，真实 Codex 内置 Chromium，服务 http://127.0.0.1:8765/。本报告记录实际执行，不能由构建成功代替。接口自动测试另见 api_test_results.json，浏览器方案读数见 browser_plan_values.json，尺寸/路线/过滤/错误恢复记录见 browser_layout_checks.json。

## 核心流程

|步骤|实际操作与结果|截图|
|---|---|---|
|首页|R01 / test / 冻结折中K20，28,823次，覆盖28,457次，路程371.98km，正式LI未评估|01_overview_1440.jpg|
|库位调查|原始R01→点击LOC03L05单元→第1层LOC03L051；SKU0001，12,134次事件/12,134次FILI>1|02_warehouse_1440.jpg|
|事件证据|列表打开R01_E0000000001；FIRWL10.405195kg、FILI1.235091、起点控制、三层状态与真实页码|03_evidence_drawer_1440.jpg、04_evidence_1440.jpg|
|unknown|精确R01_E0000000224；输入合法，single_lift missing_information，FILI/LI未评估|05_unknown_verified_v2.jpg（独立审查采用此最终稳定截图）|
|九个冻结方案|通过预算与方案select逐个切换K=5/10/20的S1/S2/S3；显示值全部与任务书联调基准一致，精确原值另用Parquet测试|06_plans_1440.jpg、06a_plans_viewport_1440.jpg、browser_plan_values.json|
|前后映射|选择SKU0002：LOC06R091→LOC01R022；同lift_key，FILI1.459284→1.187055；点击新图LOC01R01切到新布局SKU0001，未借原同库位商品|06_plans_1440.jpg与浏览器实际读取；API独立逐SKU核对|
|仅validation候选|S3_K20_w25_s51003 / test显示未评估；切validation后真实27.14超额/千共同事件、349.13km|07_not_evaluated_1440.jpg|
|缺压力组合|R03 / S1_K20显示未评估；不借R01或S3结果|07同类状态，API独立测试对应缺组合|
|已评估R03|冻结折中K20 / all，原始17,757件待完成仍保留，吞吐/积压改善未评估|08_R03_pending_1440.jpg|
|路线|批次R01_B0000000001共22段真实边；实际定时播放至4/22后暂停，再单步到5/22|15_route_playing_1280.jpg、browser_layout_checks.json|
|原始过滤|2026-09-01、W01，276次/273可评估、79次FILI>1；空班次筛选0事件，覆盖和路程未评估|16_empty_original_1280.jpg、browser_layout_checks.json|
|快速切换与刷新|连续R03→R04→R01，最终仍为R01 test 23.54/371.98；刷新后主要URL上下文保留|同源指标见browser_plan_values及本报告记录|
|导出|实际浏览器点击CSV和JSON下载；打开打印摘要，含20个移动SKU和精确指标。服务侧文件逐项与页面和Parquet对账|exports/，25_print_summary_1440.jpg；测试test_10|
|方法记录|真实片段、版本、冻结哈希、原报告和边界可展开|09_methods_1440.jpg、13_methods_1280.jpg|
|服务错误与恢复|实际停止本项目进程后查询显示错误与重试；重新启动，点击重试恢复unknown正确结果|23_service_error_1440.jpg、browser_layout_checks.json|

## 尺寸和抽屉

1440×900检查五个页面及抽屉；1280×900检查方案、仓库、方法、首页、未找到、空结果与unknown抽屉。页面scrollWidth≤viewport宽；1280抽屉宽760px，关闭按钮在视口内，Esc实际可关闭。表格局部滚动，不让整页横向溢出。

1920×1080检查首页与方案；390×844检查方案及unknown阅读/展开/关闭。小屏导航为局部横滚，地图细节依赖放大或表格入口，未承诺完整手机产品或物理触屏手势认证。

尺寸截图：10_plans_1280、11_unknown_drawer_1280、12_not_found_1280、13_methods_1280、14_warehouse_1280、17_overview_1280、18_overview_1920、19_plans_1920、20_plans_mobile、21_unknown_mobile、22_evidence_mobile_top。扩展名均.jpg。

## 证据质量与复现

浏览器控件通过实际DOM定位和真实点击/select操作。网络响应有异步绘制，一张初始unknown截图被独立审查发现仍为旧内容/加载态；已重拍并用磁盘图片查看确认，独立审查只接受05_unknown_verified_v2.jpg。旧的同名首轮记录不作为最终unknown通过依据。

复现以上流程可按README建议顺序，严格等待精确事件ID和结果出现；不要只等待“展开”按钮存在，也不要在上个事件尚可见时截屏。方案数值应与当前run/split/plan标签同时核验。

浏览器控制台在正常核心流程中检查过，无阻断错误。人为停服测试的网络错误是预期测试输入，不冒充正常零错误运行。未做NVDA/VoiceOver、物理触屏、Firefox和Edge跨浏览器专项测试。
