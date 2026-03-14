/**
 * 千岛 Figma Sync
 * 运行: node '05 figma-plugin/figma-sync-server.js' <需求文件夹名>
 * 例如: node '05 figma-plugin/figma-sync-server.js' community-default
 *
 * 读取 demos/{需求文件夹}/figma-config.json → 自动复制到剪贴板
 *
 * 更新配置：
 *   在 Figma 里精调 section → 插件「导出选中 Section」→ 粘给 Claude → Claude 更新 figma-config.json
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

try {
  const folder = process.argv[2];
  if (!folder) {
    console.error('❌ 请指定需求文件夹名，例如: node figma-sync-server.js community-default');
    process.exit(1);
  }
  const configPath = path.join(__dirname, '../04 demos', folder, 'figma-config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  const json = JSON.stringify(config);

  // 复制到剪贴板（macOS）
  execSync(`echo '${json.replace(/'/g, "'\\''")}' | pbcopy`);

  console.log('\n✅ JSON 已复制到剪贴板！\n');
  console.log('接下来：');
  console.log('  1. 打开 Figma 插件「千岛建稿助手」');
  console.log('  2. ⌘V 粘贴到输入框');
  console.log('  3. 点「生成页面」\n');

  config.pages.forEach(p => {
    console.log(`  📄 ${p.emoji || ''} ${p.title}（${p.file}）`);
  });
  console.log(`  🔗 ${config.connections.length} 条连线\n`);

} catch (e) {
  console.error('❌ 生成失败:', e.message);
  process.exit(1);
}
