# 千岛设计系统 · AI 使用说明

> 本文件供 AI（如 Claude）自动读取。当产品经理或设计师向你描述界面需求时，请严格按照本文件中的规范输出设计方案。

设计系统浏览器：https://jocelyntong.github.io/qd-design-system/
组件文档目录：`components/` 目录下每个 JSON 文件

---

## 一、Token 三级映射规范

### 核心原则
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

详见 `components/typography.json`。设计稿基准：375×667px 一倍图。

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

---

### 图标规范（Icons）

详见 `components/icons.json`。

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

## 二、组件规范（已录入）

> 详细参数见 `components/` 目录下各 JSON 文件。以下为 PM 画原型时的速查表。

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
| 主操作（唯一 CTA） | `💙 00.05_Button / MH` | Color=Primary, Type=Solid, Size=Large(40) |
| 次要操作 | `💙 00.05_Button / MH` | Color=Primary, Type=Soft 或 Outline |
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

---

## 三、如何帮 PM 画原型

当 PM 描述一个页面需求时，请按以下步骤输出：

### 步骤 1：识别页面中的组件
将 PM 描述的每个 UI 元素映射到设计系统中的组件名称。

### 步骤 2：确定变体参数
对每个组件，给出完整的变体参数组合，例如：
```
按钮：💙 00.05_Button / MH
  Color = Primary
  Type = Solid
  Size = Large(40)
  Disable = False
```

### 步骤 3：输出 Figma 操作指引
告诉 PM 在 Figma 中如何找到和配置组件：
1. 在组件库中搜索组件名（如 `00.05_Button`）
2. 拖入画布
3. 在右侧面板切换 Variant 属性

### 步骤 4：给出布局建议
使用 Spacing token 描述间距：
- 页面边距：Spacing/Large (16px)
- 组件间距：Spacing/Normal (8px)
- 紧凑间距：Spacing/Small (4px)

---

## 四、输出格式模板

当帮 PM 设计一个页面时，请使用以下格式：

```
## [页面名称] 原型方案

### 页面结构
[描述页面的整体布局]

### 组件清单
| 区域 | 组件 | 变体参数 | 说明 |
|------|------|---------|------|
| 顶部 | NavigationBar | ... | ... |
| 内容区 | ... | ... | ... |
| 底部 | Button/MH | Color=Primary, Type=Solid, Size=Large(40) | 主 CTA |

### Figma 操作步骤
1. ...
2. ...

### Token 使用
- 背景色：bg/1
- 主文字：text/1
- ...
```

---

## 五、暂未录入的组件

以下组件页面存在于 Figma 文件中，但尚未整理成结构化文档，在帮 PM 设计时需谨慎使用：

**Bar 系列**：Status Bar, SegmentedControl, Menu, Steps, Home Indicator

**Form 系列**：FormItem, Textarea, Radio, Checkbox, Switch, Stepper, Upload, DateTimePicker, Rate

**Data 系列**：Feed（内容卡片）, Spu, Price, Empty, Swipe, Checklist, List, Grid

**Feedback 系列**：NoticeBar, SnackBar, Dropdown, Popover, ShareSheet, Result Page, Skeleton

> 如需使用以上组件，请告知设计师补充录入对应 `components/*.json` 文件。
