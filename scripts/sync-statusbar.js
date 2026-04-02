#!/usr/bin/env node
/**
 * sync-statusbar.js
 *
 * CI 同步 StatusBar 组件数据
 * 从 Figma REST API 获取数据，写入 JSON 文件
 *
 * 用法：
 *   FIGMA_TOKEN=xxx FIGMA_FILE_KEY=xxx node scripts/sync-statusbar.js
 */

const fs = require('fs');
const path = require('path');

// ===== 配置 =====
const TOKEN = process.env.FIGMA_TOKEN;
const FILE_KEY = process.env.FIGMA_FILE_KEY || 'HjpmfUPwU7HGMRj9X80TAY';
const OUTPUT_DIR = path.join(__dirname, '..', '02 components');

// StatusBar COMPONENT_SET node id（在 01.00 Status Bar canvas 下）
const STATUS_BAR_PAGE_ID = '27385:288888';

// ===== API 工具 =====
async function figmaGet(path) {
  const res = await fetch(`https://api.figma.com/v1/files/${FILE_KEY}/nodes?ids=${path}`, {
    headers: { 'X-Figma-Token': TOKEN }
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Figma API error: ${res.status} ${err}`);
  }
  return res.json();
}

// ===== 主逻辑 =====
async function main() {
  console.log('🔄 Syncing StatusBar from Figma...');

  // 1. 获取 StatusBar COMPONENT_SET（包含所有 variants）
  const data = await figmaGet(STATUS_BAR_PAGE_ID);
  const compSet = data.nodes[STATUS_BAR_PAGE_ID]?.document;

  if (!compSet) {
    throw new Error(`COMPONENT_SET not found: ${STATUS_BAR_PAGE_ID}`);
  }

  console.log(`📦 Found: ${compSet.name} (${compSet.type})`);

  // 2. 提取 componentPropertyDefinitions
  const definitions = compSet.componentPropertyDefinitions || {};
  console.log('📋 Property definitions:');
  for (const [k, v] of Object.entries(definitions)) {
    console.log(`  ${k}: ${v.type} = ${JSON.stringify(v.variantOptions || v.defaultValue)}`);
  }

  // 3. 获取所有 child components（每个 variant 一个）
  const childIds = compSet.children?.map(c => c.id).join(',') || [];
  console.log(`\n🔍 Found ${compSet.children?.length || 0} variants`);

  if (childIds) {
    const variantsData = await figmaGet(childIds);

    const variants = {};
    for (const [id, nodeData] of Object.entries(variantsData.nodes)) {
      const doc = nodeData.document;
      if (!doc) continue;

      console.log(`\n📄 Variant: ${doc.name} (${doc.type})`);

      // 提取 INSTANCE 数据
      if (doc.type === 'COMPONENT') {
        const key = doc.components?.[doc.id]?.key;
        const instanceData = {
          id: doc.id,
          type: doc.type,
          name: doc.name,
          componentId: key,
          componentProperties: {},
          absoluteBoundingBox: doc.absoluteBoundingBox,
          layoutMode: doc.layoutMode,
          fills: doc.fills,
          strokes: doc.strokes,
          effects: doc.effects,
          children: doc.children?.map(child => simplifyNode(child))
        };

        // 从 children 提取 componentProperties
        // Figma 里 INSTANCE 的 componentProperties 存在自身，不在 children
        if (doc.componentProperties) {
          instanceData.componentProperties = doc.componentProperties;
        }

        // 从 INSTANCE name 解析 variant key 和 componentProperties
        const vk = parseVariantKey(doc.name, definitions);
        instanceData.componentProperties = parseComponentProperties(doc.name, definitions);
        variants[vk] = instanceData;
      }
    }

    // 4. 组装输出
    const output = {
      id: compSet.id,
      type: compSet.type,
      name: compSet.name,
      componentPropertyDefinitions: definitions,
      variants: variants
    };

    // 5. 写入文件（覆盖原文件，CI 检测变更并 commit）
    const outputPath = path.join(OUTPUT_DIR, '01.00 Status Bar.json');
    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2), 'utf-8');
    console.log(`\n✅ Written to: ${outputPath}`);
  }

  console.log('\n🎉 Sync complete!');
}

// ===== 简化节点（只保留必要字段）=====
function simplifyNode(node) {
  const simplified = {
    id: node.id,
    type: node.type,
    name: node.name
  };

  // 布局属性
  if (node.absoluteBoundingBox) {
    simplified.absoluteBoundingBox = node.absoluteBoundingBox;
  }
  if (node.layoutMode) {
    simplified.layoutMode = node.layoutMode;
  }
  if (node.itemSpacing !== undefined) {
    simplified.itemSpacing = node.itemSpacing;
  }

  // 样式属性
  if (node.fills) simplified.fills = node.fills;
  if (node.strokes) simplified.strokes = node.strokes;
  if (node.effects) simplified.effects = node.effects;

  // 文本内容
  if (node.characters) {
    simplified.characters = node.characters;
  }

  // 组件属性
  if (node.componentProperties) {
    simplified.componentProperties = node.componentProperties;
  }

  // 递归处理 children
  if (node.children && node.children.length > 0) {
    simplified.children = node.children.map(simplifyNode);
  }

  return simplified;
}

// ===== 根据 INSTANCE name 解析 variant key =====
function parseVariantKey(name, definitions) {
  // name 格式: "Color=White, Type=iPhone14pro"
  if (!name) return 'default';

  const parts = [];
  const keys = Object.keys(definitions).sort();

  for (const key of keys) {
    // 正则匹配 key=value
    const regex = new RegExp(`${key}=([^,]+)`);
    const match = name.match(regex);
    if (match) {
      parts.push(match[1]);
    }
  }

  return parts.length > 0 ? parts.join('_') : 'default';
}

// ===== 解析 INSTANCE name 获取 componentProperties =====
function parseComponentProperties(name, definitions) {
  const props = {};
  if (!name) return props;

  const keys = Object.keys(definitions).sort();
  for (const key of keys) {
    const regex = new RegExp(`${key}=([^,]+)`);
    const match = name.match(regex);
    if (match) {
      const def = definitions[key];
      props[key] = {
        type: def.type,
        value: match[1]
      };
    }
  }

  return props;
}

// ===== 入口 =====
main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
