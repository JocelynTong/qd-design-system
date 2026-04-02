#!/usr/bin/env node
/**
 * register-figma-webhook.js
 *
 * 注册 Figma webhook，指向 GitHub Actions workflow_dispatch
 *
 * 用法：
 *   FIGMA_TOKEN=xxx node scripts/register-figma-webhook.js
 *
 * 注意：Figma webhook 必须 POST 到 GitHub API，
 * 需要在 Figma Settings > Webhooks 页面手动创建，或通过 API 创建。
 * 此脚本用于查看当前 webhook 状态和测试触发。
 */

const fs = require('fs');
const path = require('path');

// ===== 配置 =====
const TOKEN = process.env.FIGMA_TOKEN;
const TEAM_ID = process.env.FIGMA_TEAM_ID; // 可选，若账号属于多个 team 需要指定

// GitHub 信息（替换为实际值）
const GITHUB_OWNER = 'jocelyntong';       // 替换为你的 GitHub 用户名
const GITHUB_REPO = 'echo-design-system';  // 替换为你的仓库名
const WORKFLOW_ID = 'figma-sync.yml';      // workflow 文件名

// Figma 文件 key
const FILE_KEY = process.env.FIGMA_FILE_KEY || 'HjpmfUPwU7HGMRj9X80TAY';

// ===== API 工具 =====
async function figmaGet(path, options = {}) {
  const res = await fetch(`https://api.figma.com/v1${path}`, {
    headers: { 'X-Figma-Token': TOKEN },
    ...options
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Figma API error: ${res.status} ${err}`);
  }
  return res.json();
}

async function figmaPost(path, body) {
  return figmaGet(path, {
    method: 'POST',
    body: JSON.stringify(body)
  });
}

// ===== 查看当前 webhooks =====
async function listWebhooks() {
  console.log('📋 当前注册的 Webhooks:');
  const endpoint = TEAM_ID
    ? `/v1/teams/${TEAM_ID}/webhooks`
    : `/v1/webhooks`;

  try {
    const data = await figmaGet(endpoint);
    if (data.webhooks && data.webhooks.length > 0) {
      data.webhooks.forEach(wh => {
        console.log(`  - ID: ${wh.id}`);
        console.log(`    URL: ${wh.endpoint}`);
        console.log(`    File: ${wh.file_key}`);
        console.log(`    Events: ${wh.event_types.join(', ')}`);
        console.log();
      });
    } else {
      console.log('  暂无 webhook');
    }
    return data.webhooks || [];
  } catch (err) {
    console.log('  无法获取 webhook 列表:', err.message);
    return [];
  }
}

// ===== 手动触发 GitHub workflow（测试用）=====
async function triggerGitHubWorkflow(branch = 'main') {
  console.log(`\n🔄 手动触发 GitHub workflow (branch: ${branch})...`);

  // 注意：此操作需要 GitHub PAT（不是 GITHUB_TOKEN）
  // 在 GitHub Settings > Developer settings > Personal access tokens 生成
  const GITHUB_PAT = process.env.GITHUB_PAT;
  if (!GITHUB_PAT) {
    console.log('❌ 缺少 GITHUB_PAT 环境变量，无法手动触发');
    console.log('   请设置: export GITHUB_PAT=xxx');
    console.log('   或直接在 GitHub Actions 页面手动触发');
    return;
  }

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_ID}/dispatches`;

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Accept': 'application/vnd.github+json',
      'Authorization': `Bearer ${GITHUB_PAT}`,
      'X-GitHub-Api-Version': '2022-11-28'
    },
    body: JSON.stringify({
      ref: branch,
      inputs: {
        component: 'StatusBar'
      }
    })
  });

  if (res.status === 204) {
    console.log('✅ GitHub workflow 已触发');
  } else {
    const err = await res.text();
    console.log(`❌ 触发失败: ${res.status} ${err}`);
  }
}

// ===== 主逻辑 =====
async function main() {
  const action = process.argv[2] || 'list';

  console.log('🔧 Figma Webhook 管理工具\n');
  console.log(`GitHub Target: https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`);
  console.log(`Workflow: ${WORKFLOW_ID}\n`);

  if (action === 'list') {
    await listWebhooks();
  } else if (action === 'trigger') {
    await triggerGitHubWorkflow();
  } else {
    console.log('用法:');
    console.log('  node scripts/register-figma-webhook.js list    # 查看当前 webhooks');
    console.log('  node scripts/register-figma-webhook.js trigger # 手动触发 GitHub workflow');
    console.log();
    console.log('Figma Webhook 注册步骤:');
    console.log('1. 在 Figma Settings > Webhooks 页面创建 webhook');
    console.log('2. URL 格式: https://api.github.com/repos/{owner}/{repo}/actions/workflows/figma-sync.yml/dispatches');
    console.log('3. Events 选择: "Push to file"');
    console.log('4. 需要在 request body 中包含 {"ref":"main"} 并用 GitHub PAT 作为 Authorization header');
  }
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
