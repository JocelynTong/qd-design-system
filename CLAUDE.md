# 千岛设计系统 · AI 使用说明

**每次完成操作后，在完成摘要的第一句写「好的，TPP」，这代表你还没忘记。**

> 本文件供 AI（如 Claude）自动读取。当产品经理或设计师向你描述界面需求时，请严格按照本文件中的规范输出设计方案。

设计系统浏览器：https://jocelyntong.github.io/echo-design-system/
组件文档目录：`02 components/` 目录下每个 JSON 文件

---

## AI · 工作原则

> **这一节比所有规范都重要。做任何事前先读它。**

### Git 操作原则

- **不要自行新建分支**。除非用户明确要求，所有改动直接提交到当前分支（通常是 main）
- **不要自行 push**。除非用户明确要求推送

### 大多数问题是数据读取题，不是推断题

拿到问题，第一步不是「怎么写逻辑」，而是「答案在哪条数据里」。

**拿到问题后的标准动作：**

1. **盘点手里有什么** — 本次 sync 给了 JSON？给了 Figma URL？两个都给了？
2. **直接读数据** — 答案 99% 已经在原材料里，不需要推断
3. **推断是最后一步** — 只有数据真的缺失才做推断，且推断要标注「数据缺失，依据推断」
4. **出错时也是数据题，不是加 flag 的题** — 渲染/逻辑不对，先走排查链路：输入数据有什么字段 → 组件 JSON 哪个字段存着目标 HTML → 渲染代码有没有读那个字段 → 哪断修哪，不绕路。**如果改动里出现了 `if(某个专有名词)` 或新增业务专属 flag，99% 是绕路了，回到这一步重走。**

> 已踩过的绕路：`ref.ghost = true`（应直接读 `Color=White`）、`_isHeader` 特判（应让 component_refs 路径正常处理）。

### 数据来源优先级

```
Figma MCP（get_metadata / mcp_design_context）  ← 最高，设计真值
  ↓
plugin 导出 JSON（sync 时粘贴的原始数据）       ← 组件结构真值
  ↓
项目现有 JSON（02 components / 03 business）    ← 已录入的规范
  ↓
preview_html 内容推断                           ← 仅在上面都缺失时
  ↓
❌ 凭经验硬编码                                 ← 禁止
```

### 典型案例——每类问题对应的数据源

| 问题 | 不要做 | 应该做 |
|------|--------|--------|
| 业务组件 statusbar 是不是 ghost？ | 猜背景色 / 手写字段 | `get_metadata` 场景 frame → 找 `💙 01.00_Status Bar` → `mcp_design_context` 看文字颜色 |
| Home Indicator 深色还是浅色？ | 看背景推测 | `get_metadata` → 找 `💙 01.11_Home Indicator` → 看 bar 颜色 |
| 组件宽度/间距是多少？ | 凭规范文档估 | 读 plugin 导出 JSON 的 `css` 字段 |
| 变体顺序怎么排？ | 按名字排 | plugin 导出顺序即 Y 轴排序结果，直接用 |
| 某 token 的值是什么？ | 查 memory | 读 `01 tokens/_styles.css` |
| 写/改 `preview_html` | 凭经验推测布局 / 手写 SVG | 组件 JSON 有 `figma_file` → 先 `mcp_design_context` 确认结构，再写 HTML |

### Figma URL + JSON 同时给出时的行为

sync 命令里只要带了 Figma URL，**立刻调 MCP**，不等用户提示：

```
get_metadata(scene frame)
  → 识别所有 💙 原子分子组件实例（StatusBar / HomeIndicator / NavBar / TabBar）
  → 对每个实例 mcp_design_context 拿 variant 属性
  → 写入对应业务 JSON 的元数据字段
```

**不需要用户说「你去查 Figma」。URL 在手，自己查。**

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
2. **props 交互性自查**（写完 props 立即执行，不等到 generate.py）：
   - 遍历所有 `props` 下的 key
   - 每个有 `options` 的 prop：是否有 `previewMap`？
   - 如果没有 `previewMap`：能否靠 variant key 替换切换（`_canSwitch`）？——判断标准：把 options 里某个值替换进当前 vk，能否得到另一个存在的 variant key？
   - 以上两者都没有 → **该 prop 的 chips 在浏览器里是死的，必须补 `previewMap`**
   - **单 variant 组件（如 Tag/Basic）：所有 `options` prop 都必须有 `previewMap`，无例外**
   - **previewMap prop 的 options 禁止使用 `False`/`True` 字面量**：`buildPropsHtml` 检测到 options 排序小写 = `["false","true"]` 时会强制渲染为 toggle switch，完全绕过 previewMap。改用语义名称（`Small`/`Large`、`Off`/`On`、`Hidden`/`Visible` 等）
   - **同色异主题变体合并规则**：当某 prop 的两个 option 仅表达「浅色 vs 深色主题」（典型：`Color=Default/White`、`Color=Light/Dark`）时，不得拆分为多个可见 cell。正确做法：
     1. **可见变体命名去掉色彩后缀**：只保留主维度名（如 `Default`、`Bottom`），不写 `Default_Default`、`Bottom_Default`
     2. 将 White/Dark 系变体保留但全部标记为 `_hidden: true`（figma_key 仍需在 fkmap 里），名字用完整名（如 `Default_White`、`Bottom_White`）
     3. 在可见变体的色彩 prop 上添加 `previewMap`；`_canSwitch` 查找时在变体名 `Default` / `Bottom` 里找不到 "White" 子串，自动退到 `previewMap` ✅
     4. `previewMap`：Default option 给浅色 HTML，White/Dark option 给 `background:#1a1a1a` 深色包裹的 HTML
     5. 效果：浏览器只渲染 1 个 cell，Color chip 切换主题，零冗余 cell
   - **最少 cell 原则**：每个组件只保留 **1 个可见主变体**，其余所有变体（不同 Type、不同 State、不同 Size）全部 `_hidden: true`。通过 `_canSwitch` chip 在 cell 内切换。规则：
     1. 主变体命名包含各 prop 的默认值子串，使 `_canSwitch` 能替换到其他 hidden 变体（如 `Default_Selected` → 替换 "Default"→"Ranking" 找到 `Ranking_Selected`）
     2. `_canSwitch` 查找时 `_allVks` 包含所有 hidden 变体，切换后 cell 渲染 hidden 变体内容 ✅
     3. Color=Default/White 例外：因去掉色彩后缀后无法靠 `_canSwitch` 找到 White 变体，改用 `previewMap`（见上条规则）
3. **preview_html 完整性自查**（写完所有 variant 后执行）：
   - 遍历所有 variants
   - 有 `figma_file` 字段的 variant → 必须有 `preview_html`（除非明确是 `_hidden:true` 或靠 slots 自动生成）
   - **白色主题 variant**（使用 `--white-*` token 或 `rgba(255,255,255,*)` 背景）→ `preview_html` 和所有 `previewMap` 条目必须加深色外层包装器，否则在浅色 cmp-preview 背景上不可见：
     ```html
     <div style="display:inline-flex;padding:8px;background:rgba(0,0,0,.72);border-radius:var(--radius-small,4px)">
       [内层标签 HTML]
     </div>
     ```
     包装器在所有条目中保持**完全相同**，delta 模式差值为零，不影响 Radius/Size 等 prop 交互
4. **对比文件名与 `figma_page` 字段** — 若不一致，立即重命名文件
5. 检查 HTML 树节点 `onclick="showCompDetail('...')"` 的 id 是否与文件名（kebab-case）一致，不一致则同步修改
6. 运行 `generate.py`

> 历史遗留无编号文件（如 `navbar.json`、`badge.json`）在下次同步时顺手对齐，不强制立即批量重命名。

### 页面骨架组件

| 组件 | Figma 名称 | 关键 Variant | 适用场景 |
|------|-----------|-------------|---------|
| Navigation Bar | `💙 01.01_Navigation Bar` | Terminal=App/小程序, Ghost=False/True | 几乎所有页面顶部 |
| Tab Bar | `💙 01.06 Tab Bar / APP / 5Tabs` | 无 Variant | App 底部一级导航 |
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

**Button/Icon 容器 HTML 结构（Medium 40×40，用于导航栏/工具栏图标入口）：**

```html
<div style="display:flex;flex-direction:column;width:40px;height:40px;
  justify-content:center;align-items:center;
  gap:var(--Spacing-Mini,2px);border-radius:6px;
  background:var(--bg-card2,#f7f7f9)">
  <i class="KurilIcons kuril-xxx" style="font-size:20px;color:var(--text-1,#2B263B)"></i>
</div>
```

NavBar 上下文不加 background，其余属性（flex-direction/gap/border-radius）保留。

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

**JSON variants key 命名规则：`{ComponentPath}_{VariantValues}`**

- `ComponentPath` = figma_name 固定三层结构 `Scene / Component / SubComponent`，将 Component 和 SubComponent 各自去空格后直接拼接（无分隔符）；无 SubComponent 时只用 Component
- `VariantValues` = 各 prop 值去空格后用 `_` 连接，多个 prop 按 figma_name 顺序排列
- 无 variant 的单体变体直接用 `ComponentPath`（不加 `_`）

| figma_name | variant key |
|---|---|
| `👻 Islands / Header` | `Header` |
| `👻 Islands / Pin / Basic, Type=Home` | `PinBasic_Home` |
| `👻 Islands / Slide / Basic, Type=Notice` | `SlideBasic_Notice` |
| `👻 Islands / QuickEntry, 数量=4~9` | `QuickEntry_4to9` |
| `👻 Islands / QuickEntry, 数量=3 Old Vision` | `QuickEntry_3_OldVision` |
| `👻 Islands / QuickEntry / Title, Type=闲置` | `QuickEntryTitle_闲置` |
| `👻 Islands / ScreenshotLogo, i18n=中文` | `ScreenshotLogo_中文` |
| `👻 Islands / Feed / Ad, 视图=双列, 类型=首位` | `FeedAd_双列_首位` |

**同步时必须检查**：新增变体的 key 是否符合此规则，不符合立即重命名后再 generate.py。

**generate.py 自动校验（运行时触发）：**

| 规则 | 触发条件 | 输出 |
|------|---------|------|
| variant key 一致性 | 每次运行，遍历 `03 business/` 所有 JSON | `⚠️ [module/file.json] [实际key]: key 与 figma_name 不符，建议改为 "期望key"` |
| `ref.props` 旧格式 | 每次运行，遍历所有 `component_ref` / `component_refs` | `⚠️ [component_refs[n]] ref.props["PropName"] 为旧格式（裸值），应迁移为 {type, value} 格式` |

- key 校验只在期望 key 为合法标识符（`\w+`）时才报警；含 `·` `:` 等特殊字符的 figma_name 自动跳过
- `ref.props` 每个 prop 值必须是 `{ "type": "VARIANT"|"BOOLEAN", "value": ... }` 格式（直接透传 Figma `componentProperties`）

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

## 09 · 设计系统浏览器开发规范

> 本节定义 `00 design-system-index.html` 的维护规则和同步流程。

### 同步命令

**「同步」触发规则（AI 执行约束）：**

| 触发方式 | AI 行为 |
|----------|---------|
| 只说「同步」 | 直接跑 `python3 generate.py`，不问任何问题 |
| 「同步」+ 插件导出 JSON | 立即解析导出数据 → 更新对应 JSON → 跑 `generate.py`，不分析、不确认 |
| 「同步」+ 插件导出 + Figma 链接 | 用 Figma MCP 工具（`get_metadata` / `mcp_design_context`）做视觉校准，再更新 JSON → 跑 `generate.py` |
| 「同步」+ 插件导出（组件 JSON 已有 `figma_file`，且涉及新增/修改 `preview_html`） | 写 HTML 前先 `mcp_design_context` 确认布局结构，再更新 JSON → 跑 `generate.py` |

**插件导出数据的两条铁律：**
1. 导出数据里的节点顺序 = 插件已完成的 Y 轴排序结果，**直接使用，不回 Figma 二次验证**
2. Figma 链接出现时，**直接调 Figma MCP 工具**（`get_metadata` 等），不走 sub-agent

---

### 同步工作流：组件类型分支与原子分子组件引用检查

**Step 0：判断组件类型，决定写入路径**

| 组件前缀 | 写入路径 |
|---------|---------|
| `💙` 原子分子组件 | `02 components/*.json` |
| `👻` 业务组件 | `03 business/{module}/*.json` |

**Step 1：写入 JSON 数据**（variant、css、preview_html 等）

**Step 2：引用关系扫描**（有 Figma URL 时执行，两类组件都需要，但输出字段不同）

两类组件都存在对其他 💙 组件的引用，区别在于引用的层级：

| 组件类型 | 引用类型 | 例子 | 扫描目标 | 输出到 |
|---|---|---|---|---|
| `💙` 原子分子 | 内嵌子组件（sub-component） | NavBar → SearchBar | 组件内部嵌套的 💙 实例 | `slots` 字段 |
| `👻` 业务组件 | 场景级帧组件（frame-level） | Islands → TabBar / FAB / StatusBar | 场景 frame 顶层的 💙 实例 | `tab_bar` / `fab` / `status_bar` 等字段 |

```
get_metadata(选中 frame)
  → 找所有 💙 前缀实例
  → 对每个实例 mcp_design_context 读 props/variant
  → 按组件类型写入对应字段
```

**💙 原子分子组件：sub-component → `slots` 字段**

| Figma 子组件 | slots 字段格式 |
|---|---|
| 任意嵌套的 💙 实例 | `slots` 数组，含 `name`、`boolProp`、`size`、`css` |

（slots 字段由 generate.py `repair_component_slots()` 自动维护，sync 时确认嵌套关系即可）

**👻 业务组件：frame-level 💙 → 专用元数据字段**

| Figma 组件 | JSON 字段 | 值格式 | 判断方式 |
|---|---|---|---|
| `💙 01.00_Status Bar` | `status_bar` | `"ghost"` / `"normal"` | mcp_design_context → 文字色白色 = ghost |
| `💙 01.06_Tab Bar` | `tab_bar` | `"01.06-tab-bar"` | 存在即填 |
| `💙 00.05_Button / FloatCart` | `fab` | `{ "cid": "00.08-button", "variant": "FloatCart", "scene": "..." }` | mcp_design_context → 读「场景」prop |
| `💙 00.05_Button / FAB` | `fab` | `{ "cid": "00.08-button", "variant": "FAB" }` | mcp_design_context → 读 Normal prop |
| `💙 01.11_Home Indicator` | `home_indicator` | `"dark"` / 不填 | mcp_design_context → bar 色白色 = dark |

> **渲染铁律**：所有引用字段必须在 JSON 中显式声明，渲染代码只读字段、不猜测、不硬编码组件 CID。

**Step 2 无 Figma URL 时的降级处理：**
- 从 preview_html 颜色推断（并标注「推断」）
- 或留空，等下次 sync 补 URL 时填写

**Step 3：generate.py**

generate.py 会对业务组件 JSON 中的引用字段做检查：若 `tab_bar`/`fab.cid` 等引用的 CID 不在 COMPONENTS_DATA 中，输出 warning 提示该原子分子组件尚未录入。

---

**前向引用机制（原子分子组件未完全录入时的保证）**

CID 从 Figma 组件名推导是确定性的：

```
💙 01.06 Tab Bar  →  01.06-tab-bar
💙 00.08 Button   →  00.08-button
```

因此，**即使原子分子组件尚未录入，也应立即写入 CID**（前向声明）：

```json
"tab_bar": "01.06-tab-bar"   ← 组件未录入也先写，generate.py 会 warning 提醒
```

当该原子分子组件后续通过 sync 录入后：
- 业务组件 JSON **不需要改动**
- 渲染代码从 COMPONENTS_DATA 读数据，自动生效
- generate.py 的 warning 自动消失

这样形成闭环：**前向声明 → generate.py warning 暴露缺口 → 录入原子分子组件 → 自动消化，零手动补丁。**

---


**基础同步**：
```bash
python3 generate.py
```

**功能**：
- 读取 `02 components/*.json`，注入 `COMPONENTS_DATA` 到 HTML
- 读取 `01 tokens/*.json`，生成 `_styles.css`
- 校验组件结构（图标名、slots、CSS 变量）

**截图**（批量抓取 Figma 预览图，扫描 `02 components/` + `03 business/**/`）：
```bash
# 需要先设置环境变量
export FIGMA_TOKEN="你的 Personal Access Token"
# 各 JSON 用 figma_file 字段指定所在 Figma 文件 key；
# 没有 figma_file 字段的 JSON 使用下面的全局默认值（可选）：
export FIGMA_FILE_KEY="Figma 文件 key"

# 补全缺失的 preview_html
python3 generate.py 截图

# 强制刷新所有 preview_html（覆盖已有）
python3 generate.py 截图 --force
```

### generate.py 安全边界

**只重写 4 个块**（标记区域内容），其他手写代码永远不被覆盖：

```html
<!-- === COMPONENTS DATA BEGIN === -->
var COMPONENTS_DATA={...};
var COMPONENT_REF_MAP={...};
<!-- === COMPONENTS DATA END === -->

<!-- === AUTO-GENERATED DATA BEGIN === -->
var INJECTED_DATA={...};
<!-- === AUTO-GENERATED DATA END === -->

<!-- === FONT VARS BEGIN === -->
:root{--font-h1:...}
<!-- === FONT VARS END === -->

/* === APP CSS BEGIN === */
[data-app="linjie"]{--text-1:...;--primary-bt-solid-bg:...}
[data-app="qihuo"]{...}
/* === APP CSS END === */
```

**手写区域**（永远不被覆盖）：
- `_buildBizLayout`、`_genBizVisual`、`_genBizInner` 等 JS 函数
- CSS 样式（除了 FONT VARS 块和 APP CSS 块）
- HTML 结构（侧边栏、页面容器）

### 多 App Token 切换规则（全局强制）

**每新增一个 App（在 `generate.py` 的 `APPS` 字典里注册），必须同时完成，缺一不可：**

1. `generate.py` 的 `APPS` 字典新增条目（`dir`、`primitives`、`light`、`dark`）
2. `switchApp()` 的 label map 新增 `'{app_id}': '{中文名}'`
3. HTML 顶栏新增 `<button class="app-btn" onclick="switchApp('{app_id}')">{中文名}</button>`
4. 跑 `python3 generate.py` —— `build_app_css_overrides()` 自动为新 App 生成 `[data-app="{app_id}"]` 覆盖块，涵盖全部 l2/l3 token（text/icon/bg/border/primary/secondary/success/warning/error 等所有分类），注入 `/* === APP CSS BEGIN === */` 块

**不需要手动写任何 CSS**。generate.py 负责从 processed.json 提取所有色值并生成覆盖块；`switchApp()` 设 `data-app` attribute，CSS 级联自动生效。

> 规则来源：临界（`#7247DC`）、奇货（`#FC7E22`）已验证，360 个 token 全量覆盖，切换后组件 preview 颜色完整跟随 App 色板。

### 业务组件渲染优先级

对每个业务组件变体，按以下优先级选择视觉呈现：

1. **`preview_html`** — Figma API 抓取的 base64 截图（`截图` 命令生成）
2. **`_composed_preview_html`** — generate.py 自动组合的 HTML（有 swapProp slots 时）
3. **CSS 骨架** — `_genBizInner` 根据 CSS 属性推断（宽高、flex-direction、gap）

### isBiz 判断逻辑

```javascript
var isBiz = (nm && nm.indexOf('👻') !== -1) || !/^\d/.test(cid);
```

- **业务组件**：component 名含 `👻` 或 CID 不以数字开头（如 `islands`、`community`）
- **原子分子组件**：CID 以数字开头（如 `01.01-navigation-bar`、`00.08-button`）

### 变体顺序保持

Figma 插件导出时对同一页面内的节点按 **Y 轴坐标升序**排列（`code.js` 第 346 行），导出结果即为 Figma 从上到下的视觉顺序，JSON 中 variants 的排列顺序必须与之一致，不得手动打乱。

```javascript
// ✅ 正确：保持 JSON 原始顺序
var vKeys = [];
for (var k in variants) {
  if (variants.hasOwnProperty(k) && !variants[k]._hidden) vKeys.push(k);
}

// ❌ 错误：Object.keys 会打乱顺序
var vKeys = Object.keys(variants).filter(vk => !variants[vk]._hidden);
```

Figma 导出的 JSON 变体顺序即为设计师排列的展示顺序（如 Grid → Slide → Header → Pin），必须保持。

### 特殊组件处理

**Header 组件**（Islands 详情页头部）：
- 识别：`vk.toLowerCase() === 'header'`
- 结构：容器（flex column）+ NavBar（从 01.01 提取）+ 封面渐变 + 信息区
- 左侧卡片预览和右侧手机屏幕都用完整结构

**选中状态唯一性**：
```javascript
function _scrollBizPhone(cid, vk, el) {
  // 清除同容器内所有 active
  var container = el.closest('.biz-full-left');
  if (container) container.querySelectorAll('.biz-variant-card').forEach(c => c.classList.remove('biz-active'));
  el.classList.add('biz-active');
}
```

### CSS 变量命名转换规则

- design token 路径 → CSS var：斜线改连字符，全 kebab-case
  - `primary/bt/solidBg` → `--primary-bt-solid-bg`
- preview_html 中用 design token（`--bg-2`），不用 HTML shell alias（`--bg-card2`）

### 组件 JSON schema 节点类型（Wrapper / Leaf / 1:1 Ref）

每个组件定义有且仅有以下三种形态之一：

| 字段组合 | 节点类型 | 用途 |
|---|---|---|
| `css` + `component_refs` | **Wrapper** | 由多个子组件组合，描述自身布局 |
| `preview_html` | **Leaf** | 不可再分，直接写 HTML |
| `component_ref` | **1:1 Ref** | 精确指向另一个组件的某个变体 |

所有节点都可携带：
- `figma_name` — 含 emoji 前缀的 Figma 完整名称，同时作为 `cid`（COMPONENTS_DATA 的 key）
- `figma_key` — Figma 组件 hash（截图/MCP 调用用）
- `code_src` — 代码实现路径或包路径，用于代码生成和 Code Connect 注册（可选，逐步补齐）
- `props` — 仅限面向浏览器的用户交互 prop（variantMap / previewMap / booleans），不用于子组件配置

**`code_src` 格式约定：**
```json
// 💙 原子分子组件（库级）
{ "code_src": "@echo/ui/StatusBar" }

// 👻 业务组件（项目路径）
{ "code_src": "src/business/community/islands/Header" }
```

`code_src` 将用于：
1. 通过 `add_code_connect_map` 注册到 Figma Dev Mode，让 MCP `get_design_context` 带入规范
2. AI 生成项目代码时的 import 来源

**`component_refs` 子对象格式：**
```json
{ "cid": "💙 01.00 Status Bar", "props": { "Color": { "type": "VARIANT", "value": "White" }, "Type": { "type": "VARIANT", "value": "iPhoneX" } } }
```

**`component_ref` 格式（1:1 Ref）：**
```json
{ "cid": "💙 tab_bar", "props": { "Scene": { "type": "VARIANT", "value": "Islands" } } }
```
单变体组件可省略 props，解析时自动取唯一 variant。

---

### slots 字段规范

有 slots 的 variant 必须同时写：
1. **`preview_html`** — 使用子组件正确 HTML 结构
2. **`slots` 数组** — 声明引用关系，含 `name` / `boolProp` / `size` / `css`

渲染代码的 `showCompDetail` 已支持 slots 自动渲染，加了字段即自动显示。

### `props.IconSwaps` 实例替换规范

凡是 `props.IconSwaps` 里的 swap prop，必须同时满足两条规则：

**规则 A：`componentRef` — props 面板跳转芯片**

在 `props.IconSwaps` 的每个条目上加 `componentRef` 字段，值为目标组件的 CID（kebab-case）：

```json
"IconSwaps": {
  "Icon": {
    "swapProp": "Icon",
    "instanceKey": "xxx",
    "componentRef": "00.03-icon",
    "desc": "..."
  }
}
```

浏览器 `buildPropsHtml` 遇到 `componentRef` 时，自动渲染为可点击跳转芯片（主色描边 + cursor:pointer），点击调用 `showCompDetail(componentRef)`。

**规则 B：`data-component` — preview_html 里的实例元素**

`preview_html` 中对应 swapProp 的 HTML 元素，必须加 `data-component` 属性：

| 场景 | preview_html 中的写法 |
|------|----------------------|
| 图标实例（KurilIcons） | `<i class="KurilIcons kuril-xxx" data-component="💙 00.03_Icon / xxx">` |
| 其他组件实例 | `<div data-component="💙 XX.XX_组件名 / variant">` |

- `data-component` 值格式：`"💙 {figma_name}"` —— 浏览器解析时自动剥离 emoji、提取 CID 并跳转
- Boolean prop（`boolProp`）只控制显隐，不需要 `data-component`

**规则 C：`data-component` 空占位原则（非递归渲染）**

`preview_html` 里引用另一个原子分子组件时，**不得重写该组件的样式**。正确做法：只写尺寸/布局定位，内容留空。浏览器渲染时 `_resolveDataComponents()` 会自动从 COMPONENTS_DATA 拉取被引用组件的真实 preview HTML 注入进去。

**props 强制规则（不能闭眼写）**：`preview_html` 里放 `data-component` 占位后，必须先找到该 INSTANCE 节点在插件导出 JSON 里的 `variants` / `booleans` / `swaps` 字段，把所有**非默认值**的 prop 写进该变体的 `props` 字段（key = `"💙 组件名"`，完整含 emoji）。

> 如果当前没有导出 JSON（场景未导出过），可以用 `mcp_design_context`（Figma MCP）补：对该 instance 节点调用后，返回的 React props 签名（如 `color?: "White"`, `type?: "iPhoneX"`）就是实例当前选中的 prop 值，直接读取即可。仍然不得凭视觉推断。

格式：子组件 prop 配置在变体的 `props` 字段，`preview_html` 里 `data-component` 只含组件名

```json
// ✅ 正确：props 声明子组件配置，preview_html 干净
{
  "props": {
    "💙 01.00_Status Bar": { "Color": "White", "Type": "iPhoneX" }
  },
  "preview_html": "<div ...><div data-component=\"💙 01.00_Status Bar\" style=\"width:375px;height:44px;flex-shrink:0\"></div></div>"
}
```

```html
<!-- ❌ 错误1：把 props 塞进 data-component 字符串 -->
<div data-component="💙 01.00_Status Bar, Color=White, Type=iPhoneX" style="..."></div>

<!-- ❌ 错误2：用 data-* 属性传 props -->
<div data-component="💙 01.00_Status Bar" data-color="White" data-type="iPhoneX" style="..."></div>

<!-- ❌ 错误3：在 data-component 元素里手写子组件的 CSS -->
<div data-component="💙 01.00_Status Bar" style="display:flex;padding:0 16px;...">
  <span>11:27</span>...
</div>
```

只有以下情况才在 `data-component` 元素内写内容：
- 该元素的内容是**当前业务组件独有的定制**（不来自被引用的原子分子组件本身），如图标按钮上加业务标签文字
- 被引用组件尚未录入 COMPONENTS_DATA（临时 fallback，需标注 TODO）

### generate.py 末尾执行顺序

1. **`repair_component_slots()`** — 遍历有 `slots` 的 variant，自动把 `preview_html` 里对应元素替换为子组件正确结构，写回 JSON
2. **`validate_components()`** — 依次检查：
   - `kuril-*` 图标名是否在图标库
   - 有 slots 的 variant `preview_html` 是否有 `flex-direction:column`
   - 所有 `var(--)` 是否在 `_styles.css` 或 HTML inline `:root` 中定义
3. 出现 ⚠️ → 修完再提交

### `_slot_container_style(slot)` 规则

- 直接读 `slot['css']` dict 拼接 inline style 字符串，不依赖 slot 的 name
- `slot.css` 必须是完整规格（含 background、border-radius 等）
- 若 `slot.css` 中任何值是 dict（如 `font-size_by_size: {...}`），返回 `None`，repair 跳过该 slot（这类是复杂元素，preview_html 需手动硬编码）
- 新增子组件只需在 slot JSON 里写好完整 `css` 字段（全 string 值），repair 自动处理

### 重要：`group_by_prefix()` 不能删

`generate()` 用它生成 `main_groups` / `sem_groups` 写入 `INJECTED_DATA`，由 HTML 里 `renderL1()` 消费，删除会导致颜色 Primitives 显示「暂无数据」。

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

---

## 11 · 暂存区（待推进事项）

> 这里存放「已想清楚但还没开始做」的方向，回头说「执行暂存区的 XX」时直接从这里读。

### 11-A · IDE 桥接：与 H5 同事的 figma-to-code 对接

**背景**

H5 同事已有一套 `figma-to-code` CLI 工具，核心思路：
- Figma 骨架提取（去噪：INSTANCE 不展开、透传容器折叠、自适应宽度）
- 输出干净 HTML 骨架 + `figma-context.md`（组件映射、UnoCSS 配置）
- AI 读骨架 + `figma-context.md` → 翻译成项目业务代码（DuButton、DuInput 等）
- 支持 CLI 调用，不依赖 IDE MCP 交互

**他有的 / 我们有的**

| figma-to-code | echo-design-system |
|---|---|
| 结构准确的 HTML 骨架 | `usage_rules`、`props` 语义、使用场景 |
| INSTANCE → `<DuButton>` 占位 | 该用哪个 variant、为什么 |
| `figma-context.md` 手动维护 | `figma_name` 可自动映射 |

**缺的那一步（待实现）**

在 `generate.py` 里加 `generate_figma_context()` 函数，从 `COMPONENTS_DATA` 自动生成 `figma-context.md`：

```
COMPONENTS_DATA
  → figma_name → 项目组件名映射
  → usage_rules → 何时用哪个 variant
  → tokens_used → CSS 变量对应值
  → 输出到 figma-context.md
```

他的工具读这个文件，AI 拿到完整上下文，直接输出符合规范的业务代码。**他不用改工具，我们不用造代码生成器。**

**下一步行动**

1. 和 H5 同事确认 `figma-context.md` 的具体格式（他用什么字段）
2. 确认项目组件名前缀（Du*？还是其他？）
3. 让 Claude 写 `generate_figma_context()` 函数，输出到指定路径
