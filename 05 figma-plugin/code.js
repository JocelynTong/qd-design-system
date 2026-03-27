/**
 * 千岛助手
 *
 * ▶ 导入 Tab
 *   把 Claude 生成的 JSON config 粘贴进来，
 *   一键在当前 Figma 文件里生成带连线的原型帧组。
 *
 * ↑ 导出 Tab（合并后，一个入口通吃两种场景）
 *   在画布中选中任意 Section / Frame / COMPONENT / COMPONENT_SET，点击「导出」：
 *   · 💙/👻 组件实例  → key + variants + CSS（Claude 按 components/*.json & business/*.json 生成 HTML）
 *   · COMPONENT_SET  → 组件定义 key + 各变体 key + CSS
 *   · 自定义节点      → CSS（追加候选池警告）
 */

// ── Key 表（Claude 按需维护，不删已有条目）──────────────────────────────
var KEYS = {
  // 系统组件（UIKit 库）
  StatusBarSolid:  '2f0822c67ed4a4951a09fecb453f76ce7e882cf5',
  StatusBarGhost:  'fca61ad869eda2219a414e1bd3799bfd88245da4',
  NavBar:          '360f770dbdab8921993cf27def796d9fd3d0f172',
  Tabs:            'c9686e38126de8f12027187be1a44b71ec9788bc',
  TabBar:          '58d45fd34a20eb2b8530af131a5291d7fa8782a9',

  // Feed
  FeedCard:        'bc257468a92875667be7ef8502c1014821c5d58a', // 👻 Feed/Post · 2ColumnMobile

  // 社区业务组件（内容详情页）
  PostHeader:      'cb0eab1b81a0a45d20a3bb1bb935dc5a78149dce',
  PostUser:        'b6eac960c5bb3bf9df0d8e79db07f9b16a5dbdf2',
  PostContents:    '0db8b003a07bb39b759da6186f9f3ed2d2ec1bc5', // LargeImage3:4
  PostDescription: '059e26c0dab5204619d673572e4a46f609633fa5',
  PostInfo:        '391fcf6eecd471b9ba66e281bd9ad19e681721d1',
  PostComments:    '5b3fe9d88dd39248b843fb8635dbc642b3d572ff', // Type=Default
  PostActionBar:   '6a884579d0077d98245b801aca063eed54362576', // 01.07 BottomBar 类型=Post

  // 社区业务组件（岛详情页）
  IslandsHeader:          'eecbc6c90b1707359ded719fde7ea758538f1a50',
  IslandsPinCell:         '0ee323d2a0cc150322dd836552a8923f8dbddb4f', // Type=Home
  IslandsPin:             'e0eaba05d0e32d3ea7ef305765499b592ee04777',
  IslandsGrid:            '9c425cfa52d08f39c0bd2470df414befee021d0e',
  IslandsSlide:           '11f0f10369d4947c619c4f74b9d00219f04e32bc',
  IslandsPairQuickEntry:  'ea4a6b55bb1be319da0bae1cea506357e0a39f69', // 数量=3
  IslandsDiscoveryHeader: '8ad2c9f998309ad6cb0bb534d366da4152b6c25d',
  IslandsDiscovery:       '4cdfb97c4bad528e37bd4a4468dc95aa276e297e',

  // 待补充
  HomeIndicator: null,
  SearchBar:     null,
};


// ── Design Token 颜色映射（与 styles.css 保持一致）──────────────────────
var TOKEN_COLORS = {
  'bg-1':              { r: 1,     g: 1,     b: 1     }, // #FFFFFF
  'bg-2':              { r: 0.969, g: 0.969, b: 0.976 }, // #F7F7F9
  'secondary-solidBg': { r: 0.169, g: 0.149, b: 0.231 }, // #2B263B
  'primary-solidBg':   { r: 0.486, g: 0.400, b: 1.000 }, // #7C66FF
};

function tokenFills(key) {
  var c = key && TOKEN_COLORS[key];
  return c ? [{ type: 'SOLID', color: c }] : null;
}

var COMP_DEFAULT_BG = {
  'StatusBarGhost': 'secondary-solidBg',
};

// ── 组件实例缓存（Build 专用）──────────────────────────────────────────
var comps = {};

// ── 组件命名辅助（导出共用）────────────────────────────────────────────
// 优先取 COMPONENT_SET 名（比单个 variant 名更具可读性）
function getCanonicalName(mc) {
  return (mc.parent && mc.parent.type === 'COMPONENT_SET')
    ? mc.parent.name
    : mc.name;
}
// 💙 = 系统 UIKit 原子；👻 = 业务分子；两者都是已注册的"已知组件"
function isRegisteredComponent(mc) {
  var name = getCanonicalName(mc);
  return name.startsWith('💙') || name.startsWith('👻');
}

// ── 递归收集选中范围内所有 💙/👻 节点 ────────────────────────────────────
// 规则：遇到 COMPONENT_SET/COMPONENT/INSTANCE 检查前缀，符合则收录，不再深入；
//       遇到 Frame/Group/Section 等容器继续递归，跳过无前缀的包裹层
function collectRegistered(node, results) {
  if (!results) results = [];
  var name = node.name || '';
  if (node.type === 'COMPONENT_SET' || node.type === 'COMPONENT') {
    if (name.startsWith('💙') || name.startsWith('👻')) results.push(node);
    return results; // 不递归进组件内部
  }
  if (node.type === 'INSTANCE') {
    if (node.mainComponent && isRegisteredComponent(node.mainComponent)) results.push(node);
    return results; // 不递归进实例内部
  }
  if ('children' in node) {
    Array.from(node.children).forEach(function(c) { collectRegistered(c, results); });
  }
  return results;
}

// ── 初始化 UI ───────────────────────────────────────────────────────────
figma.showUI(__html__, { width: 380, height: 480 });

// ── 消息路由 ────────────────────────────────────────────────────────────
figma.ui.onmessage = async function(msg) {
  switch (msg.type) {
    case 'export': await handleExport(); break;
    case 'findKeys': await handleFindKeys(msg.keyword, msg.scope); break;
    case 'build':
      try {
        var r = await buildFromConfig(msg.config);
        figma.ui.postMessage({ type: 'buildDone', count: r.count, sectionW: r.sectionW, sectionH: r.sectionH });
      } catch(e) {
        figma.ui.postMessage({ type: 'buildError', message: e.message });
      }
      break;
  }
};


// ════════════════════════════════════════════════════════════════════════
//  导出（合并后的统一入口）
//  选中 Section / Frame（原型文件）或 COMPONENT / COMPONENT_SET（组件库文件），点击导出。
//  对每个节点：
//    · COMPONENT_SET  → 组件定义：key + 各变体 key + CSS
//    · COMPONENT      → 组件定义：key + CSS
//    · INSTANCE(💙/👻)→ 组件实例：ref 名 + master key + variants
//    · INSTANCE(无前缀)→ 未注册实例：同上 + 警告
//    · 其他           → 自定义节点：CSS + 候选池警告
// ════════════════════════════════════════════════════════════════════════
async function handleExport() {
  var sel = figma.currentPage.selection;
  if (!sel || sel.length === 0) {
    figma.ui.postMessage({ type: 'exportError', message: '请先在画布中选中 Section、Frame 或组件' });
    return;
  }

  var target = sel[0];
  var warnings = [];

  // ── 工具函数 ────────────────────────────────────────────────────────

  // 过滤空 CSS 值
  async function getCss(node) {
    try {
      var raw = await node.getCSSAsync();
      var css = {};
      Object.keys(raw).forEach(function(k) {
        if (raw[k] && raw[k] !== 'undefined') css[k] = raw[k];
      });
      return Object.keys(css).length > 0 ? css : null;
    } catch(e) { return null; }
  }

  // 递归提取所有文字内容
  function extractTexts(node, result) {
    if (!result) result = {};
    if (node.type === 'TEXT') result[node.name] = node.characters;
    if ('children' in node) node.children.forEach(function(c) { extractTexts(c, result); });
    return result;
  }

  // 递归导出节点树（用于 generate.py 无 MCP 自动生成 preview_html）
  // 规则：TEXT → 记录 text 内容；INSTANCE → 记录 ref 名 + key，不深入；
  //       其余 → 递归子节点；跳过 invisible；最大深度 8
  async function exportNodeTree(node, depth) {
    if (depth === undefined) depth = 0;
    if (depth > 8) return null;
    if (node.visible === false) return null;

    var entry = { type: node.type };
    var css = await getCss(node);
    if (css) entry.css = css;

    if (node.type === 'TEXT') {
      entry.text = node.characters || '';
      return entry;
    }

    if (node.type === 'INSTANCE' && node.mainComponent) {
      entry.ref = getCanonicalName(node.mainComponent);
      entry.key = node.mainComponent.key;
      return entry;
    }

    if ('children' in node && node.children.length > 0) {
      var children = [];
      for (var ci = 0; ci < node.children.length; ci++) {
        var child = node.children[ci];
        var childEntry = await exportNodeTree(child, depth + 1);
        if (childEntry) children.push(childEntry);
      }
      if (children.length > 0) entry.children = children;
    }
    return entry;
  }

  // 递归收集带 componentPropertyReferences 的子节点（boolean / INSTANCE_SWAP 槽位）
  // 对每个匹配子节点记录：boolProp / swapProp / instanceKey / instanceName / css
  async function collectChildSlots(node) {
    var slots = [];
    async function walk(n) {
      if (!('children' in n)) return;
      for (var i = 0; i < n.children.length; i++) {
        var child = n.children[i];
        var refs = child.componentPropertyReferences || {};
        if (refs.visible || refs.mainComponent) {
          var slot = { name: child.name };
          if (refs.visible) slot.boolProp = refs.visible;
          if (refs.mainComponent && child.type === 'INSTANCE' && child.mainComponent) {
            slot.swapProp     = refs.mainComponent;
            slot.instanceKey  = child.mainComponent.key;
            slot.instanceName = child.mainComponent.name;
          }
          var css = await getCss(child);
          if (css) slot.css = css;
          slots.push(slot);
        }
        // 非实例节点继续递归，实例内部由 Figma 自行管理，不深入
        if (child.type !== 'INSTANCE') await walk(child);
      }
    }
    await walk(node);
    return slots;
  }

  // 处理单个子节点，返回结构化描述
  async function processNode(node) {
    // 解析 componentProperties：分类为 variants/booleans/swaps，
    // 并递归子节点将 INSTANCE_SWAP key 解析为组件名
    function parseComponentProps(node) {
      var cp = node.componentProperties;
      if (!cp || Object.keys(cp).length === 0) return null;

      // 先收集所有 INSTANCE_SWAP 的 key → propName 映射
      var swapKeyToProp = {};
      Object.keys(cp).forEach(function(pn) {
        if (cp[pn].type === 'INSTANCE_SWAP') swapKeyToProp[cp[pn].value] = pn;
      });

      // 递归子节点，按 mainComponent.key 反查 INSTANCE_SWAP 对应的组件名
      var resolvedSwaps = {};
      function walkChildren(n) {
        if (n.type === 'INSTANCE' && n.mainComponent) {
          var k = n.mainComponent.key;
          if (swapKeyToProp[k]) resolvedSwaps[swapKeyToProp[k]] = n.mainComponent.name;
        }
        if ('children' in n) n.children.forEach(walkChildren);
      }
      walkChildren(node);

      var variants = {}, booleans = {}, swaps = {};
      Object.keys(cp).forEach(function(pn) {
        var p = cp[pn];
        if (p.type === 'VARIANT')        variants[pn]  = p.value;
        else if (p.type === 'BOOLEAN')   booleans[pn]  = p.value;
        else if (p.type === 'INSTANCE_SWAP') swaps[pn] = resolvedSwaps[pn] || p.value;
        // TEXT type 已由 extractTexts 覆盖，跳过
      });

      var result = {};
      if (Object.keys(variants).length  > 0) result.variants  = variants;
      if (Object.keys(booleans).length  > 0) result.booleans  = booleans;
      if (Object.keys(swaps).length     > 0) result.swaps     = swaps;
      return Object.keys(result).length > 0 ? result : null;
    }

    // 导出 componentPropertyDefinitions（COMPONENT/COMPONENT_SET 用）
    function exportPropDefs(node) {
      var defs = node.componentPropertyDefinitions;
      if (!defs || Object.keys(defs).length === 0) return null;
      var result = {};
      Object.keys(defs).forEach(function(pn) {
        var d = defs[pn];
        var entry = { type: d.type };
        if (d.variantOptions)        entry.options  = d.variantOptions;
        if (d.defaultValue != null)  entry.default  = d.defaultValue;
        result[pn] = entry;
      });
      return result;
    }

    // Wrapper 检测：直接子节点含 💙/👻 实例 → 输出 component_refs (Format B)
    // Leaf：无注册实例子节点 → 输出 _tree 供 generate.py 转 preview_html
    async function buildComponentRefs(variantNode) {
      if (!('children' in variantNode)) return null;
      var refs = [];
      for (var child of Array.from(variantNode.children)) {
        if (child.type === 'INSTANCE' && child.mainComponent && isRegisteredComponent(child.mainComponent)) {
          var refName = getCanonicalName(child.mainComponent);
          var props = parseComponentProps(child);
          var ref = { cid: refName };
          var cp = child.componentProperties;
          if (cp && Object.keys(cp).length > 0) ref.props = cp;
          refs.push(ref);
        }
      }
      return refs.length > 0 ? refs : null;
    }

    // COMPONENT_SET：组件定义，列出各变体 key + CSS + 属性定义
    if (node.type === 'COMPONENT_SET') {
      var entry = { type: 'component_def', name: node.name, key: node.key };
      var css = await getCss(node);
      if (css) entry.css = css;
      var propDefs = exportPropDefs(node);
      if (propDefs) entry.propertyDefs = propDefs;
      entry.variants = await Promise.all(Array.from(node.children).map(async function(v) {
        var ve = { name: v.name, key: v.key };
        var vc = await getCss(v);
        if (vc) ve.css = vc;
        var crefs = await buildComponentRefs(v);
        if (crefs) {
          ve.component_refs = crefs;
        } else {
          var slots = await collectChildSlots(v);
          if (slots.length > 0) ve.slots = slots;
          var tree = await exportNodeTree(v);
          if (tree && (tree.children || tree.text)) ve._tree = tree;
        }
        return ve;
      }));
      return entry;
    }

    // COMPONENT：单个组件定义
    if (node.type === 'COMPONENT') {
      var entry = { type: 'component_def', name: node.name, key: node.key };
      var css = await getCss(node);
      if (css) entry.css = css;
      var propDefs = exportPropDefs(node);
      if (propDefs) entry.propertyDefs = propDefs;
      var crefs = await buildComponentRefs(node);
      if (crefs) {
        entry.component_refs = crefs;
      } else {
        var slots = await collectChildSlots(node);
        if (slots.length > 0) entry.slots = slots;
        var tree = await exportNodeTree(node);
        if (tree && (tree.children || tree.text)) entry._tree = tree;
      }
      return entry;
    }

    // INSTANCE：组件实例（原型文件里用到的）
    if (node.type === 'INSTANCE' && node.mainComponent) {
      var mc = node.mainComponent;
      var refName = getCanonicalName(mc);
      var entry = { type: 'instance', ref: refName, key: mc.key };
      // 用 componentProperties 代替 variantProperties，覆盖所有属性类型
      var props = parseComponentProps(node);
      if (props) {
        if (props.variants)  entry.variants  = props.variants;
        if (props.booleans)  entry.booleans  = props.booleans;
        if (props.swaps)     entry.swaps     = props.swaps;
      }
      if (!isRegisteredComponent(mc)) {
        warnings.push('⚠️ 实例「' + node.name + '」的主组件「' + refName + '」无 💙/👻 前缀，可能是未注册组件');
      }
      return entry;
    }

    // 其他：自定义节点
    var entry = { type: 'custom', name: node.name };
    var css = await getCss(node);
    if (css) entry.css = css;
    warnings.push('🎨 自定义节点「' + node.name + '」已导出 CSS，建议评估是否注册为正式组件');
    return entry;
  }

  // ── 直接选中 COMPONENT/COMPONENT_SET：原样导出 ──────────────────────────
  if (target.type === 'COMPONENT_SET' || target.type === 'COMPONENT') {
    var result = await processNode(target);
    var output = { pages: [{ name: target.name, nodes: [result] }] };
    if (warnings.length > 0) output.warnings = warnings;
    figma.ui.postMessage({ type: 'exportResult', json: JSON.stringify(output), warnings: warnings });
    return;
  }

  // ── 其他容器（Section / Frame / Group 等）：递归找 💙/👻 节点 ─────────────
  var found = collectRegistered(target);
  if (found.length === 0) {
    figma.ui.postMessage({ type: 'exportError', message: '未找到 💙/👻 前缀的组件，请确认选中了正确区域' });
    return;
  }

  // 按最近 Frame 祖先分组：原型场景自动按页面分组，组件库场景归入 target 本身
  function nearestFrame(node) {
    var p = node.parent;
    while (p && p.id !== target.id) {
      if (p.type === 'FRAME') return p.name;
      p = p.parent;
    }
    return target.name;
  }

  var pageMap = {};
  found.forEach(function(node) {
    var key = nearestFrame(node);
    if (!pageMap[key]) pageMap[key] = [];
    pageMap[key].push(node);
  });

  var pages = await Promise.all(Object.keys(pageMap).map(async function(pageName) {
    var sorted = pageMap[pageName].sort(function(a, b) { return (a.y || 0) - (b.y || 0); });
    var nodes = await Promise.all(sorted.map(processNode));
    return { name: pageName, nodes: nodes };
  }));

  var output = { pages: pages };
  if (warnings.length > 0) output.warnings = warnings;

  figma.ui.postMessage({
    type: 'exportResult',
    json: JSON.stringify(output),
    warnings: warnings,
  });
}


// ════════════════════════════════════════════════════════════════════════
//  🔍 查找 Key（按名字关键词，当前页或全部页面）
// ════════════════════════════════════════════════════════════════════════
async function handleFindKeys(keyword, scope) {
  if (!keyword || !keyword.trim()) {
    figma.ui.postMessage({ type: 'findKeysError', message: '请输入关键词' });
    return;
  }
  var kw = keyword.trim().toLowerCase();
  var pagesToSearch = scope === 'all'
    ? Array.from(figma.root.children)
    : [figma.currentPage];

  var results = [];
  for (var i = 0; i < pagesToSearch.length; i++) {
    var page = pagesToSearch[i];
    try {
      var nodes = page.findAll(function (n) {
        return (n.type === 'COMPONENT' || n.type === 'COMPONENT_SET')
          && n.name.toLowerCase().includes(kw);
      });
      nodes.sort(function (a, b) {
        var ay = a.absoluteBoundingBox ? a.absoluteBoundingBox.y : 0;
        var by = b.absoluteBoundingBox ? b.absoluteBoundingBox.y : 0;
        var ax = a.absoluteBoundingBox ? a.absoluteBoundingBox.x : 0;
        var bx = b.absoluteBoundingBox ? b.absoluteBoundingBox.x : 0;
        if (Math.abs(ay - by) < 10) return ax - bx;
        return ay - by;
      });
      nodes.forEach(function (node) {
        var entry = { page: page.name, name: node.name, type: node.type, key: node.key };
        if (node.type === 'COMPONENT_SET') {
          entry.variants = {};
          node.children.forEach(function (v) { entry.variants[v.name] = v.key; });
        }
        results.push(entry);
      });
    } catch (e) {
      console.warn('跳过页面', page.name, ':', e.message);
    }
  }
  figma.ui.postMessage({ type: 'findKeysResult', results: results, keyword: keyword.trim() });
}


// ════════════════════════════════════════════════════════════════════════
//  ▶ 构建原型帧（从 JSON config 生成 Figma 帧 + Prototype 连线）
// ════════════════════════════════════════════════════════════════════════
async function buildFromConfig(config) {
  figma.notify('⏳ 正在导入组件…', { timeout: 12000 });

  // 并行导入所有有效 key
  await Promise.all(Object.keys(KEYS).map(async function(kn) {
    if (!KEYS[kn]) { comps[kn] = null; return; }
    try {
      comps[kn] = await figma.importComponentByKeyAsync(KEYS[kn]);
    } catch(e) {
      console.warn('⚠️ 跳过 [' + kn + ']:', e.message);
      comps[kn] = null;
    }
  }));

  // 计算放置位置（避开已有内容）
  var startX = 0, startY = 0;
  var snapshot = Array.from(figma.currentPage.children);
  if (snapshot.length > 0) {
    var minX = Infinity, maxBottom = -Infinity;
    snapshot.forEach(function(n) {
      if (typeof n.x === 'number' && n.x < minX) minX = n.x;
      var b = (n.y || 0) + (n.height || 0);
      if (b > maxBottom) maxBottom = b;
    });
    startX = isFinite(minX) ? minX : 0;
    startY = isFinite(maxBottom) ? maxBottom + 200 : 0;
  }

  var W = 375, H = 812;
  var PADDING = 100, GAP = 120;
  var pageCount = config.pages.length;
  var totalW = PADDING * 2 + pageCount * W + (pageCount - 1) * GAP;
  var totalH = PADDING * 2 + H;

  var section = figma.createSection();
  figma.currentPage.appendChild(section);
  section.name = config.name || '从 HTML 导入';
  section.fills = [{ type: 'SOLID', color: { r: 0.929, g: 0.929, b: 0.949 } }];

  // 占位点撑开 section 尺寸
  var tl = figma.createRectangle();
  tl.resize(1, 1); tl.fills = []; tl.locked = true;
  section.appendChild(tl); tl.x = 0; tl.y = 0;

  var br = figma.createRectangle();
  br.resize(1, 1); br.fills = []; br.locked = true;
  section.appendChild(br); br.x = totalW - 1; br.y = totalH - 1;

  var frames = {};
  var x = PADDING;

  config.pages.forEach(function(page) {
    var frame = figma.createFrame();
    frame.name = page.name;
    frame.resize(W, H);
    frame.clipsContent = true;
    frame.fills = tokenFills(page.bg) || [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];
    section.appendChild(frame);
    frame.x = x; frame.y = PADDING;
    x += W + GAP;

    var y = 0;
    page.components.forEach(function(comp) {
      var node = comp.key === '__group' ? makeGroup(comp, W) : make(comp.key, W);
      var bgKey = comp.bg !== undefined ? comp.bg : COMP_DEFAULT_BG[comp.key];
      if (bgKey && bgKey !== 'none') {
        var f = tokenFills(bgKey);
        if (f) node.fills = f;
      }
      frame.appendChild(node);
      node.x = 0; node.y = y;
      y += node.height;
    });

    frames[page.name] = frame;
  });

  // Prototype 跳转（Prototype tab 可见）
  config.connections.forEach(function(conn) {
    var from = frames[conn.from], to = frames[conn.to];
    if (from && to) {
      from.reactions = [{
        trigger: { type: 'ON_CLICK' },
        actions: [{
          type: 'NODE',
          destinationId: to.id,
          navigation: 'NAVIGATE',
          transition: { type: 'SMART_ANIMATE', duration: 0.3, easing: { type: 'EASE_IN_AND_OUT' } },
          preserveScrollPosition: false,
        }],
      }];
    }
  });

  // 可视化连线（Design / Dev Mode 均可见）
  await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
  var PRIMARY = { r: 0.486, g: 0.4, b: 1.0 };

  config.connections.forEach(function(conn) {
    var from = frames[conn.from], to = frames[conn.to];
    if (!from || !to) return;

    var goRight = from.x < to.x;
    var lineY   = from.y + from.height / 2 + (goRight ? -28 : 28);
    var startX2 = goRight ? from.x + from.width : from.x;
    var endX    = goRight ? to.x : to.x + to.width;
    var lineW   = Math.abs(endX - startX2);
    if (lineW <= 0) return;

    var alpha = goRight ? 1.0 : 0.5;

    var line = figma.createRectangle();
    section.appendChild(line);
    line.resize(lineW, 2);
    line.fills = [{ type: 'SOLID', color: PRIMARY }];
    line.opacity = alpha;
    line.x = Math.min(startX2, endX); line.y = lineY - 1;

    var aw = 10, ah = 8;
    var tip = figma.createPolygon();
    section.appendChild(tip);
    tip.pointCount = 3; tip.resize(aw, ah);
    tip.fills = [{ type: 'SOLID', color: PRIMARY }];
    tip.opacity = alpha;
    tip.relativeTransform = goRight
      ? [[0, -1, endX],  [1,  0, lineY - aw / 2]]
      : [[0,  1, endX],  [-1, 0, lineY + aw / 2]];

    if (conn.trigger) {
      var lbl = figma.createText();
      section.appendChild(lbl);
      lbl.fontSize = 10; lbl.characters = conn.trigger;
      lbl.fills = [{ type: 'SOLID', color: PRIMARY }];
      lbl.opacity = alpha;
      var midX = (startX2 + endX) / 2;
      lbl.x = midX - lbl.width / 2;
      lbl.y = goRight ? lineY - 16 : lineY + 6;
    }
  });

  section.resizeWithoutConstraints(totalW, totalH);
  section.x = startX; section.y = startY;
  figma.viewport.scrollAndZoomIntoView([section]);

  return {
    count: config.pages.length,
    sectionW: Math.round(section.width),
    sectionH: Math.round(section.height),
  };
}


// ── 辅助：创建组件实例 ──────────────────────────────────────────────────
function make(name, w) {
  if (!comps[name]) {
    var ph = figma.createRectangle();
    ph.name = '[占位] ' + name;
    ph.resize(w || 375, 44);
    ph.fills = [{ type: 'SOLID', color: { r: 1, g: 0.5, b: 0.5 }, opacity: 0.4 }];
    return ph;
  }
  var node = comps[name].createInstance();
  if (w != null) node.resize(w, node.height);
  return node;
}

// ── 辅助：创建组件组（__group，竖向 Auto Layout 容器）──────────────────
function makeGroup(spec, w) {
  var f = figma.createFrame();
  f.name = '[组]';
  f.resize(w, 100);
  f.layoutMode = 'VERTICAL';
  f.primaryAxisSizingMode = 'AUTO';
  f.counterAxisSizingMode = 'FIXED';
  f.itemSpacing = spec.gap !== undefined ? spec.gap : 8;
  f.paddingTop = 0; f.paddingBottom = 0; f.paddingLeft = 0; f.paddingRight = 0;
  f.fills = tokenFills(spec.bg) || [];
  f.clipsContent = false;
  var r = spec.topRadius !== undefined ? spec.topRadius : 0;
  f.topLeftRadius = r; f.topRightRadius = r;
  f.bottomLeftRadius = 0; f.bottomRightRadius = 0;
  (spec.children || []).forEach(function(child) {
    var node = make(child.key, w);
    f.appendChild(node);
    try { node.layoutSizingHorizontal = 'FILL'; } catch(e) {}
  });
  return f;
}
