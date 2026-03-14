#!/bin/bash
# 千岛 Demo 预览 · 自动打开 / 刷新
# 用法: ./preview.sh [04 demos/{需求文件夹}/{页面}.html]
# 适用范围：04 demos/ 静态 Demo（CSS 已内联，file:// 无 CORS 问题）
# ⚠️  design-system-index.html 需通过 HTTP server：python3 -m http.server 8081 --directory .
#
# 无参数时：自动打开 04 demos/ 下最新的 HTML

cd "$(dirname "$0")"

if [ -n "$1" ]; then
  PAGE="$1"
else
  PAGE=$(find '04 demos' -maxdepth 2 -name '*.html' 2>/dev/null | sort | tail -1)
  if [ -z "$PAGE" ]; then
    echo "❌ 04 demos/ 下暂无 HTML，用法: ./preview.sh <路径>"
    exit 1
  fi
fi

FULL_PATH="$(pwd)/$PAGE"
FILE_URL="file://$FULL_PATH"
FILENAME="$(basename "$PAGE")"

# ── 在 Chrome 里找并刷新 ─────────────────────────────────────
refresh_chrome() {
  osascript 2>/dev/null <<EOF
tell application "Google Chrome"
  if not running then return "not_running"
  repeat with w in windows
    repeat with t in tabs of w
      if URL of t contains "$FILENAME" then
        reload t
        set index of w to 1
        activate
        return "refreshed"
      end if
    end repeat
  end repeat
  return "not_found"
end tell
EOF
}

# ── 在 Safari 里找并刷新 ─────────────────────────────────────
refresh_safari() {
  osascript 2>/dev/null <<EOF
tell application "Safari"
  if not running then return "not_running"
  repeat with w in windows
    repeat with t in tabs of w
      if URL of t contains "$FILENAME" then
        do JavaScript "location.reload()" in t
        set current tab of w to t
        activate
        return "refreshed"
      end if
    end repeat
  end repeat
  return "not_found"
end tell
EOF
}

RESULT=$(refresh_chrome)
if [ "$RESULT" != "refreshed" ]; then
  RESULT=$(refresh_safari)
fi

if [ "$RESULT" = "refreshed" ]; then
  echo "🔄 已刷新: $FILENAME"
else
  open "$FILE_URL"
  echo "🚀 已打开: $FILE_URL"
fi
