/**
 * 千岛设计系统 · 飞书候选池周报
 * 用法: npm run notify-feishu
 * 读取 business/_candidates.md → 格式化飞书卡片 → POST webhook
 *
 * 需要环境变量：FEISHU_WEBHOOK
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const crypto = require('crypto');
const { URL } = require('url');

const root = path.join(__dirname, '..');
const candidatesPath = path.join(root, 'business', '_candidates.md');
const webhook = process.env.FEISHU_WEBHOOK;

if (!webhook) {
  console.error('❌ 缺少环境变量 FEISHU_WEBHOOK');
  process.exit(1);
}

// ── 解析 _candidates.md 里的表格行 ───────────────────────────
function parseTable(content, section) {
  const match = content.match(new RegExp(`## ${section}[\\s\\S]*?(?=## |$)`));
  if (!match) return [];
  return match[0]
    .split('\n')
    .filter(l => l.startsWith('|') && !l.includes('---') && !l.includes('元素描述'))
    .map(l => l.split('|').filter(Boolean).map(s => s.trim()));
}

const content = fs.existsSync(candidatesPath)
  ? fs.readFileSync(candidatesPath, 'utf-8')
  : '';

const highFreq = parseTable(content, '🔴 需要决策（3次以上）');
const lowFreq  = parseTable(content, '🟡 观察中（1-2次）');

// ── 格式化卡片内容 ────────────────────────────────────────────
function formatRows(rows) {
  if (rows.length === 0) return '_暂无_';
  return rows.map(r => `• **${r[0]}** × ${r[2]}次｜最近：${r[3]}`).join('\n');
}

const repoUrl = 'https://github.com/jocelyntong/echo-design-system/blob/main/business/_candidates.md';

const card = {
  msg_type: 'interactive',
  card: {
    config: { wide_screen_mode: true },
    header: {
      title: { content: '🎨 设计系统候选池 · 周报', tag: 'plain_text' },
      template: 'purple'
    },
    elements: [
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**🔴 需要决策（${highFreq.length} 项）**\n${formatRows(highFreq)}`
        }
      },
      { tag: 'hr' },
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**🟡 观察中（${lowFreq.length} 项）**\n${formatRows(lowFreq)}`
        }
      },
      { tag: 'hr' },
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: highFreq.length > 0
            ? `⚠️ 本周有 **${highFreq.length}** 项待拍板，决策三选一：token化 / 业务组件 / 忽略 <at user_id="all"></at>`
            : '✅ 本周无需决策，继续保持'
        }
      },
      {
        tag: 'action',
        actions: [{
          tag: 'button',
          text: { content: '查看完整候选池', tag: 'plain_text' },
          url: repoUrl,
          type: 'primary'
        }]
      }
    ]
  }
};

// ── 飞书签名（如机器人开启了签名校验则必须）────────────────────
function genSign(secret, timestamp) {
  const str = timestamp + '\n' + secret;
  return crypto.createHmac('sha256', str).update('').digest('base64');
}

// ── POST 到飞书 webhook ───────────────────────────────────────
const timestamp = String(Math.floor(Date.now() / 1000));
const webhookSecret = process.env.FEISHU_WEBHOOK_SECRET;

if (webhookSecret) {
  card.sign = genSign(webhookSecret, timestamp);
  card.timestamp = timestamp;
}
const body = JSON.stringify(card);
const url = new URL(webhook);

const req = https.request({
  hostname: url.hostname,
  path: url.pathname + url.search,
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
}, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const json = JSON.parse(data);
    if (json.code === 0) {
      console.log(`✅ 飞书通知发送成功（高频 ${highFreq.length} 项，观察中 ${lowFreq.length} 项）`);
    } else {
      console.error('❌ 飞书返回错误:', json);
      process.exit(1);
    }
  });
});

req.on('error', e => { console.error('❌ 请求失败:', e.message); process.exit(1); });
req.write(body);
req.end();
