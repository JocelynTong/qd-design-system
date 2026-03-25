# 千岛 · 社区业务规则

> PM 涉及社区模块的需求时，AI 读取本文件。
> 全局规则见 `00 CLAUDE.md`，页面结构见同目录 `*.html`。

---

## 组件索引

<!-- AUTO-GENERATED FROM JSON - DO NOT EDIT -->
- `islands.json` — 千岛社区业务组件集合，包含 Island 详情页布局组件、格子/滑动/固钉入口组件、广告卡片等。👻 前缀表示业务级组件。 · key: `b73b34e01e12a1637a206752cb7fad018de6349f`
- `mark-20260127.json` — Mark 展示组件（发布侧），展示 SPU 标记信息行，含评分、数量、重量、价格、渠道等结构化属性及编辑入口 · key: `f7237a1690352d70ab75b96d3268cb2a07006488`
- `post-published.json` — 帖子发布页业务组件集合，包含分区选择、商品标记、图片上传、正文编辑等发布流程组件。 · key: `f439ddc032c2b117bd6a311c1deceb214c16092b`
- `post.json` — 帖子详情页业务组件集合，包含帖子 Header、作者信息、内容区（15种类型）、元信息行、评论区、帖子描述等。
<!-- END AUTO-GENERATED -->

---

## 业务组件 Key 表

### 岛详情页（island-detail）

> Key 表来源：Figma「👻 社区结构 - 岛」页面，共 53 个组件（2026-03-09 录入）。
> 页面结构来自插件导出，Frame 原名「岛详情页」，已注册为 `island-detail`。

#### Islands 导航与结构组件

| 组件名 | Figma Key | 说明 |
|--------|-----------|------|
| `👻 Islands / Header` | `eecbc6c90b1707359ded719fde7ea758538f1a50` | 深色顶部区域容器（flex col，gap:10px） |
| `👻 Islands / Pin` | `e0eaba05d0e32d3ea7ef305765499b592ee04777` | 横向滚动的岛入口行 |
| `👻 Islands / PinCell` [COMPONENT_SET] | `3b39931ea67f0639e205e7c99107dc05cd95d063` | PinCell 组件集 |
| `👻 Islands / PinCell` · Type=Home | `0ee323d2a0cc150322dd836552a8923f8dbddb4f` | Pin 首页格 |
| `👻 Islands / PinCell` · Type=Islands | `a0bda7eff5e42f43757ae1716d70065e6782534a` | Pin 普通岛格 |
| `👻 Islands / PinCell` · Type=MyIslands | `73277f850c6f1e31e71bd8723e100fb8d3484ad8` | Pin 我的岛格 |
| `👻 Islands / Grid` | `9c425cfa52d08f39c0bd2470df414befee021d0e` | **岛内容区白卡（即 Contents 容器），含 GridCell 排列** |
| `👻 Islands / GridCell` [COMPONENT_SET] | `2184b6619f629c043de28f9bd34507af1b109e1f` | GridCell 组件集 |
| `👻 Islands / GridCell` · Type=ISLANDS | `86678f6945c04d9df33ae08a12475a4491c60090` | Grid 普通格（岛功能入口） |
| `👻 Islands / GridCell` · Type=Search | `1ee4d24fc36777f53c8678406847ad28c93774a5` | Grid 搜索格 |
| `👻 Islands / Slide` | `11f0f10369d4947c619c4f74b9d00219f04e32bc` | 横向轮播区（公告/活动） |
| `👻 Islands / SlideCell` [COMPONENT_SET] | `949c93dae2f644fcc16dc1656188b282afa31aaa` | SlideCell 组件集 |
| `👻 Islands / SlideCell` · Type=Notice | `aa0156e774187570f2820701d3ed571c996c39c4` | 轮播公告格 |

#### QuickEntry 快捷入口组件

| 组件名 | Figma Key |
|--------|-----------|
| `👻 Islands / QuickEntryCell / Title` [COMPONENT_SET] | `dec639b2e676dc978bcbe7dcf7d610a56c6c9d8c` |
| `👻 Islands / QuickEntryCell / Title` · Type=标题 | `f2950d98db8a87fdba06c01adfdfa14ed5deb84b` |
| `👻 Islands / QuickEntryCell / Title` · Type=闲置 | `27127a87ded28f22ec50809aeb682bebdd24acc3` |
| `👻 Islands / QuickEntryCell / Title` · Type=闪购 | `6a12de52216c26de614b00820c4a0bf67ebde2f9` |
| `👻 Islands / QuickEntryCell / Title` · Type=拍卖 | `fb7adcbd2ce958220f3fd751aa2cace5e9ae6dae` |
| `👻 Islands / QuickEntryCell / Title` · Type=福袋 | `6196de8ffc5a651e9bf4f52e40e14ba8425590b9` |
| `👻 Islands / QuickEntryCell / Title` · Type=拼团 | `e596d0d6ee4079c6796b893de717971be46a32fc` |
| `👻 Islands / QuickEntryCell / Title` · Type=拼车 | `960cb8a96156c37dcffe26659942f1b7a007487c` |
| `👻 Islands / QuickEntryCell / Title` · Type=商城 | `3fd3c90d9b37206a2997bf6719e46acaf407e01c` |
| `👻 Islands / QuickEntryCell / Title` · Type=日历 | `4e4941a079ff13d23bc4a0414cd97c93d47dc52b` |
| `👻 Islands / QuickEntryCell / Title` · Type=鉴别 | `66130e8e869cc5cd1658fca0da98ea4f66832b4a` |
| `👻 Islands / QuickEntryCell / Title` · Type=同城活动 | `36b9f1bbe021beb7111818831519b79ce4e48114` |
| `👻 Islands / QuickEntryCell / Title` · Type=寄售 | `e09d32a927ee8efc845ebf71512551f3bfde3670` |
| `👻 Islands / QuickEntryCell / Title` · Type=聊天室 | `0f9731aa92bec95ade03429d2bbe2603b9b08a43` |
| `👻 Islands / QuickEntryCell / Info` [COMPONENT_SET] | `f5d42f186d7a4fa28511f36cf34e7dd75c775315` |
| `👻 Islands / QuickEntryCell / Info` · 字号=11 | `d559b6df89950dc19cd68e4fd24e18a6fe8c1819` |
| `👻 Islands / QuickEntryCell / Info` · 字号=12 | `3d765368aaa33d988273f2c2ca376aa27d102003` |
| `👻 Islands / Pair+QuickEntry` [COMPONENT_SET] | `b73b34e01e12a1637a206752cb7fad018de6349f` |
| `👻 Islands / Pair+QuickEntry` · 数量=1 | `5b16926e13b6de8fe3eaaff9b92173dab16e992c` |
| `👻 Islands / Pair+QuickEntry` · 数量=2 | `af2e8e80fd2b2e8932a00d4093476432a8d9d0c3` |
| `👻 Islands / Pair+QuickEntry` · 数量=3 | `6cff3699e2afc5b0cb987c6fcba241b786a6bf02` |
| `👻 Islands / Pair+QuickEntry` · 数量=4~9 | `03664d877db25b9fa5e10e056886bdd8db6cd496` |
| `👻 Islands / Pair+QuickEntry` · 数量=3 Old Vision | `ea4a6b55bb1be319da0bae1cea506357e0a39f69` |
| `👻 Islands / Pair+QuickEntry` · 数量=4~9 Old Vision | `cc39331e2856da4002d7c5bea8f9a8f12699584e` |
| `👻 Islands / Pair+QuickEntry` · 数量=4~9 New Vision2 | `3c39ec0f29abac2bc57dd427710a015226a93ccd` |
| `👻 Islands / Pair+QuickEntry` · 数量=4~9 New Vision3 | `b6a13aab61bf5f669c37d8186acd36f2a43786ed` |

#### 广告组件（👻 Ad）

> COMPONENT_SET key: `f83ae119d7955665dba266c48dcc39117d91ba0e`

| 变体 | Figma Key |
|------|-----------|
| 视图=双列, 类型=首位 | `ec85b4878bba24a10cc471d8bcd8c18ef362575c` |
| 视图=双列, 类型=单图 | `99e8d967c65868c01786634e43d133f2c50b169a` |
| 视图=双列, 类型=帖子 | `1d8d58a67ecb341481700e04507643cbfe9093e1` |
| 视图=单列, 类型=首位 | `7d6ce71ad815f83710e4df406c39ffaea400e7eb` |
| 视图=单列, 类型=单图 | `2d3a71b94b5ce5a13cbec0bb6908fbf3cf08b3bb` |
| 视图=单列, 类型=帖子 | `38b26bd9f4ba8e4aa747305e96689a7f3d29f46b` |

#### 发现页组件

| 组件名 | Figma Key |
|--------|-----------|
| `👻 Islands / DiscoveryHeader` | `8ad2c9f998309ad6cb0bb534d366da4152b6c25d` |
| `👻 Islands / Discovery` | `4cdfb97c4bad528e37bd4a4468dc95aa276e297e` |

#### 其他

| 组件名 | Figma Key | 说明 |
|--------|-----------|------|
| `💙 01.05 Tab Bar / APP / 5Tabs` | *(系统组件，见 `02 components/` 目录)* | 岛页面底部 TabBar，2026-03-09 新增入页面组件列表 |
| `浅色底部适配` | `aec27850bc717c09a87f743af26fe06a70e95027` | 即「Property 1=Light」，浅色主题底部适配组件，配合 TabBar 使用 |
| `👻 Islands / Tag` | `3bdc1589cd9fb7da92e95c95d63010b3b0c334cb` | 岛内容标签组件 |
| `👻截屏刘海logo` | `682fe5df9cb18d1e27eb870e691005f4ad8acbfa` | 截图用刘海 Logo，非页面正式组件 |

---

#### 插件导出 CSS 备注（自定义节点，已更正为组件引用）

| 旧描述（插件自定义节点） | 对应正式组件 |
|----------------------|-------------|
| `👻 Islands / Header`（自定义）| → `👻 Islands / Header` key: `eecbc6c90b1707359ded719fde7ea758538f1a50` |
| `👻 Islands / Pin`（自定义）| → `👻 Islands / Pin` key: `e0eaba05d0e32d3ea7ef305765499b592ee04777` |
| `Contents`（自定义节点）| → `👻 Islands / Grid` key: `9c425cfa52d08f39c0bd2470df414befee021d0e` |

### 内容详情页

| 组件名 | Figma Key |
|--------|-----------|
| `👻 Post / Header` | `cb0eab1b81a0a45d20a3bb1bb935dc5a78149dce` |
| `👻 Post / User` | `b6eac960c5bb3bf9df0d8e79db07f9b16a5dbdf2` |
| `👻 Post / Contents · LargeImage4:3` | `9a4e80ea008538345b1798d8f777a9ffcce4652e` |
| `👻 Post / Contents · LargeImage3:4` | `0db8b003a07bb39b759da6186f9f3ed2d2ec1bc5` |
| `👻 Post / Contents · NineGrid` | `ed86390c4894edb322d6632672ffc38871a0f65e` |
| `👻 Post / Contents · MainText` | `f53ed1436faf8d996e5dca9133a6a315a2346080` |
| `👻 Post / Description` | `059e26c0dab5204619d673572e4a46f609633fa5` |
| `👻 Post / Info` | `391fcf6eecd471b9ba66e281bd9ad19e681721d1` |
| `👻 Post / Comments · Default` | `5b3fe9d88dd39248b843fb8635dbc642b3d572ff` |
| `👻 Post / Comments · Empty` | `3a7f143be35176e5f0fae92ec31acf62add9b059` |
| `CommentInfo20260118`（底部互动栏） | `ad544c67ed0ecc59e1879c3a1176ce9e689af85e` |

### 帖子发布页（post-published）

> Key 表来源：Figma「02_业务组件_👻_社区」页面，2026-03-23 录入。
> 对应文件：`03 business/community/post-published.json`

| 组件名 | Figma Key | 说明 |
|--------|-----------|------|
| `👻 Post Published / Islands` | `f439ddc032c2b117bd6a311c1deceb214c16092b` | 分区选择行，展示当前选中分区 Tag 和可切换的其他分区 |
| `👻 Post Published / Mark` | `f82d8fcf45ec186c80c82a32a9442bcdb0ebfaf9` | 商品标记行，展示已关联商品的标记摘要（SPU 缩图 + 属性统计 + 编辑入口） |
| `👻 Post Published / Rating` | `4df546927d62bb3749c7058afe4869b3e116a8cf` | 评分输入行，在支持评分的分区（如演出、室内娱乐）下展示 |
| `👻 Post Published / Attachments` | `ba498f1f9aac854f0fe2f24a0191df475aa5ae4a` | 图片/视频上传区，展示已上传缩略图（96×96）和添加按钮 |
| `👻 Post Published / Topic` | `dc454af04d1e0caced45201ba92e2063e9752d31` | 标题输入框（选填），Input_Line 样式，底部下划线，高度 44px |
| `👻 Post Published / Contents` | `e92961889aa5e469eaa4fb4080afeee55048e272` | 正文输入区，固定高度 208px，左侧带紫色光标线 |
| `👻 01.05 Tab Bar / APP / Tab / 3Tabs` | `3760b867389f7ddf6e614d254d65e6f32eb1820b` | 发布页底部 3 Tab 栏（👻 业务级），对应图片/视频/投票发布模式切换 |
| `👻 Post / Header` | `cb0eab1b81a0a45d20a3bb1bb935dc5a78149dce` | 发布页 NavBar：返回键 + 发布目的地（Island 缩图 + 名称）+ 发布按钮 |
| `👻 Post Published / Tools251127` | `527383e3d84041c1f92c706096623e1cd8064173` | 底部工具栏：字数统计、权限按钮、关联 SPU 行、地点标签、键盘快捷操作行 |

---

### Mark 20260127（发布侧标记组件）

> Key 表来源：Figma「02_业务组件_👻_社区」页面，2026-03-23 录入。
> 对应文件：`03 business/community/mark-20260127.json`

| 组件名 | Figma Key | 说明 |
|--------|-----------|------|
| `👻 Mark 20260127` [COMPONENT_SET] | `f7237a1690352d70ab75b96d3268cb2a07006488` | 发布侧 Mark 组件集合 |
| `👻 Mark 20260127` · Type=SingleMark | `23b5c7b8dd644848722be90c5355b61a2f3a4e54` | 单 SPU 标记行：缩图 + 名称 + 评分/数量/重量/价格/渠道等属性 + 编辑按钮 |
| `👻 Mark 20260127` · Type=MultipleMarks | `ffeec7bae9c1a5c6402f03ef8c95bbc3e717735a` | 多 SPU 缩图列表行：横向展示多个 SPU 缩图（≤3），后接省略标记 |

---

### 首页 Feed

| 组件名 | Figma Key |
|--------|-----------|
| `👻 Feed / Post · 2ColumnMobile` | `bc257468a92875667be7ef8502c1014821c5d58a` |
| `👻 Feed / Post · 1ColumnMobile` | `1d1a919c166abcced25e50d747c1b634dc19fdba` |

---

## Post / Contents 变体选择指引

| PM 描述 | 使用 variant |
|---------|-------------|
| 图文帖（横版图） | `LargeImage4:3` |
| 图文帖（竖版图） | `LargeImage3:4` |
| 九宫格图片 | `NineGrid` |
| 纯文字帖 | `MainText` |

---

## 维护说明

- **新增业务组件**：设计师在 Figma 发布后，运行 `05 figma-plugin/extract-business-keys.js`，将新 key 补充到上方表格
- **页面结构调整**：设计师精调 Figma 后，使用插件导出 → AI 回写 `03 business/community/*.html`
- **已注册 Frame 名单**：`home-feed`、`content-detail`、`island-detail`（插件导出时校验命名一致性）
- **⚠️ Figma Frame 命名提醒**：Figma 中「岛详情页」需改名为 `island-detail` 以通过插件校验
