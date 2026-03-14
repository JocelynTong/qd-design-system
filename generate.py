#!/usr/bin/env python3
"""
Echo Design System - Token 处理脚本
用法：
  python generate.py             # 生成所有 APP（千岛同时更新 _styles.css）
  python generate.py qiandao     # 只生成千岛（同时更新 _styles.css）
  python generate.py linjie      # 只生成临界
  python generate.py qihuo       # 只生成奇货
"""

import json
import re
import os
import sys
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

APPS = {
    'qiandao':  {'name': '千岛',  'dir': '00 qiandao', 'primitives': 'Primitives-QD.json', 'light': '千岛.tokens.json',  'dark': '千岛暗黑.tokens.json'},
    'qihuo':    {'name': '奇货',  'dir': '01 qihuo',   'primitives': 'Primitives-QH.json', 'light': '奇货.tokens.json',  'dark': None},
    'shangjia': {'name': '商家版', 'dir': '01 qihuo',   'primitives': 'Primitives-QH.json', 'light': '商家版.tokens.json','dark': None},
    'linjie':   {'name': '临界',  'dir': '02 linjie',  'primitives': 'Primitives-LJ.json', 'light': '临界.tokens.json',  'dark': '临界暗黑.tokens.json'},
}

STYLES_CSS  = os.path.join(BASE, '01 tokens', '_styles.css')
DS_HTML     = os.path.join(BASE, '00 design-system-index.html')


# ── Token → CSS 辅助函数 ──────────────────────────────────────────────────────

def camel_to_kebab(s):
    """solidBg → solid-bg"""
    return re.sub(r'([A-Z])', lambda m: '-' + m.group(1).lower(), s)


def token_key_to_var(key):
    """'bg/1' → '--bg-1',  'primary/solidBg' → '--primary-solid-bg'"""
    parts = [camel_to_kebab(p) for p in key.split('/')]
    return '--' + '-'.join(parts)


def color_value(hex_val, alpha):
    """Return CSS color string, or None if unresolved."""
    if not hex_val:
        return None
    if alpha == 1:
        return hex_val
    h = hex_val.lstrip('#')
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = f'{alpha:.4f}'.rstrip('0')
        if a.startswith('0.'):
            a = a[1:]   # .64 not 0.64
        return f'rgba({r},{g},{b},{a})'
    return hex_val


def _inject_block(content, begin_marker, end_marker, data_js):
    """通用：把 data_js 替换到 begin/end 标记之间。"""
    begin_pos = content.find(begin_marker)
    end_pos   = content.find(end_marker)
    if begin_pos == -1 or end_pos == -1:
        return content  # 标记不存在时不修改
    end_line_end = content.find('\n', end_pos) + 1
    new_block = begin_marker + '\n' + data_js + '\n' + end_marker + '\n'
    return content[:begin_pos] + new_block + content[end_line_end:]


def write_components_html():
    """把 02 components/*.json 注入 HTML 的 COMPONENTS_DATA 块。"""
    SKIP_KEYS = {'figma_keys', 'common_icons_quick_ref', 'css_variables'}
    comp_dir = os.path.join(BASE, '02 components')
    if not os.path.isdir(comp_dir):
        return
    import re as _re

    components = {}
    for fn in sorted(os.listdir(comp_dir)):
        if not fn.endswith('.json') or fn.startswith('_'):
            continue
        with open(os.path.join(comp_dir, fn), encoding='utf-8') as f:
            data = json.load(f)
        cid = fn.replace('.json', '').replace(' ', '-').lower()
        light = {k: v for k, v in data.items() if k not in SKIP_KEYS}
        components[cid] = {'_file': fn, **light}

    # 按文件名排序：数字前缀优先
    def sort_key(item):
        m = _re.match(r'^(\d+)', item[0])
        return (0, item[0]) if m else (1, item[0])
    components = dict(sorted(components.items(), key=sort_key))

    data_js = 'var COMPONENTS_DATA=' + json.dumps(components, ensure_ascii=False, separators=(',', ':')) + ';'

    with open(DS_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    content = _inject_block(content,
                             '/* === COMPONENTS DATA BEGIN === */',
                             '/* === COMPONENTS DATA END === */',
                             data_js)

    with open(DS_HTML, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'✓ [组件库] COMPONENTS_DATA 已注入（{len(components)} 个组件）')


def write_font_vars_html():
    """把 typography.json 的 css_variables 注入 HTML <style> 的 FONT VARS 块。"""
    typo_path = os.path.join(BASE, '02 components', 'typography.json')
    if not os.path.exists(typo_path):
        return
    with open(typo_path, encoding='utf-8') as f:
        typo = json.load(f)
    css_vars = typo.get('css_variables', {})
    if not css_vars:
        return
    vars_css = ':root{' + ';'.join(f'{k}:{v}' for k, v in css_vars.items()) + '}'
    with open(DS_HTML, 'r', encoding='utf-8') as f:
        content = f.read()
    content = _inject_block(content,
                             '/* === FONT VARS BEGIN === */',
                             '/* === FONT VARS END === */',
                             vars_css)
    with open(DS_HTML, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✓ [Typography] HTML font vars 已注入（{len(css_vars)} 个变量）')


def write_design_system_html(all_processed):
    """将全部 APP token 数据注入 HTML，使其可双击离线打开。"""
    BEGIN = '/* === AUTO-GENERATED DATA BEGIN === */'
    END   = '/* === AUTO-GENERATED DATA END === */'

    payload = dict(all_processed)
    payload['_generated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    data_js = 'var INJECTED_DATA=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';'

    with open(DS_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    content = _inject_block(content, BEGIN, END, data_js)

    with open(DS_HTML, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'✓ [设计系统] 00 design-system-index.html Token 数据已注入')

    # 同步注入组件数据
    write_components_html()


def write_styles_css(processed, styles_path):
    """Write token CSS vars to 01 tokens/_styles.css (100% auto-generated, full overwrite)."""
    lines = ['/* === AUTO-GENERATED — DO NOT EDIT — run: python generate.py === */\n\n']

    # ── :root (light theme) ──
    lines.append('/* ================================================================\n')
    lines.append('   Design Token Variables · Light Theme (default)\n')
    lines.append('   ================================================================ */\n')
    lines.append(':root {\n')

    for cat, tokens in processed['l2_cats'].items():
        parts = []
        for t in tokens:
            val = color_value(t['hex'], t['alpha'])
            if val:
                parts.append(f"{token_key_to_var(t['key'])}:{val}")
        if parts:
            lines.append(f"  /* ── {cat} ── */\n")
            lines.append('  ' + '; '.join(parts) + ';\n')

    for comp, cats in processed['l3_data'].items():
        for cat, tokens in cats.items():
            parts = []
            for t in tokens:
                val = color_value(t['hex'], t['alpha'])
                if val:
                    parts.append(f"{token_key_to_var(t['key'])}:{val}")
            if parts:
                lines.append(f"  /* ── {comp} tokens ── */\n")
                lines.append('  ' + '; '.join(parts) + ';\n')

    if processed.get('spacing'):
        sp = '; '.join(f'--spacing-{k.lower()}:{v}px' for k, v in processed['spacing'].items())
        lines.append('  /* ── spacing ── */\n')
        lines.append(f'  {sp};\n')

    if processed.get('radius'):
        ra = '; '.join(f'--radius-{k.lower()}:{v}px' for k, v in processed['radius'].items())
        lines.append('  /* ── radius ── */\n')
        lines.append(f'  {ra};\n')

    # ── typography (from 02 components/typography.json) ──
    typo_path = os.path.join(BASE, '02 components', 'typography.json')
    if os.path.exists(typo_path):
        with open(typo_path, encoding='utf-8') as f:
            typo = json.load(f)
        css_vars = typo.get('css_variables', {})
        if css_vars:
            tv = '; '.join(f'{k}:{v}' for k, v in css_vars.items())
            lines.append('  /* ── typography ── */\n')
            lines.append(f'  {tv};\n')

    lines.append('}\n\n')

    # ── [data-theme="dark"] — only tokens that differ from light ──
    dark_parts = []
    for cat, tokens in processed['l2_cats'].items():
        cat_parts = []
        for t in tokens:
            if t.get('darkHex') and (t['darkHex'] != t['hex'] or t['darkAlpha'] != t['alpha']):
                val = color_value(t['darkHex'], t['darkAlpha'])
                if val:
                    cat_parts.append(f"{token_key_to_var(t['key'])}:{val}")
        if cat_parts:
            dark_parts.append(f"  /* ── {cat} ── */")
            dark_parts.append('  ' + '; '.join(cat_parts) + ';')

    for comp, cats in processed['l3_data'].items():
        for cat, tokens in cats.items():
            cat_parts = []
            for t in tokens:
                if t.get('darkHex') and (t['darkHex'] != t['hex'] or t['darkAlpha'] != t['alpha']):
                    val = color_value(t['darkHex'], t['darkAlpha'])
                    if val:
                        cat_parts.append(f"{token_key_to_var(t['key'])}:{val}")
            if cat_parts:
                dark_parts.append(f"  /* ── {comp} tokens ── */")
                dark_parts.append('  ' + '; '.join(cat_parts) + ';')

    if dark_parts:
        lines.append('/* ── Dark Theme Overrides ── */\n')
        lines.append('[data-theme="dark"] {\n')
        lines.append('\n'.join(dark_parts) + '\n')
        lines.append('}\n')

    with open(styles_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f'✓ [千岛] 01 tokens/_styles.css 已更新')


def update_business_module_md():
    """扫描 03 business/**/*.json，更新各模块 _module.md 的组件索引区"""
    import glob

    business_dir = os.path.join(BASE, '03 business')
    if not os.path.exists(business_dir):
        return

    for module_dir in glob.glob(os.path.join(business_dir, '*/')):
        module_name = os.path.basename(module_dir.rstrip('/'))
        module_md = os.path.join(module_dir, '_module.md')

        if not os.path.exists(module_md):
            continue

        # 扫描该模块下的所有组件 JSON（排除 .scene.json）
        components = []
        for json_file in glob.glob(os.path.join(module_dir, '*.json')):
            if json_file.endswith('.scene.json'):
                continue
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    components.append({
                        'file': os.path.basename(json_file),
                        'name': data.get('component', ''),
                        'desc': data.get('description', ''),
                        'key': data.get('figma_key', '')
                    })
            except:
                continue

        # 生成组件索引内容
        if components:
            index_lines = ['<!-- AUTO-GENERATED FROM JSON - DO NOT EDIT -->\n']
            for c in components:
                key_part = f" · key: `{c['key']}`" if c['key'] else ''
                index_lines.append(f"- `{c['file']}` — {c['desc']}{key_part}\n")
            index_lines.append('<!-- END AUTO-GENERATED -->\n')
        else:
            index_lines = [
                '<!-- AUTO-GENERATED FROM JSON - DO NOT EDIT -->\n',
                '_暂无组件 JSON（等待 Figma 插件导出）_\n',
                '<!-- END AUTO-GENERATED -->\n'
            ]

        # 替换 _module.md 里的 AUTO-GENERATED 区域
        with open(module_md, 'r', encoding='utf-8') as f:
            content = f.read()

        begin_marker = '<!-- AUTO-GENERATED FROM JSON - DO NOT EDIT -->'
        end_marker = '<!-- END AUTO-GENERATED -->'

        begin_pos = content.find(begin_marker)
        end_pos = content.find(end_marker)

        if begin_pos != -1 and end_pos != -1:
            end_line_end = content.find('\n', end_pos) + 1
            content = content[:begin_pos] + ''.join(index_lines) + content[end_line_end:]
        else:
            # 如果没有标记区，在 ## 组件索引 后面插入
            insert_pos = content.find('## 组件索引')
            if insert_pos != -1:
                next_line = content.find('\n', insert_pos) + 1
                content = content[:next_line] + '\n' + ''.join(index_lines) + '\n' + content[next_line:]

        with open(module_md, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f'✓ [{module_name}] _module.md 组件索引已更新（{len(components)} 个组件）')


# ── Token 处理核心 ────────────────────────────────────────────────────────────

def flatten_tokens(data, prefix=''):
    result = {}
    for k, v in data.items():
        if k == '$extensions':
            continue
        full_key = f"{prefix}/{k}" if prefix else k
        if isinstance(v, dict):
            if '$type' in v:
                result[full_key] = v
            else:
                result.update(flatten_tokens(v, full_key))
    return result


def resolve_chain(key, sem_flat, prim_flat_d, max_depth=8):
    chain = [key]
    current = key
    visited = set()
    while current not in visited and len(chain) <= max_depth:
        visited.add(current)
        token = sem_flat.get(current) or prim_flat_d.get(current)
        if not token:
            break
        val = token.get('$value', {})
        if isinstance(val, str) and val.startswith('{') and val.endswith('}'):
            ref = val[1:-1].replace('.', '/')
            chain.append(ref)
            current = ref
        elif isinstance(val, dict) and 'hex' in val:
            return val['hex'], val.get('alpha', 1), chain
        elif isinstance(val, (int, float)):
            return val, 1, chain
        else:
            break
    return None, 1, chain


def group_by_prefix(tokens_dict):
    groups = {}
    for k, v in tokens_dict.items():
        if not isinstance(v, dict) or '$type' not in v:
            continue
        parts = k.rsplit('_', 1)
        clean = re.sub(r'_?\d+$', '', k)
        group_key = clean if len(parts) == 2 else k
        val = v.get('$value', {})
        groups.setdefault(group_key, []).append({
            'key': k,
            'hex': val.get('hex', '') if isinstance(val, dict) else '',
            'alpha': val.get('alpha', 1) if isinstance(val, dict) else 1
        })
    return groups


def generate(app_id):
    cfg = APPS[app_id]
    token_dir = os.path.join(BASE, '01 tokens', cfg['dir'])

    with open(os.path.join(token_dir, cfg['primitives']), encoding='utf-8') as f:
        primitives = json.load(f)
    with open(os.path.join(token_dir, cfg['light']), encoding='utf-8') as f:
        light_raw = json.load(f)
    if cfg['dark']:
        with open(os.path.join(token_dir, cfg['dark']), encoding='utf-8') as f:
            dark_raw = json.load(f)
    else:
        dark_raw = light_raw

    prim_flat = flatten_tokens(primitives)
    light_flat = flatten_tokens(light_raw)
    dark_flat = flatten_tokens(dark_raw)

    def pget(key):
        return primitives.get(key) or primitives.get(key.lower()) or {}

    main_groups = group_by_prefix(pget('Main'))
    sem_groups  = group_by_prefix(pget('Semantics'))
    radius  = {k: v.get('$value') for k, v in pget('Radius').items()  if '$type' in v}
    spacing = {k: v.get('$value') for k, v in pget('Spacing').items() if '$type' in v}

    l2_cats = {}
    for cat_key, cat_val in light_raw.items():
        if cat_key == '$extensions' or not isinstance(cat_val, dict):
            continue
        tokens = []
        for tk, tv in cat_val.items():
            if isinstance(tv, dict) and '$type' in tv:
                full_key = f"{cat_key}/{tk}"
                hex_v, alpha, chain = resolve_chain(full_key, light_flat, prim_flat)
                dark_hex, dark_alpha, _ = resolve_chain(full_key, dark_flat, prim_flat)
                tokens.append({'key': full_key, 'name': tk, 'hex': hex_v, 'alpha': alpha,
                                'darkHex': dark_hex, 'darkAlpha': dark_alpha, 'chain': chain})
        if tokens:
            l2_cats[cat_key] = tokens

    l3_data = {}
    for comp in ['bt', 'tag']:
        l3_data[comp] = {}
        for cat_key, cat_val in light_raw.items():
            if cat_key == '$extensions' or not isinstance(cat_val, dict):
                continue
            comp_data = cat_val.get(comp)
            if not comp_data or not isinstance(comp_data, dict):
                continue
            tokens = []
            for tk, tv in comp_data.items():
                if isinstance(tv, dict) and '$type' in tv:
                    full_key = f"{cat_key}/{comp}/{tk}"
                    hex_v, alpha, chain = resolve_chain(full_key, light_flat, prim_flat)
                    dark_hex, dark_alpha, _ = resolve_chain(full_key, dark_flat, prim_flat)
                    tokens.append({'key': full_key, 'name': tk, 'hex': hex_v, 'alpha': alpha,
                                   'darkHex': dark_hex, 'darkAlpha': dark_alpha, 'chain': chain})
            if tokens:
                l3_data[comp][cat_key] = tokens

    processed = {'main_groups': main_groups, 'sem_groups': sem_groups,
                 'radius': radius, 'spacing': spacing, 'l2_cats': l2_cats, 'l3_data': l3_data}

    out_path = os.path.join(token_dir, 'processed.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"✓ [{cfg['name']}] 01 tokens/{cfg['dir']}/processed.json ({size_kb:.1f} KB)")
    print(f"  L2: {len(l2_cats)} 类, {sum(len(v) for v in l2_cats.values())} tokens")

    return processed


# ── 入口 ──────────────────────────────────────────────────────────────────────

target = sys.argv[1] if len(sys.argv) > 1 else None
if target:
    if target not in APPS:
        print(f"❌ 未知 APP: {target}，可用: {', '.join(APPS.keys())}")
        sys.exit(1)
    result = generate(target)
    if target == 'qiandao':
        write_styles_css(result, STYLES_CSS)
    # 单 APP 更新时也同步组件数据到 HTML
    if os.path.exists(DS_HTML):
        write_components_html()
        write_font_vars_html()
else:
    all_results = {}
    for app_id in APPS:
        result = generate(app_id)
        all_results[app_id] = result
        if app_id == 'qiandao':
            write_styles_css(result, STYLES_CSS)
    if os.path.exists(DS_HTML):
        write_design_system_html(all_results)  # 内部已调用 write_components_html
        write_font_vars_html()
    print(f"\n✓ 全部 {len(APPS)} 个 APP 生成完成")

update_business_module_md()
