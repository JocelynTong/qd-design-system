# 千岛设计系统 · 原型工作台

千岛设计系统不只是一套组件库，而是一套**从需求到原型的完整工作流基础设施**。

PM 用自然语言描述需求，AI 读取设计规范和组件文档，直接生成可在浏览器预览的 HTML 原型，再通过 Figma 插件同步到设计稿供设计师精调。设计师精调后，结果通过插件导出回写到仓库规范稿，保证下一个需求的起点永远与线上一致。设计系统的 token 和组件变更通过飞书群机器人定期通知团队决策，形成闭环。

整个流程涉及四个角色：**PM**（提需求）、**AI**（生成原型）、**设计师**（在 Figma 精调）、**开发**（按原型还原）。仓库是唯一的交付中心。

---

## 完整工作流程

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

**① PM 描述需求**

PM 用自然语言描述需求，不需要特定格式。AI 需要从中识别：
- 属于哪个业务模块（社区？C2C？跨业务？）
- 涉及哪些页面（新页面还是在现有页面上改）
- 核心功能点是什么

---

**② AI 识别业务归属 → 读 `business/*.md`**

| PM 说的关键词 | AI 读取的文件 |
|-------------|-------------|
| 社区、帖子、Feed、内容详情 | `business/community.md` |
| C2C、商品、二手、下单 | `business/c2c.md` |
| 跨业务（如社区内容变现） | 两个都读 |

读取目的：确认页面的基线组件顺序，不自己发明结构。

---

**③ AI 规划页面清单**

确定本次需求涉及的所有页面，区分：
- **改已有页面**：在基线结构上增删组件
- **新建页面**：按 `business/{module}/*.html` 的规范稿从头搭

同时规划页面间的跳转关系，为后续写 `figma-config.json` 做准备。

---

**④ 创建需求文件夹**

命名规则：`{业务}-{需求简称}-v{版本号}`，一键初始化：

```bash
npm run new-demo community-feed-v1
```

自动从 `business/_styles.css` 复制冻结 CSS——此刻复制即冻结，后续 token 升级不影响旧需求视觉。同时显示候选池待决策数量。

---

**⑤ 搭建 HTML 原型**

从 `business/{module}/` 复制对应页面 HTML 作为起点，按需求修改：
- 引用 `./styles.css`（文件夹内的冻结版本）
- 页面专属样式写在 HTML 的 `<style>` 块里
- 图片占位用实色色块，不用渐变

---

**⑥ 编写 `figma-config.json`**

描述需求内所有页面的跳转关系：

```json
{
  "name": "社区内容变现 v1",
  "pages": [
    { "name": "01 首页Feed" },
    { "name": "02 帖子详情" },
    { "name": "03 商品弹层" }
  ],
  "connections": [
    { "from": "01 首页Feed", "to": "02 帖子详情", "trigger": "FeedCard" },
    { "from": "02 帖子详情", "to": "03 商品弹层", "trigger": "商品标签" }
  ]
}
```

跨业务跳转直接在 `connections` 里写，不受业务模块归属限制。

---

**⑦ 预览 & 迭代**

```bash
bash preview.sh                                          # 默认打开基线页面
bash preview.sh demos/community-feed-v1/home-feed.html  # 指定页面
```

同一需求的迭代在同一文件夹内改，不新建文件夹。

---

**⑧ 确认交付 → 文件夹冻结存档**

PM 最终确认后该文件夹不再修改，下一期迭代新建 v2 文件夹。回看历史原型直接打开对应文件夹的 HTML，视觉还原当时的 token 版本。

---

**⑨ 同步到 Figma**

```bash
npm run figma-sync community-feed-v1
```

读取需求文件夹的 `figma-config.json` → 自动在 Figma 里生成页面和跳转关系，供设计师精调。

---

**⑩ 设计师精调 → 插件导出 → 回写 business/ 规范稿**

设计师精调完成后：
1. 在 Figma 里选中对应 Section
2. 插件点「导出结构」→ 自动导出 variants + 文字内容 + 自定义节点 CSS
3. 将导出 JSON 粘给 AI
4. AI 对比差异，回写 `business/{module}/*.html` 规范稿
5. 规范稿更新后，下次 PM 新需求从最新规范稿开始

导出时插件自动校验 Frame 命名，并将非 token 节点追加到 `business/_candidates.md`。

---

**⑪ 候选池决策（每周一 11:00 飞书提醒）**

飞书群机器人每周一自动推送候选池状态，收口人做三选一决策：

| 选项 | 操作 |
|---|---|
| token 化 | AI 将新值加入 `business/_styles.css` |
| 业务组件 | AI 在 `business/{module}/` 里建组件片段 |
| 忽略 | 从候选池移除，保留为一次性裸值 |

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

插件「导出结构」功能会导出：组件 key + variant 属性 + 文字内容 + 非组件节点的 CSS（via `getCSSAsync`）。将导出 JSON 粘给 AI，AI 对比现有规范稿后回写 `business/{module}/*.html`。

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
