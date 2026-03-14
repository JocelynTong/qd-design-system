/**
 * 千岛 · Demo 构建器
 * 运行: node '04 demos/build-demo.js'
 * 读取 demos/figma-config.json → 按组件顺序重新生成 demos/*.html
 *
 * 更新配置后只需重跑此脚本，本地 demo 自动刷新
 */

'use strict';
const fs   = require('fs');
const path = require('path');

const configPath = path.join(__dirname, 'figma-config.json');
const outDir     = __dirname;
const config     = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

// ── 分类：哪些组件固定在顶部 / 底部，哪些在滚动区 ──────────────
const FIXED_TOP    = new Set(['StatusBarSolid','StatusBarGhost','NavBar','PostHeader']);
const FIXED_BOTTOM = new Set(['TabBar','PostActionBar']);

// ── 每个组件的像素高度（用于计算滚动区高度）──────────────────────
const HEIGHTS = {
  StatusBarSolid: 44, StatusBarGhost: 0, // Ghost 透明叠加，不占流式高度
  NavBar: 44, PostHeader: 88,
  TabBar: 49, PostActionBar: 83,
  SearchBar: 48, Tabs: 40, TagHeader: 64,
};

// ── 页面元数据 ───────────────────────────────────────────────────
const PAGE_META = {
  '01 首页 Feed':  { file: 'home-feed.html',      title: '首页 Feed · 千岛',    flowIdx: 0 },
  '02 内容详情页': { file: 'content-detail.html', title: '内容详情页 · 千岛',  flowIdx: 1 },
  '03 Tag 详情页': { file: 'tag-detail.html',     title: 'Tag 详情页 · 千岛',   flowIdx: 2 },
};

// ── 组件 HTML 模板 ───────────────────────────────────────────────
const TPL = {

  StatusBarSolid: () => `
  <div class="status-bar status-bar--solid">
    <span class="status-bar-time">9:41</span>
    <div class="status-bar-icons"><span>●●●</span><span>WiFi</span><span>🔋</span></div>
  </div>`,

  StatusBarGhost: () => `
  <div class="status-bar status-bar--ghost">
    <span class="status-bar-time">9:41</span>
    <div class="status-bar-icons"><span>●●●</span><span>WiFi</span><span>🔋</span></div>
  </div>`,

  NavBar: (ctx) => ctx === '03 Tag 详情页' ? `
  <div class="navbar">
    <button class="icon-btn" onclick="history.length>1?history.back():location.href='content-detail.html'">
      <i class="KurilIcons kuril-arrow_left ki-22"></i>
    </button>
    <div class="navbar-title" id="navTitle"># Figma</div>
    <div class="navbar-right-placeholder"></div>
  </div>` : `
  <div class="navbar">
    <div class="navbar-logo">千<span>岛</span></div>
    <div class="navbar-right">
      <button class="icon-btn">
        <i class="KurilIcons kuril-alarm ki-22"></i>
        <span class="badge">3</span>
      </button>
    </div>
  </div>`,

  PostHeader: () => `
  <div class="post-header">
    <div class="post-header-inner">
      <div class="navbar-left">
        <button class="icon-btn" onclick="history.length>1?history.back():location.href='home-feed.html'">
          <i class="KurilIcons kuril-arrow_left ki-22"></i>
        </button>
      </div>
      <div class="navbar-right">
        <button class="icon-btn"><i class="KurilIcons kuril-share ki-22"></i></button>
        <button class="icon-btn"><i class="KurilIcons kuril-more ki-22"></i></button>
      </div>
    </div>
  </div>`,

  TabBar: () => `
  <div class="tabbar">
    <div class="tab-bar-item active"><i class="KurilIcons kuril-discover"></i><span class="tb-label">首页</span></div>
    <div class="tab-bar-item"><i class="KurilIcons kuril-topic"></i><span class="tb-label">发现</span></div>
    <div class="tab-bar-item publish"><i class="KurilIcons kuril-plus_circle_filled"></i><span class="tb-label" style="color:var(--primary-5)">发布</span></div>
    <div class="tab-bar-item" style="position:relative"><i class="KurilIcons kuril-message"></i><span class="tb-label">消息</span><span class="tb-badge">2</span></div>
    <div class="tab-bar-item"><i class="KurilIcons kuril-me_account"></i><span class="tb-label">我的</span></div>
  </div>`,

  PostActionBar: () => `
  <div class="bottom-bar">
    <div class="comment-input"><span>说点什么…</span></div>
    <div class="bottom-actions">
      <div class="action-btn active" id="likeBtn" onclick="toggleLike()">
        <i class="KurilIcons kuril-community_like_selected_filled"></i>
        <span class="action-count">1.2万</span>
      </div>
      <div class="action-btn" id="starBtn" onclick="toggleStar()">
        <i class="KurilIcons kuril-collect_normal" id="starIcon"></i>
        <span class="action-count">收藏</span>
      </div>
      <div class="action-btn">
        <i class="KurilIcons kuril-share"></i>
        <span class="action-count">分享</span>
      </div>
    </div>
  </div>`,

  // ── 岛组件 ──────────────────────────────────────────────────────

  IslandsHeader: () => `
  <div class="islands-header-bar">
    <span class="islands-title">我的岛</span>
    <span class="islands-more">全部 <i class="KurilIcons kuril-arrow_right ki-12"></i></span>
  </div>`,

  IslandsPinCell: () => TPL.IslandsPin(),

  IslandsPin: () => `
  <div class="islands-pin-row">
    ${[
      {emoji:'🎨',name:'设计交流'},
      {emoji:'🧸',name:'潮玩收藏'},
      {emoji:'🎮',name:'电玩部落'},
      {emoji:'📚',name:'读书岛'},
      {emoji:'🌸',name:'二次元'},
    ].map(p => `
    <div class="islands-pin-item">
      <div class="islands-pin-avatar">${p.emoji}</div>
      <span class="islands-pin-name">${p.name}</span>
    </div>`).join('')}
  </div>`,

  IslandsGrid: () => `
  <div class="islands-grid-row">
    ${[
      {emoji:'🎨',name:'设计交流',count:'2.4万'},
      {emoji:'🧸',name:'潮玩收藏',count:'1.8万'},
      {emoji:'🎮',name:'电玩部落',count:'3.1万'},
      {emoji:'📚',name:'读书岛',count:'9.6k'},
    ].map(p => `
    <div class="islands-grid-item">
      <div class="islands-grid-avatar">${p.emoji}</div>
      <div class="islands-grid-name">${p.name}</div>
      <div class="islands-grid-meta">${p.count} 成员</div>
    </div>`).join('')}
  </div>`,

  IslandsSlide: () => `
  <div class="islands-slide-row">
    ${[
      {emoji:'🎨',name:'设计交流',desc:'设计师的聚集地'},
      {emoji:'🧸',name:'潮玩收藏',desc:'限定款开箱晒图'},
      {emoji:'🎮',name:'电玩部落',desc:'游戏攻略每日更新'},
    ].map(p => `
    <div class="islands-slide-card">
      <div class="islands-slide-cover">${p.emoji}</div>
      <div class="islands-slide-name">${p.name}</div>
      <div class="islands-slide-desc">${p.desc}</div>
    </div>`).join('')}
  </div>`,

  IslandsPairQuickEntry: () => `
  <div class="islands-quick-entry">
    <div class="islands-quick-title">快速入口</div>
    <div class="islands-quick-grid">
      ${['闲置','闪购','拍卖','福袋','拼团','拼车'].map(t=>`
      <div class="islands-quick-item"><span>${t}</span></div>`).join('')}
    </div>
  </div>`,

  IslandsDiscoveryHeader: () => `
  <div class="islands-discovery-header-bar">
    <span class="islands-title">发现更多岛</span>
    <span class="islands-more">换一批</span>
  </div>`,

  IslandsDiscovery: () => `
  <div class="islands-discovery-list">
    ${[
      {emoji:'🌿',name:'植物爱好者',members:'4.2万',desc:'绿植养护 · 多肉打卡'},
      {emoji:'🎭',name:'戏剧迷俱乐部',members:'1.3万',desc:'话剧 · 音乐剧 · 演出'},
    ].map(p=>`
    <div class="islands-discovery-item">
      <div class="islands-discovery-avatar">${p.emoji}</div>
      <div class="islands-discovery-info">
        <div class="islands-discovery-name">${p.name}</div>
        <div class="islands-discovery-meta">${p.members} 成员 · ${p.desc}</div>
      </div>
      <button class="islands-join-btn">+ 加入</button>
    </div>`).join('')}
  </div>`,

  // ── Post 组件 ──────────────────────────────────────────────────

  PostUser: () => `
  <div class="post-user">
    <div class="avatar" id="authorAvatar">洁</div>
    <div class="author-info">
      <div class="author-name" id="authorName">设计师洁 · 设计碎碎念</div>
      <div class="author-meta">2025-12-18 · 广东</div>
    </div>
    <button class="btn-follow">+ 关注</button>
  </div>`,

  PostContents: () => `
  <div class="post-contents" id="postContents"><span id="coverEmoji">🎴</span></div>`,

  PostDescription: () => `
  <div class="post-description">
    <h1 class="post-title" id="postTitle">用 Figma Variables 搭了一套完整的设计系统，真的救活了产品团队</h1>
    <div class="post-text">
      <p>去年底开始接手了一个县城级政务+生活服务的产品，团队小，设计师就我一个，但要同时维护 App、小程序、H5 三端。</p>
      <p>之前每次换色换间距都要改几百个地方，噩梦。后来花了三周用 Figma Variables 搭了一套三级 Token 映射的设计系统。</p>
    </div>
    <div class="tags-row">
      <a class="tag" href="tag-detail.html?tag=Figma"># Figma</a>
      <a class="tag" href="tag-detail.html?tag=设计系统"># 设计系统</a>
      <a class="tag" href="tag-detail.html?tag=DesignToken"># Design Token</a>
    </div>
  </div>`,

  PostInfo: () => `
  <div class="post-info">
    <div class="stat-item"><i class="KurilIcons kuril-discover ki-16"></i>2.4万 浏览</div>
    <div class="stat-item"><i class="KurilIcons kuril-comment ki-16"></i>386 评论</div>
    <div class="stat-item"><i class="KurilIcons kuril-community_like_selected_filled ki-16" style="color:var(--error-solid-bg)"></i>1.2万 喜欢</div>
  </div>`,

  PostComments: () => `
  <div class="post-comments">
    <div class="comments-header">
      <span class="comments-title">评论 386</span>
      <span class="comments-meta">最热 ▾</span>
    </div>
    <div class="comment-list">
      ${[
        {bg:'#C7B8FF',ch:'小',name:'小鱼爱设计',text:'太有用了！我们公司也是这个情况，设计师就一个，要维护好几个端。',time:'3天前 · 上海',likes:'248'},
        {bg:'#9DE09D',ch:'前',name:'前端小明',text:'作为开发来说真的很感谢这种设计师，token 直接对应 CSS 变量，换主题简直不要太爽。',time:'5天前 · 北京',likes:'186'},
        {bg:'#FFABAB',ch:'产',name:'产品汪小白',text:'请问那个 AI 帮 PM 画原型是怎么实现的？我们 PM 画的原型和设计稿差很多！',time:'1周前 · 广州',likes:'112'},
      ].map(c=>`
      <div class="comment-item">
        <div class="comment-avatar" style="background:${c.bg}">${c.ch}</div>
        <div class="comment-content">
          <div class="comment-name">${c.name}</div>
          <div class="comment-text">${c.text}</div>
          <div class="comment-footer">
            <span class="comment-time">${c.time}</span>
            <span class="comment-like"><i class="KurilIcons kuril-community_like_normal ki-14"></i>${c.likes}</span>
          </div>
        </div>
      </div>`).join('')}
    </div>
    <div class="view-more">查看全部 386 条评论 →</div>
  </div>`,

  // ── Feed 卡片（批量使用，会被 wrapFeedCards 包装成 grid）───────
  FeedCard: (idx) => {
    const cards = [
      {emoji:'🎴',bg:'C7B8FF',ratio:'4/3',tag:{cls:'trade',txt:'HOT'},title:'这套 Figma Variables 三级映射真的绝了，换色只需要改一处',user:'设计师洁',likes:'1.2万',liked:true},
      {emoji:'🌿',bg:'9DE09D',ratio:'3/4',tag:{cls:'primary',txt:'新品'},title:'手办开箱 | 这款限定版真的太好看了',user:'潮玩研究所',likes:'3.4k',video:true},
      {emoji:'🎨',bg:'C7B8FF',ratio:'4/3',tag:{cls:'primary',txt:'精华'},title:'Auto Layout 高阶用法，99% 的人不知道这个技巧',user:'设计师洁',likes:'8.8k'},
      {emoji:'🖼️',bg:'B8E4FF',ratio:'3/4',title:'用 Variables 做多端适配，一套变量覆盖 Web/iOS/Android',user:'Token 研究员',likes:'5.2k'},
      {emoji:'💡',bg:'FFD6A5',ratio:'4/3',tag:{cls:'trade',txt:'HOT'},title:'Figma Dev Mode 上线后，设计研发协作效率提升了多少？',user:'UI设计师小K',likes:'3.1k'},
      {emoji:'🌱',bg:'C9F0D1',ratio:'3/4',title:'从零开始学 Figma，这 10 个插件让你事半功倍',user:'新手设计师',likes:'2.4k'},
    ];
    const c = cards[idx % cards.length];
    return `
      <div class="feed-card" onclick="openDetail('${c.emoji}','${c.bg}','7C66FF','${c.title}','${c.user}','${c.bg}')">
        <div class="card-img" style="aspect-ratio:${c.ratio}">
          <div class="img-placeholder" style="height:100%;background:#${c.bg}">${c.emoji}</div>
          ${c.tag ? `<div class="card-img-tags"><span class="img-tag ${c.tag.cls}">${c.tag.txt}</span></div>` : ''}
          ${c.video ? `<div class="video-icon"><i class="KurilIcons kuril-video_play_circle_filled" style="font-size:24px;color:#fff"></i></div>` : ''}
        </div>
        <div class="card-content"><p class="card-title">${c.title}</p></div>
        <div class="card-user">
          <div class="user-left"><div class="user-avatar-sm" style="background:#${c.bg}"></div><span class="user-name">${c.user}</span></div>
          <div class="user-like${c.liked?' liked':''}"><i class="KurilIcons kuril-community_like_${c.liked?'selected_filled':'normal'} ki-12"></i>${c.likes}</div>
        </div>
      </div>`
  },
};

// ── FeedCard 批量包装成双列 grid ─────────────────────────────────
function renderContentComponents(keys, pageName) {
  const lines = [];
  let i = 0;
  while (i < keys.length) {
    const key = keys[i];
    if (key === 'FeedCard') {
      // 收集连续的 FeedCard
      const batch = [];
      while (i < keys.length && keys[i] === 'FeedCard') { batch.push(i); i++; }
      lines.push(`
  <div class="scroll-area">
    <div class="feed-dual">` +
        batch.map((_, idx) => TPL.FeedCard(idx)).join('') + `
    </div>
  </div>`);
    } else if (TPL[key]) {
      const tplFn = TPL[key];
      const html = tplFn(pageName);
      // Post 详情内容 wrap in scroll-area + content div
      if (['PostUser','PostContents','PostDescription','PostInfo','PostComments'].includes(key)) {
        lines.push(html);
      } else {
        lines.push(html);
      }
      i++;
    } else {
      // 未知组件：占位
      lines.push(`\n  <!-- [未知组件] ${key} -->`);
      i++;
    }
  }
  return lines.join('\n');
}

// ── 滚动区包装（内容详情页需要 scroll-area + content 包装）───────
function wrapScrollArea(pageName, contentHtml, scrollH) {
  if (pageName === '02 内容详情页') {
    return `
  <div class="scroll-area">
    <div class="content">
${contentHtml}
    </div>
  </div>`;
  }
  return contentHtml;
}

// ── 计算滚动区高度 ────────────────────────────────────────────────
function calcScrollH(keys) {
  let fixed = 0;
  keys.forEach(k => { fixed += (HEIGHTS[k] || 0); });
  return Math.max(200, 844 - fixed);
}

// ── 页面专属 CSS ──────────────────────────────────────────────────
function pageCss(pageName, scrollH) {
  const base = `.scroll-area { height: ${scrollH}px; }`;

  if (pageName === '01 首页 Feed') return `${base}
.search-bar-row { background:var(--bg-1); padding:var(--spacing-normal) var(--spacing-large); border-bottom:.5px solid var(--border-2); flex-shrink:0; }
.search-bar-row .search-bar { flex:none; margin:0; width:100%; }
.feed-dual { column-count:2; column-gap:var(--spacing-normal); padding:var(--spacing-normal); }
.feed-card { background:var(--bg-1); border-radius:var(--radius-normal); overflow:hidden; cursor:pointer; break-inside:avoid; display:inline-block; width:100%; margin-bottom:var(--spacing-normal); }
.card-img { width:100%; position:relative; overflow:hidden; border-radius:var(--radius-normal) var(--radius-normal) 0 0; }
.img-placeholder { width:100%; display:flex; align-items:center; justify-content:center; font-size:28px; }
.card-img-tags { position:absolute; top:var(--spacing-small); left:var(--spacing-small); display:flex; gap:var(--spacing-mini); }
.img-tag { height:15px; padding:0 var(--spacing-small); border-radius:var(--radius-mini); font-size:10px; font-weight:700; display:flex; align-items:center; }
.img-tag.primary { background:var(--primary-tag-solid-bg); color:var(--primary-tag-solid-color); }
.img-tag.trade   { background:var(--trade-tag-solid-bg);   color:var(--trade-tag-solid-color); }
.video-icon { position:absolute; top:var(--spacing-small); right:var(--spacing-small); width:24px; height:24px; display:flex; align-items:center; justify-content:center; }
.card-content { padding:var(--spacing-small) var(--spacing-small) var(--spacing-mini); }
.card-title { font-size:12px; line-height:18px; color:var(--text-1); display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.card-user { display:flex; align-items:center; justify-content:space-between; padding:var(--spacing-mini) var(--spacing-small) var(--spacing-small); }
.user-left { display:flex; align-items:center; gap:var(--spacing-mini); }
.user-avatar-sm { width:16px; height:16px; border-radius:50%; background:linear-gradient(135deg,var(--primary-1),var(--primary-5)); flex-shrink:0; }
.user-name { font-size:11px; line-height:13px; color:var(--text-3); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:80px; }
.user-like { display:flex; align-items:center; gap:2px; font-size:11px; font-weight:500; font-family:'Roboto','PingFang SC',sans-serif; color:var(--icon-3); }
.user-like.liked { color:var(--error-solid-bg); }
/* Islands */
.islands-header-bar { display:flex; align-items:center; justify-content:space-between; padding:12px 16px 8px; background:var(--bg-1); }
.islands-title { font-size:16px; font-weight:500; color:var(--text-1); }
.islands-more { font-size:12px; color:var(--primary-color); display:flex; align-items:center; gap:2px; }
.islands-pin-row { display:flex; gap:12px; padding:4px 16px 12px; overflow-x:auto; scrollbar-width:none; background:var(--bg-1); }
.islands-pin-row::-webkit-scrollbar { display:none; }
.islands-pin-item { display:flex; flex-direction:column; align-items:center; gap:4px; flex-shrink:0; }
.islands-pin-avatar { width:52px; height:52px; border-radius:50%; background:linear-gradient(135deg,var(--primary-1),var(--primary-3)); display:flex; align-items:center; justify-content:center; font-size:24px; }
.islands-pin-name { font-size:11px; color:var(--text-2); white-space:nowrap; }
.islands-grid-row { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; padding:4px 16px 12px; background:var(--bg-1); }
.islands-grid-item { display:flex; flex-direction:column; align-items:center; gap:4px; }
.islands-grid-avatar { width:48px; height:48px; border-radius:12px; background:linear-gradient(135deg,var(--primary-1),var(--primary-3)); display:flex; align-items:center; justify-content:center; font-size:22px; }
.islands-grid-name { font-size:11px; font-weight:500; color:var(--text-1); }
.islands-grid-meta { font-size:10px; color:var(--text-3); }
.islands-slide-row { display:flex; gap:8px; padding:4px 16px 12px; overflow-x:auto; scrollbar-width:none; background:var(--bg-1); }
.islands-slide-row::-webkit-scrollbar { display:none; }
.islands-slide-card { width:120px; flex-shrink:0; border-radius:var(--radius-normal); overflow:hidden; background:var(--bg-2); }
.islands-slide-cover { height:80px; display:flex; align-items:center; justify-content:center; font-size:32px; background:linear-gradient(135deg,var(--primary-1),var(--primary-2)); }
.islands-slide-name { font-size:12px; font-weight:500; color:var(--text-1); padding:6px 8px 2px; }
.islands-slide-desc { font-size:11px; color:var(--text-3); padding:0 8px 8px; }
.islands-quick-entry { background:var(--bg-1); padding:8px 16px 12px; }
.islands-quick-title { font-size:14px; font-weight:500; color:var(--text-1); margin-bottom:8px; }
.islands-quick-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:6px; }
.islands-quick-item { display:flex; align-items:center; justify-content:center; height:32px; border-radius:var(--radius-small); background:var(--primary-1); font-size:11px; color:var(--primary-color); font-weight:500; }
.islands-discovery-header-bar { display:flex; align-items:center; justify-content:space-between; padding:12px 16px 8px; background:var(--bg-1); border-top:8px solid var(--bg-2); }
.islands-discovery-list { background:var(--bg-1); padding:0 16px; }
.islands-discovery-item { display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:.5px solid var(--border-1); }
.islands-discovery-item:last-child { border-bottom:none; }
.islands-discovery-avatar { width:44px; height:44px; border-radius:50%; background:linear-gradient(135deg,var(--primary-1),var(--primary-3)); display:flex; align-items:center; justify-content:center; font-size:20px; flex-shrink:0; }
.islands-discovery-info { flex:1; min-width:0; }
.islands-discovery-name { font-size:14px; font-weight:500; color:var(--text-1); }
.islands-discovery-meta { font-size:12px; color:var(--text-3); margin-top:2px; }
.islands-join-btn { height:28px; padding:0 12px; border-radius:var(--radius-normal); border:1px solid var(--primary-bt-border); background:transparent; color:var(--primary-bt-color); font-size:12px; font-weight:500; cursor:pointer; flex-shrink:0; }`;

  if (pageName === '02 内容详情页') return `${base}
.phone { background:var(--bg-1); }
.content { padding-bottom:83px; }
.post-header { height:88px; background:var(--bg-1); display:flex; align-items:flex-end; padding:0 var(--spacing-large); justify-content:space-between; flex-shrink:0; }
.post-header-inner { width:100%; height:44px; display:flex; align-items:center; justify-content:space-between; border-bottom:.5px solid var(--border-1); }
.post-header .navbar-left, .post-header .navbar-right { display:flex; align-items:center; gap:var(--spacing-small); }
.post-user { display:flex; align-items:center; padding:var(--spacing-normal) var(--spacing-large); gap:var(--spacing-normal); background:var(--bg-1); }
.post-user .avatar { width:40px; height:40px; border-radius:50%; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:18px; color:white; font-weight:600; background:linear-gradient(135deg,#C7B8FF,#7C66FF); }
.post-user .author-info { flex:1; min-width:0; }
.post-user .author-name { font-size:14px; font-weight:500; color:var(--text-1); line-height:22px; }
.post-user .author-meta { font-size:12px; color:var(--text-3); line-height:18px; }
.post-user .btn-follow { height:28px; padding:0 12px; flex-shrink:0; border-radius:var(--radius-normal); border:1px solid var(--primary-bt-border); background:transparent; color:var(--primary-bt-color); font-size:12px; font-weight:500; cursor:pointer; }
.post-contents { width:100%; aspect-ratio:4/3; background:#C7B8FF; display:flex; align-items:center; justify-content:center; font-size:48px; flex-shrink:0; }
.post-description { padding:var(--spacing-large); background:var(--bg-1); }
.post-title { font-size:20px; font-weight:500; color:var(--text-1); line-height:26px; margin-bottom:var(--spacing-normal); }
.post-text { font-size:16px; color:var(--text-2); line-height:24px; }
.post-text p { margin-bottom:var(--spacing-normal); }
.tags-row { display:flex; flex-wrap:wrap; gap:var(--spacing-small); margin-top:var(--spacing-medium); }
.tag { height:20px; padding:0 var(--spacing-small); border-radius:var(--radius-small); background:var(--primary-1); color:var(--primary-color); font-size:11px; font-weight:500; text-decoration:none; display:inline-flex; align-items:center; }
.post-info { padding:0 var(--spacing-large) var(--spacing-large); display:flex; align-items:center; gap:var(--spacing-large); border-bottom:8px solid var(--bg-2); }
.post-info .stat-item { display:flex; align-items:center; gap:var(--spacing-small); font-size:12px; font-weight:500; font-family:'Roboto','PingFang SC',sans-serif; color:var(--text-3); }
.post-info .stat-item i { font-size:16px; color:var(--icon-3); }
.post-comments { background:var(--bg-1); }
.comments-header { padding:var(--spacing-large) var(--spacing-large) var(--spacing-normal); display:flex; align-items:center; justify-content:space-between; }
.comments-title { font-size:16px; font-weight:500; color:var(--text-1); }
.comments-meta { font-size:12px; color:var(--text-3); }
.comment-list { padding:0 var(--spacing-large); }
.comment-item { display:flex; gap:var(--spacing-normal); padding:var(--spacing-normal) 0; border-bottom:.5px solid var(--border-1); }
.comment-item:last-child { border-bottom:none; }
.comment-avatar { width:32px; height:32px; border-radius:50%; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:14px; color:white; font-weight:600; }
.comment-content { flex:1; min-width:0; }
.comment-name { font-size:12px; font-weight:500; color:var(--text-2); margin-bottom:3px; }
.comment-text { font-size:14px; color:var(--text-1); line-height:22px; }
.comment-footer { display:flex; align-items:center; justify-content:space-between; margin-top:var(--spacing-small); }
.comment-time { font-size:12px; color:var(--text-3); }
.comment-like { display:flex; align-items:center; gap:var(--spacing-mini); font-size:12px; font-weight:500; font-family:'Roboto','PingFang SC',sans-serif; color:var(--text-3); cursor:pointer; }
.view-more { text-align:center; padding:var(--spacing-large); font-size:14px; color:var(--primary-color); cursor:pointer; }
.comment-input { flex:1; height:32px; border-radius:var(--radius-normal); background:var(--bg-2); display:flex; align-items:center; padding:0 var(--spacing-normal); cursor:text; }
.comment-input span { font-size:14px; color:var(--text-3); }
.bottom-actions { display:flex; align-items:center; gap:var(--spacing-large); flex-shrink:0; }
.action-btn { display:flex; flex-direction:column; align-items:center; gap:2px; cursor:pointer; }
.action-btn i { font-size:22px; color:var(--icon-1); }
.action-btn.active i { color:var(--error-5); }
.action-btn.active-star i { color:#FFC107; }
.action-count { font-size:11px; font-weight:500; color:var(--text-3); }`;

  if (pageName === '03 Tag 详情页') return `${base}
.tag-header { background:var(--bg-1); padding:var(--spacing-normal) var(--spacing-large) var(--spacing-large); border-bottom:.5px solid var(--border-2); flex-shrink:0; }
.tag-name { font-size:20px; font-weight:500; color:var(--text-1); margin-bottom:var(--spacing-small); }
.tag-meta { font-size:12px; color:var(--text-3); font-family:'Roboto','PingFang SC',sans-serif; font-weight:500; display:flex; gap:var(--spacing-large); }
.feed-dual { column-count:2; column-gap:var(--spacing-normal); padding:var(--spacing-normal); }
.feed-card { background:var(--bg-1); border-radius:var(--radius-normal); overflow:hidden; cursor:pointer; break-inside:avoid; display:inline-block; width:100%; margin-bottom:var(--spacing-normal); }
.card-img { width:100%; position:relative; overflow:hidden; border-radius:var(--radius-normal) var(--radius-normal) 0 0; }
.img-placeholder { width:100%; display:flex; align-items:center; justify-content:center; font-size:28px; }
.card-img-tags { position:absolute; top:var(--spacing-small); left:var(--spacing-small); display:flex; gap:var(--spacing-mini); }
.img-tag { height:15px; padding:0 var(--spacing-small); border-radius:var(--radius-mini); font-size:10px; font-weight:700; display:flex; align-items:center; }
.img-tag.primary { background:var(--primary-tag-solid-bg); color:var(--primary-tag-solid-color); }
.img-tag.trade   { background:var(--trade-tag-solid-bg);   color:var(--trade-tag-solid-color); }
.card-content { padding:var(--spacing-small) var(--spacing-small) var(--spacing-mini); }
.card-title { font-size:12px; line-height:18px; color:var(--text-1); display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.card-user { display:flex; align-items:center; justify-content:space-between; padding:var(--spacing-mini) var(--spacing-small) var(--spacing-small); }
.user-left { display:flex; align-items:center; gap:var(--spacing-mini); }
.user-avatar-sm { width:16px; height:16px; border-radius:50%; background:linear-gradient(135deg,var(--primary-1),var(--primary-5)); flex-shrink:0; }
.user-name { font-size:11px; color:var(--text-3); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:80px; }
.user-like { display:flex; align-items:center; gap:2px; font-size:11px; font-weight:500; font-family:'Roboto','PingFang SC',sans-serif; color:var(--icon-3); }`;

  return base;
}

// ── 页面专属 JS ──────────────────────────────────────────────────
function pageScripts(pageName) {
  const common = `
function toggleTheme() {
  const html = document.documentElement, btn = document.querySelector('.ctrl-btn');
  if (html.dataset.theme === 'light') { html.dataset.theme = 'dark'; btn.textContent = '☀️ 亮色'; }
  else { html.dataset.theme = 'light'; btn.textContent = '🌙 深色'; }
}
function switchTab(el) {
  document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
}`;

  if (pageName === '01 首页 Feed') return common + `
function openDetail(emoji,c1,c2,title,author,avatarC) {
  const p = new URLSearchParams({emoji,c1,c2,title,author,avatarC:avatarC||c1});
  window.location.href = 'content-detail.html?' + p.toString();
}`;

  if (pageName === '02 内容详情页') return common + `
function toggleLike() {
  const btn = document.getElementById('likeBtn');
  btn.classList.toggle('active');
  btn.querySelector('i').className = btn.classList.contains('active')
    ? 'KurilIcons kuril-community_like_selected_filled'
    : 'KurilIcons kuril-community_like_normal';
}
function toggleStar() {
  const btn = document.getElementById('starBtn');
  btn.classList.toggle('active-star');
  const icon = document.getElementById('starIcon');
  if (btn.classList.contains('active-star')) { icon.className='KurilIcons kuril-have_selected'; icon.style.color='#FFC107'; }
  else { icon.className='KurilIcons kuril-collect_normal'; icon.style.color=''; }
}
function openDetail(e,c1,c2,title,author,avatarC){}
(function(){
  const p = new URLSearchParams(window.location.search);
  if (!p.has('emoji')) return;
  const el = document.getElementById('postContents');
  if (el) el.style.background = '#' + (p.get('c1')||'C7B8FF');
  const em = document.getElementById('coverEmoji');
  if (em) em.textContent = p.get('emoji');
  const title = p.get('title');
  if (title) { const t=document.getElementById('postTitle'); if(t) t.textContent=title; }
  const author = p.get('author');
  if (author) {
    const nameEl=document.getElementById('authorName'); if(nameEl) nameEl.textContent=author;
    const avatarEl=document.getElementById('authorAvatar');
    if(avatarEl){ avatarEl.textContent=author.charAt(0); avatarEl.style.background='linear-gradient(135deg,#'+(p.get('avatarC')||p.get('c1')||'C7B8FF')+'，#'+(p.get('c2')||'7C66FF')+')'; }
  }
})();`;

  if (pageName === '03 Tag 详情页') return common + `
function openDetail(e,c1,c2,title,author,avatarC){
  const p=new URLSearchParams({emoji:e,c1,c2,title,author,avatarC:avatarC||c1});
  window.location.href='content-detail.html?'+p.toString();
}
(function(){
  const tag=new URLSearchParams(window.location.search).get('tag')||'Figma';
  const display='# '+tag;
  const nav=document.getElementById('navTitle'); if(nav) nav.textContent=display;
  const tn=document.getElementById('tagName'); if(tn) tn.textContent=display;
  document.title=display+' · Tag 详情页 · 千岛';
})();`;

  return common;
}

// ── flow chart ────────────────────────────────────────────────────
function flowChart(activeIdx) {
  const nodes = [
    {icon:'🏠', label:'首页 Feed',   href:'home-feed.html'},
    {icon:'📄', label:'内容详情页', href:'content-detail.html'},
    {icon:'🏷️', label:'Tag 详情页', href:'tag-detail.html?tag=Figma'},
  ];
  return `
  <div class="flow-chart">
    ${nodes.map((n,i) => `
    <a class="flow-node${i===activeIdx?' active':''}" href="${n.href}">
      <span class="node-icon">${n.icon}</span>
      <span class="node-label">${n.label}</span>
    </a>${i < nodes.length-1 ? `
    <div class="flow-edge"><span class="flow-edge-label">${i===0?'点击卡片':'点击 Tag'}</span></div>` : ''}`).join('')}
  </div>`;
}

// ── 组装完整 HTML ─────────────────────────────────────────────────
function buildPage(page) {
  const meta = PAGE_META[page.name];
  if (!meta) { console.warn('未知页面:', page.name); return null; }

  const keys = page.components.map(c => c.key);

  // 分类
  const topKeys     = keys.filter(k => FIXED_TOP.has(k));
  const bottomKeys  = keys.filter(k => FIXED_BOTTOM.has(k));
  const contentKeys = keys.filter(k => !FIXED_TOP.has(k) && !FIXED_BOTTOM.has(k));

  const scrollH = calcScrollH(keys);
  const css     = pageCss(page.name, scrollH);

  // 渲染各区
  const topHtml     = topKeys.map(k => TPL[k] ? TPL[k](page.name) : `<!-- ${k} -->`).join('');
  const contentHtml = renderContentComponents(contentKeys, page.name);
  const bottomHtml  = bottomKeys.map(k => TPL[k] ? TPL[k](page.name) : `<!-- ${k} -->`).join('');

  const innerContent = page.name === '02 内容详情页'
    ? `  <div class="scroll-area">\n    <div class="content">\n${contentHtml}\n    </div>\n  </div>`
    : contentHtml;

  return `<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=390, initial-scale=1.0">
<title>${meta.title}</title>
<link rel="stylesheet" href="https://at.alicdn.com/t/c/font_3550031_uwcy4h4l9a9.css">
<link rel="stylesheet" href="styles.css">
<style>
${css}
</style>
</head>
<body>

<div class="demo-ctrl">
  <button class="ctrl-btn" onclick="toggleTheme()">🌙 深色</button>
</div>

<div class="prototype-layout">
<div class="phone">
${topHtml}
${innerContent}
${bottomHtml}
</div><!-- .phone -->
${flowChart(meta.flowIdx)}
</div><!-- .prototype-layout -->

<script>
${pageScripts(page.name)}
</script>
</body>
</html>`;
}

// ── 主流程 ───────────────────────────────────────────────────────
let built = 0;
config.pages.forEach(page => {
  const meta = PAGE_META[page.name];
  if (!meta) return;
  const html = buildPage(page);
  if (!html) return;
  const outPath = path.join(outDir, meta.file);
  fs.writeFileSync(outPath, html, 'utf-8');
  console.log(`✅ ${page.name} → 04 demos/${meta.file}  (${page.components.length} 个组件)`);
  built++;
});
console.log(`\n共生成 ${built} 个页面。刷新浏览器即可查看。\n`);
