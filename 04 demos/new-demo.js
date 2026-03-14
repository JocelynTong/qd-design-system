/**
 * 千岛新需求初始化
 * 用法: node '04 demos/new-demo.js' <需求文件夹名>
 * 例如: node '04 demos/new-demo.js' community-feed-v1
 * 实际创建: 04 demos/20260312-community-feed-v1/
 *
 * 执行内容：
 *   1. 在 04 demos/ 下创建需求文件夹
 *   2. 从 03 business/_styles.css 复制冻结当前 token 版本
 *   3. 生成空白 figma-config.json 模板
 *   4. 显示候选池待决策数量
 */

const fs = require('fs');
const path = require('path');

const rawName = process.argv[2];
if (!rawName) {
  console.error('❌ 请指定需求文件夹名，例如: node new-demo.js community-feed-v1');
  process.exit(1);
}

const today = new Date();
const datePrefix = today.getFullYear().toString()
  + String(today.getMonth() + 1).padStart(2, '0')
  + String(today.getDate()).padStart(2, '0');
const name = `${datePrefix}-${rawName}`;

const root = path.join(__dirname, '..');
const targetDir = path.join(__dirname, name);

if (fs.existsSync(targetDir)) {
  console.error(`❌ 文件夹已存在: 04 demos/${name}`);
  process.exit(1);
}

// 1. 创建文件夹
fs.mkdirSync(targetDir);

// 2. 拼接三层 _styles.css，冻结当前版本（strip @import，按依赖顺序合并）
function readCss(filePath) {
  return fs.readFileSync(filePath, 'utf-8')
    .split('\n')
    .filter(line => !line.trim().startsWith('@import'))
    .join('\n');
}
const css = [
  readCss(path.join(root, '01 tokens', '_styles.css')),
  readCss(path.join(root, '02 components', '_styles.css')),
  readCss(path.join(root, '03 business', '_styles.css')),
].join('\n');
fs.writeFileSync(path.join(targetDir, 'styles.css'), css);

// 3. 生成 figma-config.json 模板
const config = { name, pages: [], connections: [] };
fs.writeFileSync(
  path.join(targetDir, 'figma-config.json'),
  JSON.stringify(config, null, 2)
);

console.log(`\n✅ 需求文件夹已创建: 04 demos/${name}/\n`);
console.log('  📁 styles.css        ← 当前 token 版本已冻结（来自 03 business/_styles.css）');
console.log('  📄 figma-config.json ← 页面流转模板，待填写');
console.log('\n接下来：');
console.log(`  1. 从 03 business/{module}/ 复制对应页面 HTML 到 04 demos/${name}/`);
console.log(`  2. 按需求改动 HTML`);
console.log(`  3. 填写 figma-config.json 的 pages 和 connections\n`);

// 4. 检查候选池
const candidatesPath = path.join(root, '_candidates.md');
if (fs.existsSync(candidatesPath)) {
  const content = fs.readFileSync(candidatesPath, 'utf-8');
  const highFreqRows = (content.match(/## 🔴[\s\S]*?(?=## 🟡|$)/)?.[0] || '')
    .split('\n').filter(l => l.startsWith('|') && !l.includes('---') && !l.includes('元素描述'));
  const lowFreqRows = (content.match(/## 🟡[\s\S]*/)?.[0] || '')
    .split('\n').filter(l => l.startsWith('|') && !l.includes('---') && !l.includes('元素描述'));

  if (highFreqRows.length > 0) {
    console.log(`⚠️  候选池有 ${highFreqRows.length} 项需要决策，${lowFreqRows.length} 项观察中`);
    console.log('   查看详情: _candidates.md\n');
  }
}
