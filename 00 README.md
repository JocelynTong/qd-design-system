# 回响 AI 设计系统 · 原型即上线

💡 **一个更近的未来**：从 产品经理 提需求到开发拿到可还原基准，整个周期可以极限压缩，其实正是目前整个「设计技术」领域在努力攻克的核心难题——如何真正打通设计与代码。你正处在这场变革的前沿探索中。

大多数团队的现实是：产品经理 写文档、AI 生成草图、设计师出稿、开发凭标注还原——四道工序，四份信息，每次交接都在损耗原始意图。最终落地的页面，和当初的设计意图之间，永远差那么一口气。

这套系统是回响对这个问题的回答：**原型即上线，速度极限压缩**。产品经理 描述需求，AI 从规范稿直接生成 HTML 原型，同步 Figma 精调，回写仓库——原型、设计稿、代码基准三者同源，从需求到交付不再靠人工比对和口头对齐。

涉及四个角色：**产品经理**（提需求）、**AI**（生成原型）、**设计师**（Figma 精调）、**开发**（按原型还原）。

与 iOS 开发 @David 沟通后，我们确定了两个阶段：

**现状最优解（当前打样阶段）**
产品经理 CC Demo 👉 产品经理 / 设计师 send CC page to Figma 👉 开发 send Figma to IDE，Done!

**未来理想解（设计系统完善后）**
产品经理 CC Demo 👉 产品经理 / 设计师 send CC page to IDE 👉 开发 IDE，Done!

先以现状最优解跑一段时间，随着设计系统逐渐完善，或许有一天可以直接跳入未来理想解——可以期待下！

---

## 工作流程与角色操作

> 默认已安装 Claude Code。在仓库目录打开终端 → `claude` 启动。

**一次性初始化（所有人）**

```bash
git clone https://github.com/JocelynTong/echo-design-system.git
cd echo-design-system
```

**全局流程一览**

```
产品经理 描述需求
       ↓
AI 识别业务归属 + 规划页面
       ↓
AI 生成 HTML 原型 + figma-config.json
       ↓
产品经理 预览 & 迭代
       ↓
产品经理 确认交付 → 发整个需求文件夹给设计师
       ↓
设计师 建稿 → Figma 精调 → 导出回写规范稿
       ↓
候选池决策（每周一 11:00 飞书提醒）
```

---

### 产品经理

**入职时（一次性）**

运行 `python3 -m http.server 8081 --directory .` → 访问 `http://localhost:8081`，看左侧「Token 三级映射原理」面板。不需要记住任何色值，只需要建立一个认知：颜色是有结构的，改底层一个值，所有引用它的地方会自动联动——这就是为什么设计系统能保持一致，也是为什么不能随口说「这里改成紫色」。

**提新需求**

把这段话发给 Claude Code，最后一行接着写需求：

```
我想出一个新需求原型。请先读 00 CLAUDE.md，再根据我描述的需求判断业务归属，读对应规范稿，在 04 demos/ 下生成需求文件夹和 HTML 原型。

我的需求是：
```

话术建议：

> 「我要在帖子详情页增加 XX 功能，用户可以 YY，点击后 ZZ」
> 「这是社区内容变现需求，从帖子里的商品标签跳转到 C2C 商品详情页」
> 「在已有的首页 Feed 上改，搜索栏下方加一个 XX 入口」

不需要说明用哪个组件或怎么实现，只描述用户行为和目标页面即可。跨业务需求说清起点和终点。

**预览 & 迭代**

```bash
bash preview.sh                                          # 默认打开基线页面
bash preview.sh 04\ demos/community-feed-v1/home-feed.html  # 指定需求页面
```

> 「第一稿的 XX 改成 YY，其他不动」
> 「把这个模块移到评论区下面，间距大一点」

同一需求的所有迭代在同一文件夹内改，不新建文件夹。

**确认交付**

说「这版 OK 了，可以交付」，文件夹冻结，不再修改。下一期迭代新建 v2 文件夹。

把整个需求文件夹（如 `04 demos/community-feed-v1/`）发给设计师（飞书 / Slack 均可）。

---

### AI（自动完成，无需干预）

收到需求后依次执行：

1. 根据关键词识别业务归属，读取对应规范

| 关键词 | 读取文件 |
|---|---|
| 社区、帖子、Feed、内容详情 | `03 business/community/_module.md` + `03 business/community/*.html` |
| C2C、商品、二手、下单 | `03 business/c2c/_module.md` + `03 business/c2c/*.html` |
| 跨业务 | 两个都读 |

2. 规划涉及页面：改已有页面从规范稿起点改，新建页面按规范结构搭

3. 创建需求文件夹，冻结 CSS（与外部脱钩，token 升级不影响旧需求视觉）

```bash
node '04 demos/new-demo.js' community-feed-v1   # 命名：{业务}-{需求简称}-v{版本号}
                                     # 实际创建：20260312-community-feed-v1/
```

4. 生成 HTML 原型 + `figma-config.json`（含页面跳转关系，跨业务跳转也直接写在 `connections` 里）

5. 精调后对比差异回写 `03 business/{module}/*.html`，非 token 节点自动追加候选池，Frame 命名异常时给出警告

---

### 设计师

**精调时参考 Token**

运行 `python3 -m http.server 8081 --directory .` → `http://localhost:8081`，可按 APP 切换（千岛 / 临界 / 奇货）、按分类筛选、点击色块复制色值。

---

**插件安装（一次性，需要 Figma Desktop）**

两个插件均为本地插件，需手动导入：

Figma Desktop → 顶部菜单「Plugins」→「Development」→「Import plugin from manifest...」

| 插件 | 选择的 manifest 路径 | 用途 |
|---|---|---|
| 千岛建稿助手 | `05 figma-plugin/manifest.json` | 建稿 + 导出结构 + 查找组件 Key |

导入后在 Figma 里通过「Plugins → Development → 插件名」运行。

---

**步骤一：建稿**（插件：千岛建稿助手）

收到产品经理发来的需求文件夹后，放入本地 `04 demos/` 目录（建议每人维护自己的 `04 demos/`，结构与仓库一致）。

```bash
node '05 figma-plugin/figma-sync-server.js' community-feed-v1
```

config 已复制到剪贴板。打开 Figma → 运行「千岛建稿助手」插件 → 粘贴 JSON → 点击「建稿」，自动生成页面帧 + 跳转连线。文件夹里的 HTML 原型可同步对照参考。

> 如果需要查某个组件在 Figma 里的 Key，运行「组件 Key 查找器」插件，输入组件名搜索，把找到的 key 告诉 AI 更新进 `05 figma-plugin/code.js`。

---

**步骤二：Figma 精调**

在生成的 Frame 里正常做设计。组件尽量用库里已有的，自定义节点（渐变、特殊图形等）会在导出时标记为候选池候选项，等收口人决策。

---

**步骤三：导出结构 → 回写规范稿**（插件：千岛建稿助手）

精调完成后：Figma 里选中对应 Section 或 Frame → 插件点击「导出选中 Section」→ 指令自动复制到剪贴板 → 直接粘贴给 Claude Code。

AI 对比差异后回写 `03 business/{module}/*.html`，Frame 命名与 HTML 文件名不一致时会给出警告。

---

**新增了自定义设计元素（无法通过插件导出）**

> 「我在首页新加了一个渐变 banner，用的是 #7C66FF 到 #A594FF，高度 120px，帮我加进去」

AI 会写入规范并追加到候选池，等收口人每周决策是否 token 化。

---

### 开发

**现状**

还原基准是设计师精调后的 Figma 链接，和现在大多数团队一样——对着标注还原，有疑问截图问设计师。

**目标**

还原基准迁移到 `demos/{需求文件夹}/` 里的 HTML 文件。样式已冻结、token 已对齐，结构即规范，不再需要反复确认标注，也不受后续 token 升级影响。

> 两者的核心区别：Figma 是静态截图，HTML 是可运行的实现意图。开发按 HTML 还原，和最终落地的差距会小得多。

**查阅 Token 值**

运行 `python3 -m http.server 8081 --directory .` → `http://localhost:8081`，可搜索 token 名称或色值。

**有疑问时问 Claude Code**

```
请解释 04\ demos/community-feed-v1/home-feed.html 里 XX 部分的结构和样式规范
```

---

### 收口人 · 候选池决策

每周一 11:00 飞书提醒，三选一拍板：

> 「渐变紫色背景 token 化，命名 `--brand-gradient-primary`」  → AI 加入 `01 tokens/_styles.css`
> 「虚线分割线做成社区业务组件，叫 community-divider」  → AI 在 `03 business/community/` 建片段
> 「手绘插画忽略，一次性的」  → AI 从候选池移除

```bash
node notify-feishu.js   # 手动触发飞书周报（测试用）
```

---

## 项目结构

```
├── 00 CLAUDE.md                           # AI 工作指令（全局组件规范、页面尺寸安全区）
├── 00 README.md                           # 本文件：工作流 + 目录 + 常见问题
├── 00 design-system-index.html            # 设计系统预览入口（Token · 组件 · 业务组件）
├── preview.sh                             # 本地预览脚本，自动打开/刷新浏览器
│
├── generate.py                            # Token/组件/业务组件 JSON → CSS 转换脚本（根目录，统管全局）
├── _candidates.md                         # 设计候选池：跨层待决策元素（token化/组件化/忽略）
├── notify-feishu.js                       # 飞书候选池周报推送脚本
│
├── 01 tokens/                             # 设计 Token 源头（Figma 导出，不手动编辑）
│   ├── 00 qiandao/                        # 千岛品牌 token
│   │   ├── 千岛.tokens.json               # 亮色主题 L2/L3 Token
│   │   ├── 千岛暗黑.tokens.json           # 暗色主题 L2/L3 Token
│   │   ├── Primitives-QD.json             # L1 原始色板
│   │   └── processed.json                 # generate.py 产物，自动生成
│   ├── 01 qihuo/                          # 奇货品牌 token
│   └── 02 linjie/                         # 临界品牌 token
│
├── 02 components/                         # 原子组件规范文档（AI 读，16 个组件）
│   └── button/navbar/tabs...json          # 各组件的变体、尺寸、用法说明
│
├── 03 business/                           # 各业务模块的完整规范（source of truth）
│   ├── _styles.css                        # 业务层样式（@import 02 components，新需求从这里拼接）
│   ├── _candidates.md                     # → 已移至根目录
│   ├── community/                         # 社区业务模块
│   │   ├── _module.md                     # 社区业务规则：组件 Key 表、variant 选择指引
│   │   ├── home-feed.html                 # 社区首页 Feed 最新规范稿
│   │   └── content-detail.html            # 帖子详情页最新规范稿
│   ├── c2c/                               # C2C 业务模块
│   │   └── _module.md                     # C2C 业务规则（待完善）
│   └── notify-feishu.js                   # → 已移至根目录
│
├── 04 demos/                              # 需求原型存档（一需求一文件夹，历史快照）
│   ├── new-demo.js                        # 新需求初始化脚本（服务此目录，归属于此）
│   ├── build-demo.js                      # 构建打包 demo HTML
│   └── community-default/                 # 社区基线需求（初始版本）
│       ├── styles.css                     # 冻结的 token 版本（创建时从 03 business/ 复制）
│       ├── home-feed.html                 # 该需求的首页 Feed 原型
│       ├── content-detail.html            # 该需求的帖子详情页原型
│       └── figma-config.json              # 该需求的页面流转配置
│
├── 05 figma-plugin/                       # Figma 建稿插件本地源码
│   ├── manifest.json                      # 插件配置，Figma Desktop 导入用
│   ├── code.js                            # 插件主逻辑：建稿 / 导出结构 / 可视化连线
│   ├── ui.html                            # 插件操作界面
│   ├── extract-business-keys.js           # 控制台脚本：按关键词批量提取 Key，贴入 _module.md
│   ├── figma-sync-server.js               # 读 figma-config.json → 复制到剪贴板供插件使用
│   ├── parse-html-to-config.js            # 解析 HTML 生成 Figma 配置
│   └── diagnose.js                        # 插件诊断/调试脚本
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
| `01 tokens/**/*.json` | `generate.py` 脚本 | 颜色、间距、圆角的原始数值（Figma 导出）|
| `02 components/*.json` | AI | 组件的变体、尺寸、用法规范 |
| `00 CLAUDE.md` | AI | 全局规范、token铁律、组件速查、工作流、架构规则——所有需求必读 |
| `03 business/*.md` | AI | 某个业务的组件 Key、variant 选择指引 |
| `03 business/{module}/*.html` | AI + 浏览器 | 该业务页面的最新规范稿，新需求的起点 |
| `03 business/_styles.css` | 拼接到 `04 demos/` | 业务层，拼接 01+02+03 后冻结为 demo styles.css |
| `04 demos/*/*.html` | 浏览器 | 某次需求交付时的页面原型快照 |
| `04 demos/*/figma-config.json` | Figma 插件 | 页面流转关系，用于同步到 Figma |
| `_candidates.md` | AI + 收口人 | 设计候选池，非 token 元素的决策记录 |

---

### 为什么 token 要存两份？（JSON 和 CSS）

浏览器不认识 JSON，只认识 CSS。所以同一份 token 数据需要两种格式：

```
01 tokens/00 qiandao/千岛.tokens.json    →   generate.py   →   01 tokens/_styles.css（token 变量）
                                                           ↓
                                              02 components/_styles.css（@import 01）
                                                           ↓
                                              03 business/_styles.css（@import 02）
                                                           ↓
                                              new-demo.js 拼接三层 → demo/styles.css（冻结快照）

（设计师维护的源头）                                （浏览器能读的形式）
```

`01 tokens/_styles.css` 里的 token 变量是脚本生成的产物，不是手写的，不算重复。

---

### 03 business/{module}/_module.md 和 03 business/{module}/*.html 各管什么？

- `_module.md`：**规则文档**，组件 Key 表、variant 怎么选、维护说明——给 AI 读的上下文
- `{module}/*.html`：**规范页面**，页面现在实际长什么样——设计师精调后的最新状态

MD 管「怎么做」，HTML 管「现在是什么」，两者不重叠。

---

### demos 为什么一个需求一个文件夹？

每个需求文件夹是一份**完整快照**。`styles.css` 在创建时从母版复制并冻结，之后与外部脱钩。即使设计系统 token 升级，旧需求的视觉也不受影响，方便随时回看历史版本的视觉状态。

---

### figma-config.json 是什么？

描述这个需求里各页面的跳转关系，供 Figma 插件读取，自动生成可点击的原型流程。一个需求一个文件，跨业务的页面跳转也直接写在 `connections` 里。

---

### 设计师改了 Figma，怎么同步回来？

插件「导出结构」功能会导出：组件 key + variant 属性 + 文字内容 + 非组件节点的 CSS。将导出 JSON 粘给 AI，AI 对比现有规范稿后回写 `03 business/{module}/*.html`。

非 token 的自定义节点会自动追加到 `_candidates.md`，每周一飞书提醒收口人决策。

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

1. Figma 重新导出 JSON → 覆盖 `01 tokens/` 对应文件
2. `git add '01 tokens/' && git commit -m "update: tokens" && git push`
3. GitHub Actions 自动运行 `generate.py` → 更新 `01 tokens/*/processed.json`
4. 同步更新 `01 tokens/_styles.css`（重新运行 generate.py 覆盖）

## 常用命令

```bash
# Token 全量更新（Figma 导出新 JSON 后运行）
python3 generate.py

# 只更新某个 APP
python3 generate.py linjie    # 临界
python3 generate.py qiandao   # 千岛
python3 generate.py qihuo     # 奇货
python3 generate.py shangjia  # 商家版

# 设计系统预览 → http://localhost:8081
python3 -m http.server 8081 --directory .

# 需求原型预览 → http://localhost:8080
python3 -m http.server 8080 --directory '04 demos'

# 新需求初始化
node '04 demos/new-demo.js' community-feed-v1

# 飞书周报（手动触发）
node notify-feishu.js
```

> 直接双击 HTML 文件因浏览器 CORS 限制无法加载数据，需通过 HTTP 服务访问。
