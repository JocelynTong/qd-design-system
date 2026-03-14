/**
 * 千岛建稿助手 · 属性诊断
 * 导入所有组件并打印其真实 componentPropertyDefinitions
 * 跑一次即可，结果用于校对 code.js 里的 setProperties 参数
 */
(async function () {
  var KEYS = {
    NavBar:    'b2b040109a3194d1818e598751582bf685d56551',
    SearchBar: '8b129ca6225476095227df191a7f630654612077',
    Tabs:      '1aa866b3dcf60c27913f6b01a34c0f28f6cae456',
    TabBar:    '58d45fd34a20eb2b8530af131a5291d7fa8782a9',
    BottomBar: '223c9d06ca6d7cecfdc35f41afdd0ae927e39fea',
    FeedPost:  'f0ec27a6b9af0c27581dbd28ccb32ec12087fe8d'
  };

  figma.notify('⏳ 正在导入组件...', { timeout: 10000 });

  try {
    var entries = await Promise.all(
      Object.keys(KEYS).map(function (name) {
        return figma.importComponentByKeyAsync(KEYS[name]).then(function (c) {
          return [name, c];
        });
      })
    );

    entries.forEach(function (entry) {
      var name = entry[0];
      var comp = entry[1];
      var defs = comp.componentPropertyDefinitions;
      console.log('\n=== ' + name + ' (' + comp.name + ') ===');
      Object.keys(defs).forEach(function (propKey) {
        var def = defs[propKey];
        if (def.type === 'VARIANT') {
          console.log('  [VARIANT] ' + propKey + ': ' + def.variantOptions.join(' | ') + '  (default: ' + def.defaultValue + ')');
        } else {
          console.log('  [' + def.type + '] ' + propKey + '  (default: ' + def.defaultValue + ')');
        }
      });
    });

    figma.notify('✅ 诊断完成，查看 Console', { timeout: 4000 });
  } catch (e) {
    figma.notify('❌ ' + e.message, { error: true, timeout: 6000 });
    console.error(e.message);
  }

  figma.closePlugin();
})();
