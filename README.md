# 回响 AI 设计系统 · 原型即上线

💡 **一个更近的未来**：从 PM 提需求到开发拿到可还原基准，整个周期可以极限压缩，其实正是目前整个「设计技术」领域在努力攻克的核心难题——如何真正打通设计与代码。你正处在这场变革的前沿探索中。

大多数团队的现实是：PM 写文档、AI 生成草图、设计师出稿、开发凭标注还原——四道工序，四份信息，每次交接都在损耗原始意图。最终落地的页面，和当初的设计意图之间，永远差那么一口气。

这套系统是回响对这个问题的回答：**原型即上线，速度极限压缩**。PM 描述需求，AI 从规范稿直接生成 HTML 原型，同步 Figma 精调，回写仓库——原型、设计稿、代码基准三者同源，从需求到交付不再靠人工比对和口头对齐。

涉及四个角色：**PM**（提需求）、**AI**（生成原型）、**设计师**（Figma 精调）、**开发**（按原型还原）。

---

## 各角色快速开始

> 默认已安装 Claude Code。在仓库目录打开终端 → `claude` 启动 → 发送下方指令即可。

**一次性初始化（所有人）**

```bash
git clone https://github.com/JocelynTong/qd-design-system.git
cd qd-design-system
```

---

### PM · 提需求出原型

**有新需求时，把这段话发给 Claude Code，最后一行接着写需求：**

```
我想出一个新需求原型。请先读 business/_rules.md，再根据我描述的需求判断业务归属，读对应规范稿，在 demos/ 下生成需求文件夹和 HTML 原型。

我的需求是：
```

**迭代修改：** 直接描述改动，AI 在原文件夹里改，不新建文件夹。

**确认交付：** 说「这版 OK 了，可以交付」，文件夹冻结存档，不再改动。

---

### 设计师 · 精调后回写规范

**Figma 里精调完成后，把这段话发给 Claude Code：**

```
精调完了，这是插件导出的 JSON：
[粘贴插件导出内容]

请更新对应业务的规范稿。
```

**新增了自定义设计元素：** 直接描述给 AI，AI 会写入规范并追加到候选池，等候收口人每周决策是否 token 化。

---

### 开发 · 拿还原基准

还原基准在 `demos/{需求文件夹}/`，直接打开对应 HTML 文件对照还原。样式已冻结，不受后续 token 升级影响。

有疑问时问 Claude Code：

```
请解释 demos/community-feed-v1/home-feed.html 里 XX 部分的结构和样式规范
```

---

## 完整工作流程

> 各角色的话术和指令随流程内嵌，持续更新。

```
① PM 描述需求
       ↓
② AI 识别业务归属
       ↓
③ AI 规划页面清单
       ↓
④ 创建需求文件夹
       ↓
⑤ 搭建 HTML 原型
       ↓
⑥ 编写 figma-config.json
       ↓
⑦ 预览 & 迭代
       ↓
⑧ 确认交付 → 文件夹冻结存档
       ↓
⑨ 同步到 Figma
       ↓
⑩ 设计师精调 → 插件导出 → 回写 business/ 规范稿
       ↓
⑪ 候选池决策（每周一 11:00 飞书提醒）
```

---

**① PM 描述需求** `角色：PM`

话术建议：

> 「我要在帖子详情页增加 XX 功能，用户可以 YY，点击后 ZZ」
> 「这是社区内容变现需求，从帖子里的商品标签跳转到 C2C 商品详情页」
> 「在已有的首页 Feed 上改，在搜索栏下方加一个 XX 入口」

不需要说明用哪个组件或怎么实现，只描述用户行为和目标页面即可。跨业务需求说清起点和终点。

---

**② AI 识别业务归属** `角色：AI`

AI 自动根据关键词判断并读取对应规范：

| 关键词 | 读取文件 |
|---|---|
| 社区、帖子、Feed、内容详情 | `business/community.md` + `community/*.html` |
| C2C、商品、二手、下单 | `business/c2c.md` + `c2c/*.html` |
| 跨业务 | 两个都读 |

此步骤无需 PM 干预，AI 自行完成。

---

**③ AI 规划页面清单** `角色：AI`

AI 自动确认本次需求涉及的所有页面：
- **改已有页面** → 从 `business/{module}/*.html` 规范稿开始改
- **新建页面** → 按规范稿的组件结构从头搭

同时规划页面间跳转关系，为写 `figma-config.json` 做准备。此步骤无需 PM 干预。

---

**④ 创建需求文件夹** `角色：AI 或开发`

```bash
npm run new-demo community-feed-v1   # 命名规则：{业务}-{需求简称}-v{版本号}
```

自动从 `business/_styles.css` 复制冻结 CSS，创建时即与外部脱钩，后续 token 升级不影响旧需求视觉。启动时同步显示候选池待决策数量。

---

**⑤ 搭建 HTML 原型** `角色：AI`

AI 从 `business/{module}/` 复制规范 HTML 作为起点，按需求修改后输出至需求文件夹。PM 无需操作，等待预览链接即可。

---

**⑥ 编写 `figma-config.json`** `角色：AI`

AI 同步生成页面流转配置：

```json
{
  "name": "社区内容变现 v1",
  "pages": [{ "name": "01 首页Feed" }, { "name": "02 帖子详情" }],
  "connections": [
    { "from": "01 首页Feed", "to": "02 帖子详情", "trigger": "FeedCard" }
  ]
}
```

跨业务跳转直接写在 `connections` 里，不受业务模块限制。

---

**⑦ 预览 & 迭代** `角色：PM`

```bash
bash preview.sh                                          # 默认打开基线页面
bash preview.sh demos/community-feed-v1/home-feed.html  # 指定需求页面
```

话术建议：

> 「第一稿的 XX 改成 YY，其他不动」
> 「把这个模块移到评论区下面，间距大一点」

同一需求的所有迭代在同一文件夹内改，不新建文件夹，不算新需求。

---

**⑧ 确认交付 → 文件夹冻结存档** `角色：PM`

话术建议：

> 「这版 OK 了，可以交付」

PM 确认后该文件夹不再修改，下一期迭代新建 v2 文件夹。

---

**⑨ 同步到 Figma** `角色：AI 或开发`

```bash
npm run figma-sync community-feed-v1
```

读取需求文件夹的 `figma-config.json` → 复制到剪贴板 → 在 Figma 插件里粘贴运行，自动生成页面帧和跳转连线。

---

**⑩ 设计师精调 → 回写规范稿** `角色：设计师 → AI`

设计师在 Figma 精调完成后：

话术建议：

> 「精调完了，这是导出的 JSON：[粘贴插件导出内容]，请更新 community 的规范稿」
> 「我在首页新加了一个渐变 banner，用的是 #7C66FF 到 #A594FF，高度 120px，帮我加进去」

AI 对比差异后回写 `business/{module}/*.html`，非 token 节点自动追加到候选池，Frame 命名异常时给出警告。

---

**⑪ 候选池决策** `角色：收口人`  每周一 11:00 飞书提醒

话术建议：

> 「渐变紫色背景 token 化，命名 `--brand-gradient-primary`」  → AI 加入 `business/_styles.css`
> 「虚线分割线做成社区业务组件，叫 community-divider」  → AI 在 `business/community/` 建片段
> 「手绘插画忽略，一次性的」  → AI 从候选池移除

```bash
npm run notify-feishu   # 手动触发飞书周报（测试用）
```

---

## 项目结构

```
├── CLAUDE.md                              # AI 工作指令（全局组件规范、页面尺寸安全区）
├── README.md                              # 本文件：工作流 + 目录 + 常见问题
├── index.html                             # 设计系统 Token 浏览器（GitHub Pages 展示）
├── generate.py                            # Figma 导出 JSON → CSS 变量转换脚本
├── package.json                           # npm 脚本入口
├── preview.sh                             # 本地预览脚本，自动打开/刷新浏览器
│
├── tokens/                                # 设计 Token 源头（Figma 导出，不手动编辑）
│   ├── 千岛.tokens.json                   # 亮色主题 L2/L3 Token
│   ├── 千岛暗黑.tokens.json               # 暗色主题 L2/L3 Token
│   ├── Primitives-QD.json                 # L1 原始色板
│   └── processed.json                     # generate.py 产物，自动生成
│
├── components/                            # 原子组件规范文档（AI 读，16 个组件）
│   └── button/navbar/tabs...json          # 各组件的变体、尺寸、用法说明
│
├── business/                              # 各业务模块的完整规范（source of truth）
│   ├── _rules.md                          # 全局规则：命名约定、token 铁律、安全区、候选池机制
│   ├── _styles.css                        # CSS 母版：token 变量 + reset + 通用组件（新需求从这里复制）
│   ├── _candidates.md                     # 设计候选池：非 token 新创意的追踪与决策记录
│   ├── community.md                       # 社区业务规则：组件 Key 表、variant 选择指引
│   ├── community/                         # 社区规范页面（设计师精调后回写至此）
│   │   ├── home-feed.html                 # 社区首页 Feed 最新规范稿
│   │   └── content-detail.html            # 帖子详情页最新规范稿
│   └── c2c.md                             # C2C 业务规则（待完善）
│
├── demos/                                 # 需求原型存档（一需求一文件夹，历史快照）
│   ├── styles.css                         # CSS 母版备份，不直接引用
│   └── community-default/                 # 社区基线需求（初始版本）
│       ├── styles.css                     # 冻结的 token 版本（创建时从 business/ 复制）
│       ├── home-feed.html                 # 该需求的首页 Feed 原型
│       ├── content-detail.html            # 该需求的帖子详情页原型
│       └── figma-config.json              # 该需求的页面流转配置
│
├── figma-plugin/                          # Figma 建稿插件（HTML → Figma 同步）
│   ├── code.js                            # 插件主逻辑：生成页面帧 + 可视化连线 + 导出结构
│   ├── ui.html                            # 插件操作界面
│   └── manifest.json                      # 插件配置
│
├── figma-plugin-keyfinder/                # Figma 辅助插件（查找组件 Key）
│   └── code.js                            # 按组件名搜索并输出 Figma Key
│
├── scripts/                               # 自动化脚本
│   ├── new-demo.js                        # 新需求初始化：建文件夹 + 复制冻结 CSS + 显示候选警告
│   ├── figma-sync-server.js               # 读需求 figma-config.json → 复制到剪贴板供插件使用
│   ├── notify-feishu.js                   # 读候选池 → 格式化飞书卡片 → POST webhook
│   ├── build-demo.js                      # 构建打包 demo HTML
│   └── parse-html-to-config.js            # 解析 HTML 生成 Figma 配置
│
└── .github/workflows/                     # GitHub Actions 自动化
    ├── build.yml                           # Token 更新时自动构建部署
    └── design-review.yml                  # 每周一 11:00 推送候选池周报到飞书群
```

---

## 常见问题

### 这个项目里谁读哪个文件？

| 文件 | 谁读 | 存什么 |
|------|------|--------|
| `tokens/*.json` | `generate.py` 脚本 | 颜色、间距、圆角的原始数值（Figma 导出）|
| `components/*.json` | AI | 组件的变体、尺寸、用法规范 |
| `business/_rules.md` | AI | 全局规则和约束，所有需求必读 |
| `business/*.md` | AI | 某个业务的组件 Key、variant 选择指引 |
| `business/{module}/*.html` | AI + 浏览器 | 该业务页面的最新规范稿，新需求的起点 |
| `business/_styles.css` | 复制到 demos/ | CSS 母版，新需求初始化时冻结一份 |
| `demos/*/*.html` | 浏览器 | 某次需求交付时的页面原型快照 |
| `demos/*/figma-config.json` | Figma 插件 | 页面流转关系，用于同步到 Figma |
| `business/_candidates.md` | AI + 收口人 | 设计候选池，非 token 元素的决策记录 |

---

### 为什么 token 要存两份？（JSON 和 CSS）

浏览器不认识 JSON，只认识 CSS。所以同一份 token 数据需要两种格式：

```
tokens/千岛.tokens.json    →   generate.py   →   business/_styles.css
{ "primary": "#7C66FF" }                          --primary-solid-bg: #7C66FF;

（设计师维护的源头）                                （浏览器能读的形式）
```

`_styles.css` 里的 token 变量是脚本生成的产物，不是手写的，不算重复。

---

### business/*.md 和 business/*.html 各管什么？

- `community.md`：**规则文档**，组件 Key 表、variant 怎么选、维护说明——给 AI 读的上下文
- `community/*.html`：**规范页面**，页面现在实际长什么样——设计师精调后的最新状态

MD 管「怎么做」，HTML 管「现在是什么」，两者不重叠。

---

### demos 为什么一个需求一个文件夹？

每个需求文件夹是一份**完整快照**。`styles.css` 在创建时从母版复制并冻结，之后与外部脱钩。即使设计系统 token 升级，旧需求的视觉也不受影响，方便随时回看历史版本的视觉状态。

---

### figma-config.json 是什么？

描述这个需求里各页面的跳转关系，供 Figma 插件读取，自动生成可点击的原型流程。一个需求一个文件，跨业务的页面跳转也直接写在 `connections` 里。

---

### 设计师改了 Figma，怎么同步回来？

插件「导出结构」功能会导出：组件 key + variant 属性 + 文字内容 + 非组件节点的 CSS。将导出 JSON 粘给 AI，AI 对比现有规范稿后回写 `business/{module}/*.html`。

非 token 的自定义节点会自动追加到 `business/_candidates.md`，每周一飞书提醒收口人决策。

---

## 飞书机器人配置

**第一步：创建机器人**

飞书群 → 群设置 → 机器人 → 添加机器人 → 自定义机器人 → 复制 Webhook 地址

**第二步：存入 GitHub Secrets**

仓库 → Settings → Secrets and variables → Actions → New repository secret
- Name：`FEISHU_WEBHOOK`
- Value：上一步的 Webhook 地址

完成后每周一 11:00 自动推送。手动触发：Actions → 「设计系统候选池提醒」→ Run workflow

---

## Token 更新流程

1. Figma 重新导出 JSON → 覆盖 `tokens/` 对应文件
2. `git add tokens/ && git commit -m "update: tokens" && git push`
3. GitHub Actions 自动运行 `generate.py` → 更新 `tokens/processed.json`
4. 同步更新 `business/_styles.css`（重新运行 generate.py 覆盖）

## 本地预览

```bash
python3 -m http.server 8080
# 访问 http://localhost:8080
```

> 直接双击 HTML 文件因浏览器 CORS 限制无法加载数据，需通过 HTTP 服务访问。
