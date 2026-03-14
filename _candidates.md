# 设计系统候选池

> 由 Figma 插件导出时自动追加，AI 归纳高频模式。
> 收口人每次开新需求时查看，或等飞书周报（每周一 11:00）提醒。
>
> 决策三选一：**🎨 token 化** → `01 tokens/` / **🧩 组件化** → `02 components/` / **📄 业务** → `03 business/{module}/` / **忽略（一次性）**

---

## 🔴 需要决策（3次以上）

| 元素描述 | CSS 值 | 出现次数 | 最近需求 | 预计去向 |
|---|---|---|---|---|

---

## 🟡 观察中（1-2次）

| 元素描述 | CSS 值 | 出现次数 | 最近需求 | 预计去向 |
|---|---|---|---|---|
| `👻 Islands / Header` gap 10px | `gap: 10px`（介于 Spacing/Normal 8px 和 Spacing/Medium 12px 之间，未 token 化） | 1 | island-detail（2026-03-09） | 🎨 token |

> ✅ 已解决：「`👻 Islands / Pin`」和「`Contents`（白卡容器）」在 2026-03-09 补录 key 后确认为正式注册组件（`👻 Islands / Pin` key: `e0eaba05d0e32d3ea7ef305765499b592ee04777`；`Contents` = `👻 Islands / Grid` key: `9c425cfa52d08f39c0bd2470df414befee021d0e`），已从候选池移除。
