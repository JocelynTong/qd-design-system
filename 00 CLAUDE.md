# 千岛设计系统 · AI 使用说明

> 本文件供 AI（如 Claude）自动读取。当产品经理或设计师向你描述界面需求时，请严格按照本文件中的规范输出设计方案。

设计系统浏览器：https://jocelyntong.github.io/echo-design-system/
组件文档目录：`02 components/` 目录下每个 JSON 文件

---

## 00 · 全局页面尺寸与 iOS 安全区

**设计基准：iPhone 375×812（1x）**，对应 iPhone X/11/12/13 mini 等主流机型。

```
┌─────────────────────────┐  ↑
│     Status Bar 44px     │  │ 顶部安全区（iOS 状态栏）
├─────────────────────────┤  │
│                         │  │
│      内容区              │  812px
│                         │  │
├─────────────────────────┤  │
│   Home Indicator 34px   │  │ 底部安全区（iOS 手势条）
└─────────────────────────┘  ↓
         375px
```

| 区域 | 高度 | 说明 |
|------|------|------|
| Status Bar | 44px | 顶部，使用 `💙 01.00_Status Bar` 组件；透明时 opacity=0 |
| Home Indicator | 34px | 底部，使用 `💙 01.11_Home Indicator` 组件 |
| 纯内容区 | 734px | 812 - 44 - 34 |

**注意：** TabBar（83px）和 BottomBar/ActionBar（83px）内部已包含 Home Indicator 的 34px 安全区，不需要额外叠加。独立页面（无 TabBar/BottomBar）才需要单独放置 Home Indicator 组件。

---

## 01 · Token 三级映射规范

### 层级原理

颜色**只能**使用 L2 或 L3 token，**禁止**直接写 HEX 值。

```
L1 Primitives（原始值）
  └─ primarypurple_05 = #7C66FF
        ↓
L2 Tokens（语义层）
  ├─ 色阶层：primary/5 → primarypurple_05
  └─ 角色层：primary/solidBg → primary/5
        ↓
L3 Tokens（组件层）
  └─ primary/bt/solidBg → primary/solidBg
```

### Token 铁律

- 所有颜色、间距、圆角必须使用 CSS `var()` token
- 禁止裸 hex / rgba() / px 颜色值直接写入 HTML
- 需要新值时：先在 `01 tokens/_styles.css` 加 token，再用 `var()`

### 常用 L2 颜色 Token 速查

| Token | 用途 |
|-------|------|
| `primary/solidBg` | 主色实底背景 |
| `primary/softBg` | 主色淡底背景 |
| `primary/color` | 主色文字/图标 |
| `text/1` | 主要文字颜色 |
| `text/2` | 次要文字颜色 |
| `text/disabled` | 禁用文字颜色 |
| `icon/1` | 主要图标颜色 |
| `icon/2` | 次要图标颜色 |
| `bg/1` | 页面/卡片背景 |
| `border/1` | 常规描边颜色 |
| `success/solidBg` | 成功色背景 |
| `warning/solidBg` | 警告色背景 |
| `error/solidBg` | 错误色背景 |

### 间距 Token

| Token | 像素值 |
|-------|--------|
| `Spacing/Large` | 16px |
| `Spacing/Medium` | 12px |
| `Spacing/Normal` | 8px |
| `Spacing/Small` | 4px |
| `Spacing/Mini` | 2px |

### 圆角 Token

| Token | 像素值 |
|-------|--------|
| `Radius/Large` | 16px |
| `Radius/Medium` | 12px |
| `Radius/Normal` | 8px |
| `Radius/Small` | 4px |
| `Radius/Mini` | 2px |

### 文字规范（Typography）

详见 `02 components/typography.json`。设计稿基准：375×667px 一倍图。

| Token | 字号 | 字重 | 行高 | 字体 | 典型用途 |
|-------|------|------|------|------|---------|
| `H1` | 24px | 500 | 30px | PingFang SC | 页面大标题 |
| `H2` | 20px | 500 | 26px | PingFang SC | 区块标题 |
| `H3` | 18px | 500 | 25px | PingFang SC | 卡片主标题 |
| `H4` | 16px | 500 | 24px | PingFang SC | NavBar 标题、列表标题 |
| `H5` | 14px | 500 | 22px | PingFang SC | 按钮文字、正文加粗 |
| `H6` | 12px | 500 | 18px | PingFang SC | Tab 文字、辅助标签 |
| `H7` | 11px | 500 | 13px | PingFang SC | 角标文字 |
| `B4` | 16px | 400 | 24px | PingFang SC | 正文标准 |
| `B5` | 14px | 400 | 22px | PingFang SC | 常规正文（feed 标题、评论）|
| `B6` | 12px | 400 | 18px | PingFang SC | 辅助正文、描述 |
| `N5` | 14px | 500 | 22px | **Roboto** | 数字、英文内容 |
| `N6` | 12px | 500 | 18px | **Roboto** | 点赞数、评论数、角标数字 |

**规则**：中文用 H/B 系列（PingFang SC），数字/价格/统计数据用 N 系列（Roboto）。

### 图标规范（Icons）

详见 `02 components/icons.json`。

- **字体库**：`KurilIcons`（iconfont 项目 3550031）
- **CSS 引入**：`<link rel="stylesheet" href="//at.alicdn.com/t/c/font_3550031_uwcy4h4l9a9.css">`
- **使用方式**：`<i class="KurilIcons kuril-{name}"></i>`
- **颜色**：继承父元素 color，配合 `icon/1`、`icon/2` token

| 场景 | 图标名 |
|------|-------|
| 返回 | `kuril-arrow_left` |
| 搜索 | `kuril-search` |
| 点赞 | `kuril-like_normal` / `kuril-like_selected_filled` |
| 评论 | `kuril-comment` |
| 分享 | `kuril-share` |
| 关闭 | `kuril-close` |
| 更多 | `kuril-more` |
| 视频播放 | `kuril-video_play_circle_filled` |
| 购物车 | `kuril-cart` |
| 消息 | `kuril-message` |
| 设置 | `kuril-setting` |
| 关注/想要 | `kuril-have_normal` / `kuril-have_selected` |

---

## 02 · 原子分子组件规范

> 详细参数见 `02 components/` 目录下各 JSON 文件。以下为速查表。

### 组件 JSON 文件命名规范

`02 components/` 下的文件名必须与 JSON 内 `figma_page` 字段完全一致：

```
figma_page: "01.01 Navigation Bar"  →  文件名: 01.01 Navigation Bar.json
figma_page: "00.08 Button"          →  文件名: 00.08 Button.json
```

**同步组件时的强制检查步骤（缺一不可）：**

1. 写入/更新 JSON 内容
2. **对比文件名与 `figma_page` 字段** — 若不一致，立即重命名文件
3. 检查 HTML 树节点 `onclick="showCompDetail('...')"` 的 id 是否与文件名（kebab-case）一致，不一致则同步修改
4. 运行 `generate.py`

> 历史遗留无编号文件（如 `navbar.json`、`badge.json`）在下次同步时顺手对齐，不强制立即批量重命名。

### 页面骨架组件

| 组件 | Figma 名称 | 关键 Variant | 适用场景 |
|------|-----------|-------------|---------|
| Navigation Bar | `💙 01.01_Navigation Bar` | Terminal=App/小程序, Ghost=False/True | 几乎所有页面顶部 |
| Tab Bar | `💙 01.05 Tab Bar / APP / 5Tabs` | 无 Variant | App 底部一级导航 |
| Search Bar | `💙 01.04_Search Bar` | 无 Variant | 首页导航嵌入或独立搜索页 |
| Tabs | `💙 01.02_Tabs / Echo` | className=CardDefault, Amount=>3 | 内容分类切换（首页/用户主页） |
| Bottom Bar | `💙 01.07_Bottom Bar` | 无 Variant | 内容详情页底部互动区 |

### 内容展示组件

| 组件 | Figma 名称 | 关键 Variant | 适用场景 |
|------|-----------|-------------|---------|
| Feed 双列卡片 | `💙 03.07_Feed / Post` | Size=4:3/3:4, Image=True/False | 首页/发现页瀑布流 |
| Feed 单列卡片 | `💙 03.07_Feed / Post` | Size=1 Column, Image=True | 关注页/搜索结果全宽信息流 |
| Tag | `💙 03.02_Tag / Echo` | className=Tag/SPU/Post/Spec | 内容标签、商品状态、帖子角标 |
| Avatar | `💙 03.05_Avatar / Basic` | Size=Normal/Small, Color=Default | 作者头像、评论列表 |
| Avatar Echo | `💙 03.05_Avatar / Echo` | className=AvatarLive/AvatarReddot | 直播状态、未读提示 |
| Badge | `💙  03.01_Badge/Shop/Normal` | 无 Variant | Tab 角标、消息未读数 |

**Feed 布局规则：**
- 双列：卡片宽 174px，间距 8px（Spacing/Normal），页面两侧各 8px
- 单列：卡片全宽，左右各 16px（Spacing/Large）边距
- 图片圆角：Radius/Normal(8px)

### 交互输入组件

| 组件 | Figma 名称 | 关键 Variant | 适用场景 |
|------|-----------|-------------|---------|
| Input Frame | `💙 02.03_Input_Frame` | State=Default/Completed/Error, Size=Normal | 评论输入、表单填写 |
| Input Line | `💙 02.03_Input_Line` | State=Default/Completed | 嵌入表单行内 |
| Input Select | `💙 02.03_Input_Select` | State=Default/Completed | 下拉选择（城市/类别） |

### Button 按钮

| 场景 | 使用组件 | 关键参数 |
|------|---------|---------|
| 主操作（唯一 CTA） | `💙 00.08_Button` | Color=Primary, Type=Solid, Size=Large(40) |
| 次要操作 | `💙 00.08_Button` | Color=Primary, Type=Soft 或 Outline |
| 成功/警告/错误/交易色 | `💙 00.08_Button` | Color=Success/Warning/Error/Trade |
| 单品牌色 | `💙 00.05_Button / QH` | Type=Solid/Soft/Outline/Text |
| 全局浮动 | `💙 00.05_Button / FAB` | Normal=True |
| 购物车 | `💙 00.05_Button / FloatCart` | 场景=home published |
| 纯图标 | `💙 00.05_Button / Icon` | Size=Normal |

Button 尺寸：Large(40px) 主CTA · Medium(36px) 弹窗 · Normal(32px) 卡片内 · Small(28px) 紧凑区

### 反馈组件

| 组件 | Figma 名称 | 关键 Variant | 使用时机 |
|------|-----------|-------------|---------|
| Toast | `💙 04.03_Toast` | Type=Text/icon | 操作成功/失败，2秒自动消失 |
| Dialog | `💙 04.04_Dialog` | Image=-/top/middle, Button Count=1/2 | 不可逆操作二次确认 |
| Popup | `💙 04.05_Popup` | 无 Variant | 评论列表、分享面板、筛选器 |

### 暂未录入的原子分子组件

以下组件存在于 Figma 文件中，尚未整理成结构化文档，使用时需谨慎：

**Bar 系列**：Status Bar, SegmentedControl, Menu, Steps, Home Indicator

**Form 系列**：FormItem, Textarea, Radio, Checkbox, Switch, Stepper, Upload, DateTimePicker, Rate

**Feedback 系列**：NoticeBar, SnackBar, Dropdown, Popover, ShareSheet, Result Page, Skeleton

> 如需使用以上组件，请告知设计师补充录入对应 `02 components/*.json` 文件。

---

## 03 · 业务组件规范（按需加载）

> CLAUDE.md 只维护全局规范。各业务线的页面模板、组件 Key 表、变体选择指引存放在独立文件中。
> **PM 提出原型需求时，根据业务归属读取对应文件，不要把所有业务内容加载进来。**

| 业务线 | 文件 | 状态 |
|--------|------|------|
| 社区（内容详情页、首页 Feed） | `03 business/community/_module.md` | ✅ 可用 |
| C2C（二手交易、商品详情） | `03 business/c2c/_module.md` | ⚠️ 待补充 |

### 调用规则

- PM 说「社区」「内容详情」「帖子」「Feed」→ 读取 `03 business/community/_module.md`
- PM 说「C2C」「商品」「二手」→ 读取 `03 business/c2c/_module.md`
- 不确定时询问 PM 属于哪个业务线

### 10% 新创意规则

- 允许不完全使用 token 和组件的新创意设计
- 新创意元素由插件导出时自动标记，记录进 `_candidates.md`
- 收口人在每次新需求开始时做决策（见候选池决策规则）

### 候选池决策规则

| 出现频次 | 状态 | 处理时机 |
|---|---|---|
| 3 次以上 | 🔴 需要决策 | 本周处理，飞书周报提醒 |
| 1-2 次 | 🟡 观察中 | 暂不处理，继续观察 |

决策三选一：**token 化** / **业务组件** / **忽略（一次性）**

### 业务组件命名规范

**格式：** `👻 {Scene} / {Component}`

- `👻` = 业务组件标记（区别于 `02 components/` 的原子分子组件）
- `Scene`（`/` 前）= 场景/页面上下文，对应 `{scene}.scene.json`
- `Component`（`/` 后）= 可复用业务组件，对应 `{component}.json`

### 插件组件识别规则（💙 / 👻）

插件导出时递归扫描选中区域，**只认前缀，不认 Frame 结构**：

| 前缀 | 含义 | 归属层 |
|------|------|-------|
| `💙` | 系统 UIKit 原子分子组件 | `02 components/` |
| `👻` | 业务场景组件 | `03 business/` |
| 无前缀 | 包裹层 Frame / 自定义图形 | 自动跳过，不产生警告 |

**无论选中 Section、Frame、整个面板还是单个组件，插件都会递归找出其中所有 💙/👻 节点并导出，其余包裹层自动忽略。**

| Figma 图层名 | 生成文件 | 归属目录 |
|-------------|---------|---------|
| `👻 Islands / Grid` | `grid.json` + `islands.scene.json` 引用 | `03 business/community/` |
| `👻 展示侧 / Cell` | `cell.json` + `展示侧.scene.json` 引用 | `03 business/community/` |
| `👻 订单详情 / ProductCard` | `product-card.json` + `order-detail.scene.json` 引用 | `03 business/c2c/` |

**跨模块引用规则：** 组件定义权归属于首次出现的业务模块，其他模块通过 `ref` 引用，不重复定义：

```json
// 03 business/c2c/order-detail.scene.json
{
  "components": [
    { "ref": "community/post-card", "context": "recommendation-feed" }
  ]
}
```

### 新业务线创建规则

**在 `03 business/` 下新增任何业务线时，必须同时完成，缺一不可：**

1. 创建文件夹：`03 business/{module}/`
2. 创建说明文件：`03 business/{module}/_module.md`（页面模板、组件 Key 表、变体选择指引）
3. 在本节业务线表格中新增一行
4. 在 `00 README.md` 目录树中新增对应条目

### 暂未录入的业务组件

**Data 系列**：Feed（内容卡片）, Spu, Price, Empty, Swipe, Checklist, List, Grid

> 如需使用以上组件，请告知设计师补充录入对应 `03 business/{module}/_module.md` 文件。

---

## 04 · 原型工作流

### 04-A · PM 提需求 → AI 生成原型

**触发**：PM 描述界面需求

**AI 步骤：**
1. 识别业务归属，读取对应规范文件（`03 business/*.md`）
2. 规划涉及页面，从规范稿起点（`03 business/{module}/*.html`）开始
3. 运行 `node '04 demos/new-demo.js'` 初始化需求文件夹
4. 选型组件 → 确定变体 → 生成 HTML + `figma-config.json`

**原型规范约束：**
- 图片占位用实色色块（`background: var(--bg-4)`），禁止用渐变
- 所有颜色、间距、圆角使用 token，见 `01`
- iOS 安全区遵守 `00`

**输出格式：**

```
## [页面名称] 原型方案

### 页面结构
[描述页面的整体布局]

### 组件清单
| 区域 | 组件 | 变体参数 | 说明 |
|------|------|---------|------|
| 顶部 | NavigationBar | Terminal=App, Ghost=False | 页面标题 |
| 内容区 | ... | ... | ... |
| 底部 | Button/MH | Color=Primary, Type=Solid, Size=Large(40) | 主 CTA |

### Token 使用
- 背景色：bg/1
- 主文字：text/1
- ...

### Figma 操作步骤
1. 在组件库搜索组件名，拖入画布
2. 右侧面板切换 Variant 属性
3. ...
```

---

### 04-B · 设计师导出 → AI 回写规范稿

**触发**：设计师将 Figma 插件导出 JSON 粘贴给 AI

**AI 步骤：**
1. 解析导出 JSON，与 `03 business/{module}/*.html` 对比差异
2. 将变更回写规范稿
3. 非 token 自定义节点追加至 `_candidates.md`
4. 检查 Frame 命名是否与 HTML 文件名一致，不一致给出警告（见 `10` 规则 3）

**输出格式：**

```
## 回写摘要 · [Frame 名称]

### 变更内容
- [改动 1]
- [改动 2]

### 候选池新增
- [元素描述]（出现位置：[页面名]，CSS：[样式值]）

### 命名警告（如有）
- Frame「XXX」与文件名「yyy.html」不一致，请修正 Figma Frame 名称
```

---

### 04-C · 收口人决策 → AI 执行

**触发**：收口人对候选池条目做出决策

| 决策 | AI 执行 |
|------|--------|
| Token 化 | 在 `01 tokens/_styles.css` 新增 token，更新引用处 |
| 业务组件化 | 在 `03 business/{module}/` 新建 HTML 片段，更新对应 `*.md` Key 表 |
| 忽略（一次性） | 从 `_candidates.md` 移除该条目 |

**输出格式：**

```
## 执行确认 · [候选池条目名称]

决策：[token化 / 业务组件 / 忽略]

### 操作
- 修改文件：[文件路径]
- 具体改动：[说明]

### 候选池状态
- 已移除：[条目名称]
```

---

## 05 · 【预留】

---

## 06 · 【预留】

---

## 07 · 【预留】

---

## 08 · 【预留】

---

## 09 · 【预留】

---

## 10 · 项目架构规则

> 本节定义项目文件组织的核心原则，供 AI 初始化学习和维护时遵守。
> 发现潜在违反时，AI 应主动标注「涉及架构规则 X」并等待确认后再执行。

### 规则 1：脚本归属原则

**脚本必须归属于它服务的功能文件夹，不独立存在于根目录或统一的 scripts/ 文件夹。**

| 脚本 | 服务对象 | 归属位置 |
|------|---------|---------|
| `new-demo.js` | 在 `04 demos/` 下创建需求文件夹 | `04 demos/` |
| `build-demo.js` | 打包 `04 demos/` 里的 HTML | `04 demos/` |
| `figma-sync-server.js` | 读 figma-config.json 供插件使用 | `05 figma-plugin/` |
| `parse-html-to-config.js` | 解析 HTML 生成 Figma 配置 | `05 figma-plugin/` |
| `notify-feishu.js` | 读 `_candidates.md` 推飞书 | 根目录 |
| `generate.py` | 处理 `01 tokens/` 下的 JSON，未来扩展至 `02 components/`、`03 business/` | 根目录 |

反例（已废弃）：❌ `06 scripts/` 统一存放所有脚本 → 违反就近原则

### 规则 2：数字前缀排序

所有一级目录使用两位数字前缀，按依赖关系和工作流顺序排列：

```
00 CLAUDE.md / README.md    # 文档优先
01 tokens/                  # 设计 Token 源头
02 components/              # 原子分子组件规范
03 business/                # 业务规范（依赖 tokens + components）
04 demos/                   # 需求原型（依赖 business 规范）
05 figma-plugin/            # Figma 工具（服务 demos 和 business）
```

新增一级目录时，按依赖关系插入合适的数字前缀，不使用 `scripts/`、`utils/`、`tools/` 等通用名称。

### 规则 4：数据流单向自动化（三层统一）

**Figma 导出 JSON → `generate.py` 处理 → `_styles.css` 自动生成，三层全部遵循此原则，禁止反向手动编辑。**

```
Figma
  ↓ 插件导出
01 tokens/*.json        → generate.py → 01 tokens/_styles.css      （全量覆写，禁止手动编辑）
02 components/*.json    → generate.py → 02 components/_styles.css   （自动生成部分，禁止手动编辑）
03 business/**/*.json   → generate.py → 03 business/_styles.css     （自动生成部分，禁止手动编辑）
  ↓ 层级依赖
new-demo.js 拼接三层 → 04 demos/{name}/styles.css（冻结快照）
```

**各层当前状态：**

| 层级 | JSON 源 | generate.py 支持 | _styles.css 状态 |
|------|---------|-----------------|-----------------|
| `01 tokens/` | ✅ Figma 变量导出 | ✅ 已实现 | ✅ 全量覆写 |
| `02 components/` | ✅ 已有 JSON 规范 | 🚧 待实现 | 手写（暂时） |
| `03 business/` | 🚧 HTML 迁移 JSON 中 | 🚧 待实现 | 手写（暂时） |

**铁律：**
- 已自动化的层（`01 tokens/_styles.css`）**禁止手动编辑**
- 未自动化的层（`02 components/`、`03 business/`）手写样式时，写在 `_styles.css` 的**自动生成区以外**，等待 generate.py 接管后自然迁移
- CI 在对应 JSON 变更时自动运行 `generate.py` 并提交产物

### 规则 3：Frame 命名约定

- Figma Frame 名字必须与对应 HTML 文件名一致（不含 .html 后缀）
- 例：Figma Frame `home-feed` → `03 business/community/home-feed.html`
- 命名确定后不可更改；删除重建时保持同名，ID 变了不影响按名字同步
- AI 在 04-B 回写时若发现命名不一致，必须在输出中给出警告

### 规则 5：禁止随意新建文件或文件夹

> ⚠️ 写给 AI 和开发者：新建是最容易被忽视的架构侵蚀方式。每新增一个文件或文件夹，都会增加维护成本、打破已有的归属逻辑。

**执行铁律：**

1. **先找现有位置，再考虑新建。** 动手前必须确认：现有目录结构里是否已有合适的归属位置？
2. **新建文件前必须通知负责人。** AI 执行任何新建操作前，须在输出中明确标注：
   > 「即将新建：`{路径}`，原因：{理由}，请确认后继续」
3. **新建文件夹的门槛更高。** 新建文件夹意味着新的职责边界，必须同时：
   - 说明它服务哪个层级（tokens / components / business / demos / plugin）
   - 更新 `00 CLAUDE.md` 目录表和 `00 README.md` 目录树
4. **禁止用新建解决可以用现有文件扩展解决的问题。** 例：
   - ❌ 新建 `05 figma-plugin/schemas/` 存放 JSON Schema → 应写入 `00 CLAUDE.md`
   - ❌ 新建 `06 scripts/` 存放工具脚本 → 应归属到对应功能目录
   - ❌ 新建 `utils.js` 存放共用函数 → 应内联到调用方或加入已有脚本
