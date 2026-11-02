---
name: 仓储拣选设计实验室
description: 中文本地仓储研究工作台，以地图、事件与同源方案比较组织证据。
colors:
  ink: "#22364a"
  muted: "#536577"
  nav: "#172c42"
  accent: "#087c78"
  orange: "#ad570e"
  line: "#d8e0e6"
  ground: "#f1f4f6"
  unknown: "#aeb7c0"
  surface: "#fff"
  control-border: "#bdcbd5"
  focus: "#108f9a"
  primary-hover: "#05615f"
  nav-hover: "#233e57"
  nav-active: "#2c4f66"
  nav-indicator: "#66c9bb"
  context: "#e7edf2"
  warning-bg: "#fbf0e3"
  warning-text: "#7e450f"
  map-bg: "#f7f9fa"
  ramp-zero: "#e4e9ed"
  ramp-low: "#f6dfc4"
  ramp-mid: "#eeb780"
  ramp-high: "#db8a46"
  tag-bg: "#e8f1f2"
  tag-text: "#33616c"
typography:
  headline:
    fontFamily: "'Microsoft YaHei','PingFang SC',sans-serif"
    fontSize: "26px"
    lineHeight: 1.4
    letterSpacing: "-0.02em"
  title:
    fontFamily: "'Microsoft YaHei','PingFang SC',sans-serif"
    fontSize: "18px"
    lineHeight: 1.5
  subheading:
    fontFamily: "'Microsoft YaHei','PingFang SC',sans-serif"
    fontSize: "15px"
  body:
    fontFamily: "'Microsoft YaHei','PingFang SC',sans-serif"
    fontSize: "14px"
    lineHeight: 1.65
  label:
    fontFamily: "'Microsoft YaHei','PingFang SC',sans-serif"
    fontSize: "12px"
  comparison:
    fontFamily: "'Microsoft YaHei','PingFang SC',sans-serif"
    fontSize: "31px"
    fontWeight: 600
    lineHeight: 1.3
  metric:
    fontFamily: "'Microsoft YaHei','PingFang SC',sans-serif"
    fontSize: "29px"
    fontWeight: 600
    lineHeight: 1.4
  mono:
    fontFamily: "Consolas,monospace"
    fontSize: "12px"
rounded:
  tag: "4px"
  control: "6px"
  context: "8px"
  panel: "12px"
spacing:
  step-4: "4px"
  step-8: "8px"
  step-10: "10px"
  step-12: "12px"
  step-14: "14px"
  step-16: "16px"
  step-18: "18px"
  step-20: "20px"
  step-22: "22px"
  step-24: "24px"
  step-28: "28px"
  step-32: "32px"
  step-36: "36px"
  step-40: "40px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-link:
    backgroundColor: "transparent"
    textColor: "{colors.accent}"
    padding: "2px 0"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  navigation-active:
    backgroundColor: "{colors.nav-active}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "12px 14px"
  tag:
    backgroundColor: "{colors.tag-bg}"
    textColor: "{colors.tag-text}"
    rounded: "{rounded.tag}"
    padding: "2px 7px"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
  level:
    backgroundColor: "#f5f7f9"
    rounded: "{rounded.tag}"
    padding: "10px 12px"
---
# Design System: 仓储拣选设计实验室

## Overview

**Creative North Star: "可查证的仓储研究工作台"**

以深蓝导航、冷灰工作画布和白色数据面板承载中文研究操作。密度服务于地图定位、事件核对和方案比较；视觉状态与文字说明一起表达选择、缺失和适用边界。

这是从已实现代码提取的系统，延续本次任务书与会话已确定的方向。视觉权威为代码（Operate，code-led），没有批准的视觉稿；五个既定页面共享导航、情景选择、表格和证据抽屉。此文将本次新建的临时规范收束为实际使用的规则。

**Key Characteristics:**
- 地图为工作主区，货架单元下钻四层，再进入具体事件证据。
- 前后地图同尺度、同色标，以同一 SKU 对应源目标，并以 lift_key 核对事件。
- 中文原生控件、等宽数字与明确空值语义支撑可核对阅读。

## Colors

2026-11-01 精修延续既有配色；禁止紫色。访问过的链接也显式沿用青绿，浏览器默认访问色不能进入页面。未覆盖在灰色填充上加斜线，与零计数及空位区别，斜线仅用于地图数据缺失语义。

青绿表示操作与选择，橙棕表示需关注的量值，深蓝与冷灰承担结构；调色板以 frontmatter 为规范值，来源为 `frontend/style.css` 与 `frontend/app.js`。

### Primary
- **调查青绿**（accent）：按钮、链接、所选库位、移动 SKU 描边和路线。
- **关注橙棕**（orange）：指标色阶高端及需关注的候选；不代表伤病概率。

### Neutral
- **结构深蓝**（nav）：固定导航背景与交接点。
- **正文墨蓝 / 辅助蓝灰**（ink / muted）：正文与次要说明。
- **冷灰画布 / 白色表面 / 分隔灰**（ground / surface / line）：页面、面板、边界。
- **未覆盖灰**（unknown）：无可评估数据，与白底虚线空位分开。
- **筛查色阶**（ramp-zero → ramp-low → ramp-mid → ramp-high → orange）：代码中的五级连续量分箱；当前指标及归一化上限显示在图例中。

**The Shared Evidence Rule.** 前后地图必须共用指标与色标，选择态与移动态用描边表达，不替代数值填色。

## Typography

**Display Font / Body Font:** Microsoft YaHei、PingFang SC、sans-serif，中文无外部字体依赖。
**Label/Mono Font:** 来源标识使用 Consolas、monospace；普通辅助标签沿用正文族。

字体层级以 frontmatter 为准。页面标题为 headline；面板标题为 title；立面分组为 subheading；正文为 body；单位、图例、表格和来源提示为 label；统计摘要为 metric。没有额外展示字体。表格字号为辅助层级；状态标签另用（11px）。方法正文行高（1.9），证据片段（13px / 1.8）。标题字重沿用 HTML 标题语义，未另造全局字重 token。

**The Numeric Reading Rule.** 正文启用 tabular-nums；来源 ID 与 lift_key 使用独立等宽样式，长 ID 可换行。

## Layout

2026-11-01：助手入口并入标题行；比较主结果（31px）与基线/差值分层，双地图面板内边距缩到（12px）、间距（18px）。顶部上下文收为（12px 16px），保持分母和近似回放限制可见。证据与助手侧层在桌面距视口（8px），移动端覆盖可用布局宽度而非含滚动条的100vw。

桌面以固定左导航（208px）、顶部上下文栏（62px）和自适应工作区构成。主区上限（1840px），常态内边距（28px 32px 36px）。共享情景条可换行，调查区为（1.7fr / minmax(300px,1fr)），双地图为两个等宽可收缩列；一般网格间距（22px），节间距（24px）。间距来自实际选择器，不宣称单一等比栅格。

大屏断点（min-width:1700px）扩展导航至（224px）、主区边距至（32px 40px）并放大地图最大高度。收窄断点（max-width:1300px）将导航收为（176px）。在（max-width:1000px）导航置顶并横向滚动，调查和双地图转单列，四项统计转两列。在（max-width:600px）主区边距为（18px 12px），比较指标与三列区域转单列，情景字段逐行。

地图基于真实几何 SVG（viewBox 0 0 700 445），宽度自适应，通常最大高度（425px），大屏（520px）。表格容器内部滚动，最大高度（460px）；表头粘顶。单元格上下内边距（11px），不将实际行高假定为固定 44px。概览导语与方案摘要使用样式表末尾的紧凑覆盖，保持地图较早进入工作视口。

## Elevation & Depth

普通面板通过白色表面、细边框与浅色状态形成层次，没有卡片投影。侧边原生 dialog 使用侧向阴影（见 sidecar），深蓝透明遮罩聚焦证据；其宽度（min(780px,96vw)），桌面高度（100dvh - 16px），移动端高度（100dvh），标题行粘顶。选中导航的内侧细线属于状态指示，不是悬浮阴影。

**The Evidence Drawer Rule.** 主工作面板保持平面层级；侧边证据对话框使用遮罩与侧向阴影区分当前阅读上下文。

## Shapes

面板与统计组使用 panel 圆角，情景条与配对证据容器使用 context 圆角，控件和提示使用 control 圆角，标签和层级按钮使用 tag 圆角。边界普遍为（1px）细实线；空位用虚线。地图货架单元矩形为（16 × 20）SVG 单位、圆角（2），中心坐标保持真实几何映射，选择与移动采用加粗青绿描边。

## Components

### Buttons
原生控件保留明确可操作形态。主操作用青绿底白字；普通按钮白底细边框；链接按钮透明底并下划线。控件最小高度（38px），链接按钮最小高度（28px）。主按钮悬停变深，普通按钮悬停浅青绿；禁用透明度（.48）与不可用光标。所有可键盘交互对象共享可见焦点轮廓（3px solid focus，偏移 3px）。控件边框与底色使用（150ms）短过渡，无位移动画；减少动态偏好下关闭过渡。

### Chips
紧凑标签采用 tag 的文字、底色和圆角。关注变体用暖浅底，灰色变体用于候选或中性状态；文本本身必须交代状态。

### Cards / Containers
面板白底、细边框、无阴影、溢出裁切。标题区内边距（18px 22px 10px），内容区（16px 22px 22px）；方案摘要与窄屏有代码中明确覆盖。浅色提示条与正文配合，不替代数值或来源说明。

### Inputs / Fields
input 与 select 共用白底边框和 control 圆角；输入框允许收缩。焦点改变边框并保留全局焦点轮廓。字段标签为中文辅助字号，label 与控件关联；精确库位输入提供地图以外的入口。

### Navigation
桌面左侧五个页面：项目总览、仓库调查、风险与证据、方案实验、方法与记录。导航按钮左对齐，当前页用浅深蓝底、白字和左内嵌青绿线，以 aria-current 标记。图标为内联描边 SVG，移动断点隐藏；品牌为仓储线框标记。说明行保留真实产品信息，不作为装饰性眉题扩展。

### Warehouse / Evidence Signature

2026-11-01：每张选中地图显示当前SKU/库位；切换时替换本地定位提示，不添加网络请求。证据抽屉以FILI、FIRWL和实际载荷作为摘要；null保持未评估，身份字段与计算参数分开。章节导航可在同一抽屉跳转到计算与来源，不隐藏正式LI和方法边界。

上下文证据助手沿用当前检索/生成能力、授权、预算与原请求载荷。范围区、模型/索引状态、输入、结果与引用分层；状态可用是工具就绪信息，不是风险安全结论。未配置、证据不足、取消和错误继续使用明确文字；不以演示文本填充回答。侧层非模态，保留关闭、Escape和焦点返回。
地图方格表示一侧货架单元的四层汇总，点击后在立面按降序查看四层和具体库位；再从事件表进入原生证据对话框。选中层用青绿边框和浅青底。无商品分配、没有匹配事件和无可评估数据分别写明。风险与证据页沿用事件表、筛选和证据片段，方法页使用同一面板与可折叠完整记录。

方案页的前后地图共享几何尺度及计算后的共同色标。移动 SKU 用青绿描边，清单选中行浅青高亮，同 SKU 的源目标位置同步选中；配对容器显示 lift_key、来源事件和两列参数。路线逐边示意使用青绿路径与橙色下一边，页面文字限定其含义。prefers-reduced-motion 已禁用通用动画与过渡，但不得据此宣称路线定时播放已经自动停止。

## Do's and Don'ts

### Do:
- **Do** 保留地图、四层立面和事件证据之间的可追踪选择关系。
- **Do** 在同一 SKU 的前后地图中保留共同色标，并在配对详情中显示 lift_key。
- **Do** 保持可见键盘焦点、中文标签、颜色加文字，以及库位输入和表格替代入口。
- **Do** 让表格在自身容器内滚动，让布局列允许收缩。
- **Do** 分别显示未评估、无可评估数据、空位、加载、错误和无组合。

### Don't:
- **Don't** 用灰色未覆盖记录表示低风险，也不要把零值标为健康安全。
- **Don't** 用色彩或动画暗示正式 LI、吞吐或积压改善已得到验证。
- **Don't** 让前后地图独立归一化色标或以不同 SKU 拼成改善对照。
- **Don't** 将逐边路线播放解释为经过物理验证的时间模拟。

未规范化的缺陷或偏差：未发现需要把装饰性眉题、硬偏移阴影或字形图标收编为规则的依据；路线定时播放与减少动态偏好的联动未从样式源得到证明，不作已解决承诺。本次仅记录已交付样式，不修改实现或上游。
