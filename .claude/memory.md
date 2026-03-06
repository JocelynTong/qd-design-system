# AI 工作记忆 · Echo Design System

> 本文件记录跨会话积累的决策、踩坑和快捷参考。
> 和 CLAUDE.md 分开存放，后续不需要时直接删除本文件即可。

---

## 项目信息

- **GitHub**: https://github.com/JocelynTong/echo-design-system
- **Token 浏览器**: https://jocelyntong.github.io/echo-design-system/
- **Figma 文件 ID**: `HjpmfUPwU7HGMRj9X80TAY`
- **图标库 CSS**: `//at.alicdn.com/t/c/font_3550031_uwcy4h4l9a9.css`

---

## HTML 原型规范

- 共享样式在 `demos/styles.css`，各页面 `<style>` 只写页面专属样式
- 图片占位用**实色**，不用渐变（渐变看起来像设计元素）
- Demo 控件按钮：`position:fixed; top:16px; right:16px`，不放进设计稿区域
- **禁止**写裸 hex / rgba() / px 颜色值，必须用 `var(--token-name)`
- 需要新 token 时：先在 `demos/styles.css` 定义，再用 `var()`

---

## 关键 Bug 修复记录

- **瀑布流留白**：`grid-template-columns:1fr 1fr` → `column-count:2` + `break-inside:avoid`
- **视频图标位置**：`bottom` → `top`
- **Emoji 居中**：`.card-img img,.img-placeholder{display:block}` 覆盖了 flex → 拆分规则
- **按钮圆角成胶囊**：`Radius/Large(16px)` 在小按钮上被 clamp → 改用 `Radius/Normal(8px)`
- **switchLayout 布局切换**：`display:'grid'` → `display:'block'`（column-count 是 block 布局）

---

## Token 速查

- 字体栈：`'PingFang SC', -apple-system, Roboto, 'Hiragino Sans GB', 'Helvetica Neue', sans-serif`
- KurilIcons 尺寸 class：`.ki-22 / .ki-20 / .ki-16 / .ki-14 / .ki-12 / .ki-10`
- Typography class：`.t-h1~h8` / `.t-b4~b8` / `.t-n5~n6`（已加入 styles.css）
- 深色背景白色文字：`--white-text-color`(100%) / `--white-text-2`(64%) / `--white-text-3`(40%)
- 深色背景填充：`--white-soft-bg`(12%) / `--white-3`(12%) / `--white-5`(24%)
- `--error-solid-bg` = #D94A4E（error/6，表单报错）
- `--trade-solid-bg` = #F96464（trade/5，角标/价格）

---

## Figma Plugin 组件 Key 表

以 `figma-plugin/code.js` 里的 `KEYS` 对象为准，此处为便于查阅的副本：

| 组件 | Key |
|------|-----|
| 💙 Status Bar (Solid) | `2f0822c67ed4a4951a09fecb453f76ce7e882cf5` |
| 💙 Status Bar (Ghost) | `fca61ad869eda2219a414e1bd3799bfd88245da4` |
| 💙 NavBar | `360f770dbdab8921993cf27def796d9fd3d0f172` |
| 💙 Tabs | `c9686e38126de8f12027187be1a44b71ec9788bc` |
| 💙 TabBar | `58d45fd34a20eb2b8530af131a5291d7fa8782a9` |
| 👻 FeedCard (2ColumnMobile) | `bc257468a92875667be7ef8502c1014821c5d58a` |
| 👻 Post/Header | `cb0eab1b81a0a45d20a3bb1bb935dc5a78149dce` |
| 👻 Post/User | `b6eac960c5bb3bf9df0d8e79db07f9b16a5dbdf2` |
| 👻 Post/Contents (LargeImage3:4) | `0db8b003a07bb39b759da6186f9f3ed2d2ec1bc5` |
| 👻 Post/Description | `059e26c0dab5204619d673572e4a46f609633fa5` |
| 👻 Post/Info | `391fcf6eecd471b9ba66e281bd9ad19e681721d1` |
| 👻 Post/Comments Default | `5b3fe9d88dd39248b843fb8635dbc642b3d572ff` |
| 👻 Post/ActionBar | `6a884579d0077d98245b801aca063eed54362576` |
| 👻 Islands/Header | `eecbc6c90b1707359ded719fde7ea758538f1a50` |
| 👻 Islands/PinCell | `0ee323d2a0cc150322dd836552a8923f8dbddb4f` |
| 👻 Islands/Pin | `e0eaba05d0e32d3ea7ef305765499b592ee04777` |
| 👻 Islands/Grid | `9c425cfa52d08f39c0bd2470df414befee021d0e` |
| 👻 Islands/Slide | `11f0f10369d4947c619c4f74b9d00219f04e32bc` |
| 👻 Islands/PairQuickEntry | `ea4a6b55bb1be319da0bae1cea506357e0a39f69` |
| 👻 Islands/DiscoveryHeader | `8ad2c9f998309ad6cb0bb534d366da4152b6c25d` |
| 👻 Islands/Discovery | `4cdfb97c4bad528e37bd4a4468dc95aa276e297e` |
