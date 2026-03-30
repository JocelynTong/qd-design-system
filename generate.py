#!/usr/bin/env python3
"""
Echo Design System - Token 处理脚本
用法：
  python generate.py             # 生成所有 APP（千岛同时更新 _styles.css）
  python generate.py qiandao     # 只生成千岛（同时更新 _styles.css）
  python generate.py linjie      # 只生成临界
  python generate.py qihuo       # 只生成奇货

  python generate.py 截图           # 批量截图：补全所有缺失的 preview_html
  python generate.py 截图 --force   # 批量截图：强制刷新所有（覆盖已有）
  （需先：export FIGMA_TOKEN=... 每个 JSON 的 figma_file 字段指定文件 key）
"""

import json
import re
import os
import sys
import datetime

# ── Figma API 配置（用于 --fetch-previews）────────────────────────────────────
# 在此填写，或通过环境变量 FIGMA_TOKEN / FIGMA_FILE_KEY 传入
FIGMA_TOKEN    = os.environ.get('FIGMA_TOKEN', '')
FIGMA_FILE_KEY = os.environ.get('FIGMA_FILE_KEY', '')

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


# ── 骨架翻译：plugin _tree → token HTML ──────────────────────────────────────

def _normalize_color(s):
    """把 rgba(r, g, b, a) / hex 统一成可查 map 的 key。
    alpha=1 → '#RRGGBB'；否则 → 'rgba(r,g,b,a)'（去空格，数值精简）。"""
    s = s.strip()
    m = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)', s)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        if abs(a - 1.0) < 0.01:
            return f'#{r:02X}{g:02X}{b:02X}'
        # 精简小数：0.64 → .64
        a_str = f'{a:.4f}'.rstrip('0')
        if a_str.startswith('0.'):
            a_str = a_str[1:]
        return f'rgba({r},{g},{b},{a_str})'
    if s.startswith('#'):
        return s.upper()
    return s


def _build_token_color_map():
    """从 _styles.css 构建颜色逆映射：normalized_color → 'var(--token,value)'。"""
    cmap = {}
    if not os.path.exists(STYLES_CSS):
        return cmap
    for m in re.finditer(r'--([\w-]+)\s*:\s*([^;}\n]+)', open(STYLES_CSS, encoding='utf-8').read()):
        var_name, raw = '--' + m.group(1), m.group(2).strip()
        if not raw or raw.startswith('/*') or not (raw.startswith('#') or 'rgb' in raw):
            continue
        key = _normalize_color(raw)
        if key and key not in cmap:
            cmap[key] = f'var({var_name},{raw})'
    return cmap


def _build_font_token_map():
    """从 typography.json 构建字体逆映射：(weight,size_px,lh_px) → 'var(--font-xx,...)'。"""
    fmap = {}
    typo_path = os.path.join(BASE, '02 components', '00.01 Typography.json')
    if not os.path.exists(typo_path):
        return fmap
    css_vars = json.load(open(typo_path, encoding='utf-8')).get('css_variables', {})
    for var_name, val in css_vars.items():
        # "500 24px/30px 'PingFang SC',sans-serif"
        m = re.match(r'(\d+)\s+(\d+)px/(\d+)px', val)
        if m:
            fmap[(m.group(1), m.group(2), m.group(3))] = f'var({var_name},{val})'
    return fmap


# 初始化一次，供全局使用（generate.py 运行时加载一次即可）
_TOKEN_CMAP = None
_TOKEN_FMAP = None

def _get_token_maps():
    global _TOKEN_CMAP, _TOKEN_FMAP
    if _TOKEN_CMAP is None:
        _TOKEN_CMAP = _build_token_color_map()
        _TOKEN_FMAP = _build_font_token_map()
    return _TOKEN_CMAP, _TOKEN_FMAP


# CSS 属性白名单：保留对渲染有意义的属性，过滤 Figma 专有噪音
_KEEP_CSS = {
    'display', 'flex-direction', 'flex-wrap', 'align-items', 'align-content',
    'align-self', 'justify-content', 'justify-self', 'gap', 'row-gap', 'column-gap',
    'flex', 'flex-grow', 'flex-shrink', 'flex-basis',
    'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
    'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
    'background', 'background-color', 'border-radius', 'border',
    'border-top', 'border-right', 'border-bottom', 'border-left',
    'color', 'font-size', 'font-weight', 'line-height', 'font-family',
    'letter-spacing', 'text-align', 'white-space', 'overflow', 'text-overflow',
    'position', 'top', 'right', 'bottom', 'left', 'inset', 'z-index',
    'opacity', 'box-shadow', 'transform', 'pointer-events',
}
_COLOR_CSS = {'color', 'background', 'background-color', 'border-color',
              'fill', 'stroke', 'outline-color', 'text-decoration-color'}


def _map_css(css_dict, cmap, fmap):
    """把 Figma 原始 CSS dict 翻译成 token 化 CSS dict。
    - 颜色属性 → cmap 逆查
    - font-size + font-weight + line-height 组合 → font token shorthand"""
    result = {}

    # 字体 token（先剥掉 Figma 注入的 CSS 注释，如 "18px /* 150% */"）
    def _strip_css_comment(v):
        return re.sub(r'/\*.*?\*/', '', v).strip()
    w = css_dict.get('font-weight', '')
    sz = re.sub(r'px$', '', _strip_css_comment(css_dict.get('font-size', '')))
    lh = re.sub(r'px$', '', _strip_css_comment(css_dict.get('line-height', '')))
    font_skip = set()
    if w and sz and lh:
        fkey = (w, sz, lh)
        if fkey in fmap:
            result['font'] = fmap[fkey]
            font_skip = {'font-size', 'font-weight', 'line-height', 'font-family',
                         'letter-spacing', 'font-style', 'font-variant'}

    for k, v in css_dict.items():
        if k not in _KEEP_CSS or k in font_skip:
            continue
        v = _strip_css_comment(v)  # 剥掉 "18px /* 110% */" 等注释
        if any(cp in k for cp in _COLOR_CSS):
            nv = _normalize_color(v)
            v = cmap.get(nv, v)
        result[k] = v

    return result


def _tree_to_html(tree, cmap, fmap, depth=0, fkmap=None, _inline=False):
    """递归把 plugin 导出的 _tree 转成 token 化 HTML。
    TEXT → <span>；INSTANCE → 1)embed_html 2)_tree递归 3)_css_to_embed 4)空占位；其余 → <div>。
    fkmap: figma_key → vdata，用于查 embed_html 或递归渲染 _tree。
    _inline: True 时把当前节点渲染成 inline-flex（父容器 ellipsis 模式下使用）。"""
    if not tree or not isinstance(tree, dict):
        return ''

    t = tree.get('type', 'FRAME')
    raw_css = tree.get('css') or {}
    css = _map_css(raw_css, cmap, fmap)
    style = ';'.join(f'{k}:{v}' for k, v in css.items())

    # TEXT
    if t == 'TEXT':
        text = tree.get('text', '')
        tag = 'p' if depth == 0 else 'span'
        # nowrap 默认：防止标签文字在紧凑布局里折行（有 overflow:hidden 时 nowrap 本就是必要的）
        if 'white-space' not in css:
            css['white-space'] = 'nowrap'
        style = ';'.join(f'{k}:{v}' for k, v in css.items())
        s = f' style="{style}"' if style else ''
        return f'<{tag}{s}>{text}</{tag}>'

    # INSTANCE：_tree 有 children 时优先 P2（保留 data-component 嵌套）；否则 P1 embed_html
    if t == 'INSTANCE':
        if _inline:
            css['display'] = 'inline-flex'
            css['vertical-align'] = 'middle'
        # _embed 字段：节点自带的 embed HTML，优先于 fkmap 查找（允许在引用节点中覆盖子组件样式）
        embed = tree.get('_embed') or None
        if not embed and fkmap and tree.get('key'):
            vdata = fkmap.get(tree['key'])
            if vdata:
                sub_tree = vdata.get('_tree')
                has_children = bool(sub_tree and sub_tree.get('children'))
                if has_children:
                    embed = (
                        _tree_to_html(sub_tree, cmap, fmap, depth + 1, fkmap)
                        or vdata.get('embed_html')
                        or _css_to_embed(vdata.get('css'))
                    )
                else:
                    embed = (
                        vdata.get('embed_html')
                        or _tree_to_html(sub_tree, cmap, fmap, depth + 1, fkmap)
                        or _css_to_embed(vdata.get('css'))
                    )
        ref = tree.get('ref', '')
        data_comp = f' data-component="{ref}"' if ref else ''
        bool_prop = tree.get('_bool_prop', '')
        data_bool = f' data-bool="{bool_prop}"' if bool_prop else ''
        if embed:
            # 使用 embed 时：外层 div 只保留布局属性（flex/尺寸/对齐），
            # 去掉视觉属性（background/border-radius/padding/color），
            # 防止与 embed_html 自带样式叠加导致双重背景/尺寸。
            _VISUAL = {'background', 'background-color', 'border-radius', 'color',
                       'box-shadow', 'padding', 'padding-top', 'padding-right',
                       'padding-bottom', 'padding-left', 'border',
                       'border-top', 'border-right', 'border-bottom', 'border-left'}
            layout_css = {k: v for k, v in css.items() if k not in _VISUAL}
            layout_style = ';'.join(f'{k}:{v}' for k, v in layout_css.items())
            s = f' style="{layout_style}"' if layout_style else ''
            return f'<div{s}{data_comp}{data_bool}>{embed}</div>'
        s = f' style="{style}"' if style else ''
        return f'<div{s}{data_comp}{data_bool}></div>'

    # FRAME / GROUP / COMPONENT 等容器
    children = tree.get('children') or []
    is_h_flex = css.get('display') == 'flex' and css.get('flex-direction', 'row') != 'column'

    # depth=0 根节点：fixed width → fill container
    if depth == 0 and 'width' in css:
        css['width'] = '100%'
        css.setdefault('box-sizing', 'border-box')

    # 行内省略号模式：水平 flex 子项 > 4 时（属性行/芯片行），改为 block ellipsis 容器
    # 子项渲染为 inline-flex，overflow 产生标准 text-overflow:ellipsis 省略号
    if is_h_flex and len(children) > 4:
        gap = css.get('gap', '4px')
        ell_css = {
            'display': 'block',
            'overflow': 'hidden',
            'white-space': 'nowrap',
            'text-overflow': 'ellipsis',
        }
        # 保留 align-self / padding / background 等不影响内联布局的属性
        for k in ('align-self', 'padding', 'background', 'border-radius'):
            if k in css:
                ell_css[k] = css[k]
        ell_style = ';'.join(f'{k}:{v}' for k, v in ell_css.items())
        children_html = ''.join(
            _tree_to_html(ch, cmap, fmap, depth + 1, fkmap, _inline=True)
            for ch in children
        )
        return f'<div style="{ell_style}">{children_html}</div>'

    # 普通水平 flex 容器：overflow:hidden + min-width:0 防折行
    if is_h_flex:
        css.setdefault('overflow', 'hidden')
        css.setdefault('min-width', '0')

    # _inline 模式（父容器要求 inline-flex）
    if _inline:
        gap = css.pop('gap', '4px')
        css['display'] = 'inline-flex'
        css['vertical-align'] = 'middle'
        css['margin-right'] = gap
        for k in ('flex', 'flex-grow', 'flex-shrink', 'flex-basis', 'min-width', 'align-self'):
            css.pop(k, None)

    style = ';'.join(f'{k}:{v}' for k, v in css.items())
    children_html = ''.join(
        _tree_to_html(ch, cmap, fmap, depth + 1, fkmap)
        for ch in children
    )
    bool_prop = tree.get('_bool_prop', '')
    data_bool = f' data-bool="{bool_prop}"' if bool_prop else ''
    s = f' style="{style}"' if style else ''
    return f'<div{s}{data_bool}>{children_html}</div>'


def _css_to_embed(css):
    """从 variant.css 字段派生简单的 embed_html（fallback，无手写 embed_html 时使用）。
    只取 width / height / border-radius / background 生成占位 div。"""
    if not css or not isinstance(css, dict):
        return ''
    props = {}
    for k in ('width', 'height', 'border-radius', 'background'):
        if k in css:
            props[k] = css[k]
    if not props:
        return ''
    style = ';'.join(f'{k}:{v}' for k, v in props.items())
    return f'<div style="{style};flex-shrink:0"></div>'


def _resolve_ref_comp(ref_cid, components, ref_map):
    """用 kebab CID / figma 原名 / 前缀三种方式查找目标组件，返回 (comp, resolved_vk)。"""
    # 1. kebab CID 直接查
    comp = components.get(ref_cid)
    if comp:
        return comp, None
    # 2. COMPONENT_REF_MAP 精确查（figma_name → {cid, variant}）
    mapped = ref_map.get(ref_cid)
    if mapped:
        return components.get(mapped['cid']), mapped.get('variant')
    # 3. 前缀查（base 组件名，如 "💙 01.01_Navigation Bar"）
    for mk, mv in ref_map.items():
        if mk.startswith(ref_cid):
            return components.get(mv['cid']), None
    return None, None


def _check_one_ref(cref, components, cid, vk, label='component_ref', ref_map=None):
    """校验单个 ref 对象（{ cid, props/variants }）"""
    ref_cid = cref.get('cid', '')
    ref_comp, resolved_vk = _resolve_ref_comp(ref_cid, components, ref_map or {})
    if not ref_comp:
        print(f'⚠️ [{label}] {ref_cid} 未找到（{cid}/{vk}）')
        return
    if resolved_vk:
        if resolved_vk not in (ref_comp.get('variants') or {}):
            print(f'⚠️ [{label}] resolved variant "{resolved_vk}" 在 {ref_cid} 中不存在（{cid}/{vk}）')
    else:
        match_props = cref.get('props') or cref.get('variants') or {}
        if match_props:
            # 旧格式检测：裸值（非 {type,value} dict）说明未迁移到 componentProperties 透传格式
            for _k, _val in match_props.items():
                if not isinstance(_val, dict) or 'type' not in _val:
                    print(f'⚠️ [{label}] ref.props["{_k}"] 为旧格式（裸值 {_val!r}），应迁移为 {{type, value}} 格式（直接透传 componentProperties）')
            def _hay(rvk):
                fn = (ref_comp.get('variants') or {}).get(rvk, {}).get('figma_name', '')
                return rvk + ' ' + fn
            def _pval(v):
                return v['value'] if isinstance(v, dict) and 'value' in v else v
            variant_props = {k: _pval(v) for k, v in match_props.items()
                             if not (isinstance(v, dict) and v.get('type') == 'BOOLEAN')
                             and not isinstance(v, bool)}
            found = not variant_props or any(
                all(f'{k}={v}' in _hay(rvk) for k, v in variant_props.items())
                for rvk in (ref_comp.get('variants') or {})
            )
            if not found:
                print(f'⚠️ [{label}] {ref_cid} 无精确匹配 variant（props={match_props}）')


def resolve_component_refs(components, ref_map=None):
    """校验 component_ref / component_refs 引用是否有效，打印缺口警告。
    不复制 HTML——浏览器侧 _genBizVisual 在运行时从 COMPONENTS_DATA 直接解析。
    支持三种节点：
      Leaf       → preview_html（无需校验）
      1:1 Ref    → component_ref: { cid, props }
      Wrapper    → component_refs: [{ cid, props }, ...]
    cid 支持 kebab 格式（01.01-navigation-bar）和 figma 原名（💙 01.01_Navigation Bar）。"""
    if ref_map is None:
        ref_map = build_ref_map(components)
    for cid, cdata in components.items():
        for vk, vdata in (cdata.get('variants') or {}).items():
            cref = vdata.get('component_ref')
            if cref:
                _check_one_ref(cref, components, cid, vk, 'component_ref', ref_map)
            for i, ref in enumerate(vdata.get('component_refs') or []):
                _check_one_ref(ref, components, cid, vk, f'component_refs[{i}]', ref_map)


def auto_generate_tree_previews(components):
    """对有 _tree 但缺 preview_html 的 variant，
    用 _tree_to_html 生成 _tree_preview_html（存入 components dict，不写 JSON）。
    _hidden 变体也处理，供 _canSwitch chip 切换时渲染用。
    返回生成数量。"""
    cmap, fmap = _get_token_maps()

    # 构建 figma_key → vdata 查找表，供 INSTANCE embed_html 内嵌使用
    fkmap = {}
    for cdata in components.values():
        for vdata in (cdata.get('variants') or {}).values():
            fk = vdata.get('figma_key')
            if fk and (vdata.get('embed_html') or vdata.get('css')):
                fkmap[fk] = vdata

    count = 0
    for cdata in components.values():
        for vdata in (cdata.get('variants') or {}).values():
            if vdata.get('preview_html') or vdata.get('_tree_preview_html'):
                continue
            # 有 previewMap 的 variant 不需要 _tree_preview_html（chips 即是交互入口）
            props = vdata.get('props') or {}
            has_pm = any(
                isinstance(pv, dict) and pv.get('previewMap')
                for pv in props.values()
            )
            if has_pm:
                continue
            tree = vdata.get('_tree')
            if not tree:
                continue
            html = _tree_to_html(tree, cmap, fmap, fkmap=fkmap)
            if html:
                # 包 padding:0 10px 外边距，对齐 preview_html 手写规范（375px 容器由浏览器侧 _genBizVisual 包）
                vdata['_tree_preview_html'] = f'<div style="width:375px;box-sizing:border-box;overflow:hidden">{html}</div>'
                count += 1
    if count:
        print(f'✓ [骨架翻译] 从 _tree 自动生成 {count} 个 _tree_preview_html')
    return count


def build_ref_map(components):
    """构建 {figma_name: {cid, variant}} 映射，用于 slot 引用解析。
    key 为 variant 的 figma_name（精确匹配，含 variant 部分如 '💙 00.05_Button / Icon'），
    value 为 {cid: '00.08-button', variant: 'Icon'}。"""
    ref_map = {}
    for cid, cdata in components.items():
        for vk, vdata in (cdata.get('variants') or {}).items():
            fn = (vdata.get('figma_name') or '').strip()
            if fn:
                ref_map[fn] = {'cid': cid, 'variant': vk}
    return ref_map


def compose_variant_preview(variant, all_comps, ref_map):
    """对有 swapProp slots 的 variant，生成：
    - composed_html：含组件边界标注（cmp-slot-ref badge）的预览 HTML
    - code_html：纯结构参考版，slot 内容替换为带 props 注释的占位，供研发拿来即用
    返回 (composed_html, code_html) 或 (None, None)。
    """
    slots = variant.get('slots') or []
    swap_slots = [s for s in slots if s.get('swapProp') and (s.get('name') or '').startswith('💙')]
    if not swap_slots:
        return None, None

    slot_parts = []
    code_parts = []
    for sl in swap_slots:
        ref = ref_map.get((sl['name'] or '').strip())
        if not ref:
            return None, None
        child_variant = (all_comps.get(ref['cid'], {}).get('variants') or {}).get(ref['variant'], {})
        embed_html = child_variant.get('embed_html')
        if not embed_html:
            return None, None
        css = sl.get('css')
        if not css or not isinstance(css, dict) or any(isinstance(v2, dict) for v2 in css.values()):
            return None, None
        slot_style = ';'.join(f'{k}:{v2}' for k, v2 in css.items())
        comp_label = sl['name'].strip()

        # 预览：slot 容器（无标注，仅布局）
        slot_parts.append(
            f'<div class="cmp-slot-ref" data-component="{comp_label}" style="{slot_style}">'
            f'{embed_html}'
            f'</div>'
        )

        # 结构参考：收集子组件默认 props，生成注释占位
        child_props = child_variant.get('props') or {}
        prop_hints = []
        for pk, pv in child_props.items():
            if pk == 'Booleans' and isinstance(pv, dict):
                for bk, bv in pv.items():
                    if isinstance(bv, dict) and 'default' in bv:
                        prop_hints.append(f'{bk}:{"on" if bv["default"] else "off"}')
            elif isinstance(pv, dict) and 'default' in pv:
                prop_hints.append(f'{pk}:{pv["default"]}')
        props_str = '  ' + ' · '.join(prop_hints) if prop_hints else ''
        swap_prop = sl.get('swapProp', '')
        comment = f'<!-- {comp_label}  slot:{swap_prop}{props_str} -->'
        code_parts.append(f'<div style="{slot_style}">{comment}</div>')

    inner = ''.join(slot_parts)
    code_inner = ''.join(code_parts)
    variant_css = variant.get('css') or {}
    if isinstance(variant_css, dict) and variant_css:
        outer_style = ';'.join(f'{k}:{v}' for k, v in variant_css.items())
        composed_html = f'<div style="{outer_style}">{inner}</div>'
        code_html = f'<div style="{outer_style}">{code_inner}</div>'
    else:
        composed_html = inner
        code_html = code_inner

    return composed_html, code_html


def _load_components():
    """扫描 02 components/*.json + 03 business/*/*.json，返回 (components, ref_map)。
    供 write_components_html / repair_component_slots / validate_components 共享，避免重复 IO。"""
    import glob as _glob
    SKIP_KEYS = {'figma_keys', 'common_icons_quick_ref', 'css_variables'}
    comp_dir = os.path.join(BASE, '02 components')
    components = {}

    if os.path.isdir(comp_dir):
        for fn in sorted(os.listdir(comp_dir)):
            if not fn.endswith('.json') or fn.startswith('_'):
                continue
            with open(os.path.join(comp_dir, fn), encoding='utf-8') as f:
                data = json.load(f)
            fp = data.get('figma_page', '')
            cid = ('💙 ' + fp) if fp else fn.replace('.json', '').replace(' ', '_').lower()
            light = {k: v for k, v in data.items() if k not in SKIP_KEYS}
            components[cid] = {'_file': fn, '_path': os.path.join(comp_dir, fn), **light}

    def _vk_from_figma_name(figma_name):
        """'Type=ISLANDS' → 'ISLANDS', '视图=单列, 类型=单图' → '单列_单图'"""
        if not figma_name:
            return 'Default'
        if '=' not in figma_name:
            return figma_name.strip().replace(' ', '_')
        parts = [p.strip() for p in figma_name.split(',')]
        vals = [p.split('=', 1)[1].strip() if '=' in p else p.strip() for p in parts]
        result = '_'.join(v for v in vals if v)
        return result or 'Default'

    biz_dir = os.path.join(BASE, '03 business')
    for biz_path in sorted(_glob.glob(os.path.join(biz_dir, '*', '*.json'))):
        fn = os.path.basename(biz_path)
        if fn.startswith('_'):
            continue
        with open(biz_path, encoding='utf-8') as f:
            data = json.load(f)

        if 'pages' in data:
            # ── 新 pages 格式：每个 component_def 节点 → 独立组件 ──────────────────
            for page in data.get('pages', []):
                for node in page.get('nodes', []):
                    if node.get('type') != 'component_def':
                        continue
                    figma_name = node.get('figma_name', '')
                    if not figma_name:
                        continue
                    cid = figma_name
                    if cid in components:
                        continue
                    variants_raw = node.get('variants', [])
                    if isinstance(variants_raw, list) and variants_raw:
                        # list of variant dicts → 转 dict，key 从 figma_name 推导
                        variants = {}
                        seen = set()
                        for v in variants_raw:
                            if not isinstance(v, dict):
                                continue
                            vfn = v.get('figma_name', '')
                            vk = _vk_from_figma_name(vfn)
                            base, i = vk, 2
                            while vk in seen:
                                vk = f'{base}_{i}'; i += 1
                            seen.add(vk)
                            variants[vk] = v
                        comp_data = {
                            '_file': fn, '_path': biz_path,
                            'figma_name': figma_name,
                            'figma_key': node.get('figma_key', ''),
                            'css': node.get('css', {}),
                            'variants': variants,
                        }
                    else:
                        # 无子变体 → 节点本身作为单一 variant
                        last = figma_name.split(' / ')[-1].strip()
                        single_v = {k: v for k, v in node.items() if k not in ('type', 'figma_name')}
                        comp_data = {
                            '_file': fn, '_path': biz_path,
                            'figma_name': figma_name,
                            'figma_key': node.get('figma_key', ''),
                            'css': node.get('css', {}),
                            'variants': {last: single_v},
                        }
                    components[cid] = comp_data
        else:
            # ── 旧格式：单文件单组件 ───────────────────────────────────────────────
            comp_field = data.get('component', '')
            cid = comp_field if comp_field else fn.replace('.json', '').replace(' ', '_').lower()
            if cid in components:
                continue
            light = {k: v for k, v in data.items() if k not in SKIP_KEYS}
            components[cid] = {'_file': fn, '_path': biz_path, **light}

    def sort_key(item):
        k = re.sub(r'^[^\w\d]+\s*', '', item[0])  # strip emoji prefix for sorting
        m = re.match(r'^(\d+)', k)
        return (0, k) if m else (1, k)
    components = dict(sorted(components.items(), key=sort_key))

    ref_map = build_ref_map(components)
    return components, ref_map


def write_components_html(components=None, ref_map=None):
    """把组件数据注入 HTML 的 COMPONENTS_DATA 块。
    components/ref_map 可由调用方传入（_load_components()），避免重复 IO。"""
    if components is None:
        components, ref_map = _load_components()

    # 为有 swapProp slots 的 variant 生成组合预览 + 组件树
    composed_count = 0
    for cid, cdata in components.items():
        for vk, vdata in (cdata.get('variants') or {}).items():
            composed_html, code_html = compose_variant_preview(vdata, components, ref_map)
            if composed_html:
                vdata['_composed_preview_html'] = composed_html
                if code_html:
                    vdata['_code_html'] = code_html
                composed_count += 1
    if composed_count:
        print(f'✓ [组件库] 组合预览已生成（{composed_count} 个 variant）')

    # 从 _tree 自动生成 _tree_preview_html（fallback，不写 JSON）
    auto_generate_tree_previews(components)
    # 解析 component_ref 引用，从被引用组件复用 preview_html
    resolve_component_refs(components, ref_map)

    # 合并 _White 变体：将 Foo_White 的预览挂载到 Foo._white_preview_html，并标记隐藏
    for cdata in components.values():
        variants = cdata.get('variants') or {}
        for gk in [k for k in list(variants) if k.endswith('_White')]:
            base_key = gk[:-6]
            if base_key in variants:
                gv = variants[gk]
                variants[base_key]['_white_preview_html'] = (
                    gv.get('_composed_preview_html') or gv.get('preview_html', ''))
                if gv.get('_code_html'):
                    variants[base_key]['_white_code_html'] = gv['_code_html']
                gv['_hidden'] = True

    data_js = ('var COMPONENTS_DATA=' + json.dumps(components, ensure_ascii=False, separators=(',', ':')) + ';'
               + 'var COMPONENT_REF_MAP=' + json.dumps(ref_map, ensure_ascii=False, separators=(',', ':')) + ';')

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
    typo_path = os.path.join(BASE, '02 components', '00.01 Typography.json')
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


def write_design_system_html(all_processed, components=None, ref_map=None):
    """将全部 APP token 数据 + 组件数据 + 字体变量一次性注入 HTML（单次读写）。"""
    if components is None:
        components, ref_map = _load_components()

    # ── 1. token data ──
    BEGIN = '/* === AUTO-GENERATED DATA BEGIN === */'
    END   = '/* === AUTO-GENERATED DATA END === */'
    payload = dict(all_processed)
    payload['_generated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    data_js = 'var INJECTED_DATA=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';'

    # ── 2. components data ──
    composed_count = 0
    for cid, cdata in components.items():
        for vk, vdata in (cdata.get('variants') or {}).items():
            composed_html, code_html = compose_variant_preview(vdata, components, ref_map)
            if composed_html:
                vdata['_composed_preview_html'] = composed_html
                if code_html:
                    vdata['_code_html'] = code_html
                composed_count += 1
    if composed_count:
        print(f'✓ [组件库] 组合预览已生成（{composed_count} 个 variant）')

    # 从 _tree 自动生成 _tree_preview_html（fallback，不写 JSON）
    auto_generate_tree_previews(components)
    # 解析 component_ref 引用，从被引用组件复用 preview_html
    resolve_component_refs(components, ref_map)

    for cdata in components.values():
        variants = cdata.get('variants') or {}
        for gk in [k for k in list(variants) if k.endswith('_White')]:
            base_key = gk[:-6]
            if base_key in variants:
                gv = variants[gk]
                variants[base_key]['_white_preview_html'] = (
                    gv.get('_composed_preview_html') or gv.get('preview_html', ''))
                if gv.get('_code_html'):
                    variants[base_key]['_white_code_html'] = gv['_code_html']
                gv['_hidden'] = True

    comp_js = ('var COMPONENTS_DATA=' + json.dumps(components, ensure_ascii=False, separators=(',', ':')) + ';'
               + 'var COMPONENT_REF_MAP=' + json.dumps(ref_map, ensure_ascii=False, separators=(',', ':')) + ';')

    # ── 3. font vars ──
    font_css = ''
    typo_path = os.path.join(BASE, '02 components', '00.01 Typography.json')
    if os.path.exists(typo_path):
        with open(typo_path, encoding='utf-8') as f:
            typo = json.load(f)
        css_vars = typo.get('css_variables', {})
        if css_vars:
            font_css = ':root{' + ';'.join(f'{k}:{v}' for k, v in css_vars.items()) + '}'

    # ── 单次读写 ──
    with open(DS_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    content = _inject_block(content, BEGIN, END, data_js)
    content = _inject_block(content,
                             '/* === COMPONENTS DATA BEGIN === */',
                             '/* === COMPONENTS DATA END === */',
                             comp_js)
    if font_css:
        content = _inject_block(content,
                                 '/* === FONT VARS BEGIN === */',
                                 '/* === FONT VARS END === */',
                                 font_css)

    app_css = build_app_css_overrides(all_processed)
    if app_css:
        content = _inject_block(content,
                                 '/* === APP CSS BEGIN === */',
                                 '/* === APP CSS END === */',
                                 app_css)

    with open(DS_HTML, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'✓ [设计系统] 00 design-system-index.html Token 数据已注入')
    print(f'✓ [组件库] COMPONENTS_DATA 已注入（{len(components)} 个组件）')
    if font_css:
        typo_count = font_css.count(';') + 1
        print(f'✓ [Typography] HTML font vars 已注入（{typo_count} 个变量）')


def build_app_css_overrides(all_results):
    """为非千岛 app 生成 [data-app="xxx"] CSS 覆盖块，供组件 preview 颜色随 app 切换。"""
    lines = []
    for app_id, processed in all_results.items():
        if app_id == 'qiandao':
            continue  # 千岛是 :root 默认值，不需要覆盖
        parts = []
        for cat, tokens in processed.get('l2_cats', {}).items():
            for t in tokens:
                val = color_value(t['hex'], t['alpha'])
                if val:
                    parts.append(f"{token_key_to_var(t['key'])}:{val}")
        for comp, cats in processed.get('l3_data', {}).items():
            for cat, tokens in cats.items():
                for t in tokens:
                    val = color_value(t['hex'], t['alpha'])
                    if val:
                        parts.append(f"{token_key_to_var(t['key'])}:{val}")
        if parts:
            lines.append(f'[data-app="{app_id}"] {{{"; ".join(parts)}}}')
        # dark overrides
        dark_parts = []
        for cat, tokens in processed.get('l2_cats', {}).items():
            for t in tokens:
                if t.get('darkHex') and (t['darkHex'] != t['hex'] or t['darkAlpha'] != t['alpha']):
                    val = color_value(t['darkHex'], t['darkAlpha'])
                    if val:
                        dark_parts.append(f"{token_key_to_var(t['key'])}:{val}")
        for comp, cats in processed.get('l3_data', {}).items():
            for cat, tokens in cats.items():
                for t in tokens:
                    if t.get('darkHex') and (t['darkHex'] != t['hex'] or t['darkAlpha'] != t['alpha']):
                        val = color_value(t['darkHex'], t['darkAlpha'])
                        if val:
                            dark_parts.append(f"{token_key_to_var(t['key'])}:{val}")
        if dark_parts:
            lines.append(f'[data-app="{app_id}"][data-theme="dark"] {{{"; ".join(dark_parts)}}}')
    return '\n'.join(lines)


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

    # ── typography (from 02 components/00.01 Typography.json) ──
    typo_path = os.path.join(BASE, '02 components', '00.01 Typography.json')
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

def group_by_prefix(tokens_dict):
    """把 {key_NN: token} 字典按前缀分组，返回 {prefix: [{key, hex, alpha}, ...]}。"""
    groups = {}
    for k, v in tokens_dict.items():
        if not isinstance(v, dict) or '$type' not in v:
            continue
        group_key = re.sub(r'_\d+$', '', k)
        val = v.get('$value', {})
        hex_v = val.get('hex', '') if isinstance(val, dict) else ''
        alpha = val.get('alpha', 1) if isinstance(val, dict) else 1
        groups.setdefault(group_key, []).append({'key': k, 'hex': hex_v, 'alpha': alpha})
    return groups


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

    main_groups = group_by_prefix(pget('Main'))
    sem_groups  = group_by_prefix(pget('Semantics'))

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

# ── 入口 ──────────────────────────────────────────────────────────────────────

_quick = '--quick' in sys.argv  # 仅更新组件数据，跳过 token 处理
_args = [a for a in sys.argv[1:] if not a.startswith('--') and a not in ('截图', '--fetch-previews', '强制')]
target = _args[0] if _args else None

if _quick and not target:
    # --quick：只重新扫描 JSON，跳过 token 处理，单次写 HTML
    print('⚡ quick 模式：仅更新组件数据')
    if os.path.exists(DS_HTML):
        _comps, _ref_map = _load_components()
        write_components_html(_comps, _ref_map)
        write_font_vars_html()
elif target:
    if target not in APPS:
        print(f"❌ 未知 APP: {target}，可用: {', '.join(APPS.keys())}")
        sys.exit(1)
    result = generate(target)
    if target == 'qiandao':
        write_styles_css(result, STYLES_CSS)
    if os.path.exists(DS_HTML):
        _comps, _ref_map = _load_components()
        write_components_html(_comps, _ref_map)
        write_font_vars_html()
else:
    all_results = {}
    for app_id in APPS:
        result = generate(app_id)
        all_results[app_id] = result
        if app_id == 'qiandao':
            write_styles_css(result, STYLES_CSS)
    if os.path.exists(DS_HTML):
        _comps, _ref_map = _load_components()
        write_design_system_html(all_results, _comps, _ref_map)  # 单次读写
    print(f"\n✓ 全部 {len(APPS)} 个 APP 生成完成")

update_business_module_md()


# ── Slot 结构自动修复 ──────────────────────────────────────────────────────────

def _slot_container_style(slot):
    """从 slot.css 字段直接生成容器 style 字符串；字段缺失则返回 None。
    通用实现：不依赖 slot 引用的子组件类型，slot.css 即为完整规格。
    若 css 中任意值为 dict（如 _by_size 分尺寸规格），返回 None——这类 slot
    不是简单容器，无需 repair 函数修改 preview_html。"""
    css = slot.get('css')
    if not css or not isinstance(css, dict):
        return None
    if any(isinstance(v, dict) for v in css.values()):
        return None
    return ';'.join(f"{k}:{v}" for k, v in css.items())


def _patch_bool_style(html, bool_prop, new_style):
    """把 preview_html 里 data-bool="{bool_prop}" 元素的 style 替换为 new_style。
    兼容 style 在 data-bool 之前或之后两种写法。"""
    esc = re.escape(bool_prop)
    # 先试：... style="..." ... data-bool="X" ...
    r1 = r'(<\w+[^>]*?)\bstyle="[^"]*?"([^>]*?\bdata-bool="' + esc + r'"[^>]*?>)'
    out = re.sub(r1, rf'\1style="{new_style}"\2', html, flags=re.DOTALL)
    if out != html:
        return out
    # 再试：... data-bool="X" ... style="..." ...
    r2 = r'(<\w+[^>]*?\bdata-bool="' + esc + r'"[^>]*?)\bstyle="[^"]*?"([^>]*?>)'
    return re.sub(r2, rf'\1style="{new_style}"\2', html, flags=re.DOTALL)


def repair_component_slots(components=None):
    """
    对每个有 slots 声明的 variant 自动修复 preview_html，写回 JSON 文件。
    components 可由调用方传入，避免重复 IO。
    """
    comp_dir = os.path.join(BASE, '02 components')
    repaired = []

    # 只遍历 02 components（业务组件暂不做 repair）
    for fn in sorted(os.listdir(comp_dir)):
        if not fn.endswith('.json') or fn.startswith('_'):
            continue
        path = os.path.join(comp_dir, fn)
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue

        file_changed = False
        for vk, v in (data.get('variants') or {}).items():
            slots = v.get('slots') or []
            ph = v.get('preview_html', '')
            if not slots or not ph:
                continue

            for sl in slots:
                bool_prop = sl.get('boolProp') or sl.get('swapProp')
                if not bool_prop:
                    continue
                expected = _slot_container_style(sl)
                if not expected:
                    continue
                patched = _patch_bool_style(ph, bool_prop, expected)
                if patched != ph:
                    ph = patched
                    file_changed = True

            if file_changed:
                v['preview_html'] = ph

        if file_changed:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            repaired.append(fn)

    if repaired:
        print(f'🔧 slot 结构自动修复: {", ".join(repaired)}')
    else:
        print('✓ slot 结构检查通过，无需修复')
    return repaired


def _derive_expected_key(figma_name):
    """从 👻 业务组件的 figma_name 推导期望的 variant key。
    规则：👻 {Scene} / {ComponentPath}, {prop=value, ...}
      ComponentPath = Scene 之后各路径段去空格直接拼接（已是 CamelCase）
      VariantValues = 各 prop 的 value，~ → to，多词值首词保留其余首字母大写后用 _ 连接
    示例：
      👻 Islands / Feed / Ad, 视图=双列, 类型=首位  →  FeedAd_双列_首位
      👻 Islands / QuickEntry, 数量=3 Old Vision    →  QuickEntry_3_OldVision
      👻 Islands / QuickEntry, 数量=4~9             →  QuickEntry_4to9
      👻 Islands / Pin / Basic, Type=Home            →  PinBasic_Home
    """
    if not figma_name or '👻' not in figma_name:
        return None
    s = re.sub(r'^👻\s*', '', figma_name.strip())
    # 分离路径段和 variant 属性
    if ', ' in s:
        path_part, variant_part = s.split(', ', 1)
    else:
        path_part, variant_part = s, ''
    # ComponentPath：Scene 之后各段去空格拼接
    path_segs = [seg.strip().replace(' ', '') for seg in path_part.split('/')]
    component_path = ''.join(path_segs[1:]) if len(path_segs) > 1 else path_segs[0]
    if not variant_part:
        return component_path
    # VariantValues：多个 prop=value 按 ', ' 分割
    def _transform_val(val):
        val = val.replace('~', 'to')
        words = val.split()
        if len(words) <= 1:
            return val
        first = words[0]
        rest = ''.join((w[0].upper() + w[1:]) if w else '' for w in words[1:])
        return first + '_' + rest
    props = [p.strip() for p in variant_part.split(', ')]
    values = []
    for p in props:
        raw_val = p.split('=', 1)[1].strip() if '=' in p else p.strip()
        values.append(_transform_val(raw_val))
    return component_path + '_' + '_'.join(values) if values else component_path


def validate_components(components=None, ref_map=None):
    """
    校验 02 components/*.json 中的引用完整性，生成完成后自动运行。
    components/ref_map 可由调用方传入，避免重复 IO。
    """
    comp_dir = os.path.join(BASE, '02 components')
    icon_json = os.path.join(comp_dir, '00.03 Icon.json')
    warnings = []

    # 1. 读取合法图标集
    valid_icons = set()
    if os.path.exists(icon_json):
        raw = open(icon_json, encoding='utf-8').read()
        valid_icons = set(re.findall(r'"(kuril-[a-z0-9_]+)"', raw))

    # 3. 收集已定义的 CSS 变量（来自 _styles.css 和 HTML inline :root）
    known_vars = set()
    if os.path.exists(STYLES_CSS):
        css_raw = open(STYLES_CSS, encoding='utf-8').read()
        known_vars.update(re.findall(r'--([\w-]+)\s*:', css_raw))
    if os.path.exists(DS_HTML):
        html_raw = open(DS_HTML, encoding='utf-8').read()
        style_block = re.search(r'<style>(.*?)</style>', html_raw, re.DOTALL)
        if style_block:
            known_vars.update(re.findall(r'--([\w-]+)\s*:', style_block.group(1)))

    # 4. 构建 ref_map（使用传入的或独立加载）
    if components is not None and ref_map is not None:
        # 从传入的 components 提取 all_comps_raw（仅 02 components/）
        all_comps_raw = {cid: cdata for cid, cdata in components.items()
                         if not (cdata.get('_path') or '').startswith(os.path.join(BASE, '03'))}
        known_refs = ref_map
    else:
        all_comps_raw = {}
        for fn2 in sorted(os.listdir(comp_dir)):
            if not fn2.endswith('.json') or fn2.startswith('_') or fn2 == '00.03 Icon.json':
                continue
            try:
                d = json.loads(open(os.path.join(comp_dir, fn2), encoding='utf-8').read())
                d_fp = d.get('figma_page', '')
                cid2 = ('💙 ' + d_fp) if d_fp else fn2.replace('.json', '').replace(' ', '_').lower()
                all_comps_raw[cid2] = d
            except Exception:
                continue
        known_refs = build_ref_map(all_comps_raw)

    # 2. 遍历所有组件 JSON（跳过图标自身）
    for fn in sorted(os.listdir(comp_dir)):
        if not fn.endswith('.json') or fn.startswith('_') or fn == '00.03 Icon.json':
            continue
        path = os.path.join(comp_dir, fn)
        raw = open(path, encoding='utf-8').read()

        # 检查 kuril-* 图标名
        if valid_icons:
            used = set(re.findall(r'kuril-[a-z0-9_]+', raw))
            bad = used - valid_icons
            for name in sorted(bad):
                warnings.append(f'  ⚠️  {fn}: 图标 `{name}` 不在图标库中')

        try:
            data = json.loads(raw)
        except Exception:
            continue

        for vk, v in (data.get('variants') or {}).items():
            ph = v.get('preview_html', '')

            # 检查有 Button/Icon slots 的 variant 里 icon 是否用了 Button/Icon 结构
            if v.get('slots'):
                has_icon_btn_slot = any(
                    'Button / Icon' in (sl.get('name') or '') or '00.05_Button' in (sl.get('name') or '')
                    for sl in v['slots']
                )
                if has_icon_btn_slot and 'KurilIcons' in ph and 'flex-direction:column' not in ph:
                    warnings.append(f'  ⚠️  {fn} [{vk}]: 有 Button/Icon slots 但 preview_html 图标未用 Button/Icon 结构（缺 flex-direction:column）')

            # 检查 preview_html 和 slot.css 里的 var(--xxx) 是否都已定义
            if known_vars:
                used_in_ph = set(re.findall(r'var\(--([\w-]+)', ph))
                used_in_slots = set()
                for sl in (v.get('slots') or []):
                    for val in (sl.get('css') or {}).values():
                        used_in_slots.update(re.findall(r'var\(--([\w-]+)', str(val)))
                bad_vars = (used_in_ph | used_in_slots) - known_vars
                for bv in sorted(bad_vars):
                    warnings.append(f'  ⚠️  {fn} [{vk}]: CSS 变量 `--{bv}` 未在 _styles.css / HTML :root 中定义')

            # 检查 Booleans 与 preview_html 的 data-bool 对应关系
            props_data = v.get('props') or {}
            booleans_data = props_data.get('Booleans') or {}
            if isinstance(booleans_data, dict):
                # 收集所有可搜索的 HTML（preview_html + previewMap 所有值）
                all_html_sources = ph or ''
                for pk2, pv2 in props_data.items():
                    if isinstance(pv2, dict):
                        for pm_key in ('previewMap', 'whitePreviewMap'):
                            pm = pv2.get(pm_key)
                            if isinstance(pm, dict):
                                all_html_sources += ''.join(pm.values())
                for bk, bv_def in booleans_data.items():
                    # _boolsFor 限定类型的 boolean 在 previewMap 里找，不只查 preview_html
                    search_in = all_html_sources if (isinstance(bv_def, dict) and bv_def.get('_boolsFor')) else ph
                    if search_in and f'data-bool="{bk}"' not in search_in:
                        warnings.append(f'  ⚠️  {fn} [{vk}]: Boolean "{bk}" 无对应 data-bool="{bk}"（preview_html 缺少可控元素）')
                    elif ph and isinstance(bv_def, dict) and bv_def.get('default') is False:
                        tag_m = re.search(r'<[^>]*data-bool="' + re.escape(bk) + r'"[^>]*>', ph)
                        if tag_m and 'display:none' not in tag_m.group(0):
                            warnings.append(f'  ⚠️  {fn} [{vk}]: Boolean "{bk}" default=false 但元素无 display:none（初始状态不匹配）')

            # 检查 SELECT prop 默认值是否为 variant key 的子串（切换机制前提）
            # 排除 _hidden variant，避免其 key 分段干扰 is_switching 判断
            all_vks = set(k for k, vv in (data.get('variants') or {}).items() if not vv.get('_hidden'))
            for pk, pv_def in props_data.items():
                if pk == 'Booleans':
                    continue
                if not isinstance(pv_def, dict) or not pv_def.get('options'):
                    continue
                opts = pv_def['options']
                if sorted(str(o).lower() for o in opts) == ['false', 'true']:
                    continue
                all_vk_segments = set(seg for vk2 in all_vks for seg in vk2.split('_'))
                is_switching = any(str(o) in all_vk_segments for o in opts)
                if not is_switching:
                    continue
                if pv_def.get('variantMap'):
                    continue
                if pv_def.get('previewMap'):
                    continue
                _dv = pv_def.get('default')
                default_val = str(_dv) if _dv is not None else str(opts[0])
                if default_val not in vk:
                    warnings.append(f'  ⚠️  {fn} [{vk}]: prop "{pk}" 默认值 "{default_val}" 不在 key "{vk}" 中，variant 切换将失败')

            # 检查 slots 里的 💙 引用是否已录入，以及引用的子组件是否有 embed_html
            for sl in (v.get('slots') or []):
                sname = (sl.get('name') or '').strip()
                if not sname.startswith('💙'):
                    continue
                if sname not in known_refs:
                    warnings.append(f'  ℹ️  {fn} [{vk}]: 引用子组件 `{sname}` 尚未录入')
                elif sl.get('swapProp'):
                    ref = known_refs[sname]
                    child_v = (all_comps_raw.get(ref['cid'], {}).get('variants') or {}).get(ref['variant'], {})
                    if not child_v.get('embed_html'):
                        warnings.append(f'  ⚠️  {fn} [{vk}]: slot `{sname}` 有 swapProp 但子组件缺少 embed_html，组合预览将跳过')

            # 检查有 Color=White prop 的 variant 是否存在对应 _White 变体
            # 例外1：任一 prop 含 whitePreviewMap → White 已由 previewMap 机制处理
            # 例外2：variant 自身有 _white_preview_html → White 切换直接可用
            color_prop = props_data.get('Color')
            if isinstance(color_prop, dict) and color_prop.get('options'):
                has_white_opt = 'White' in [str(o) for o in color_prop['options']]
                has_white_preview_map = any(
                    isinstance(pv, dict) and pv.get('whitePreviewMap')
                    for pv in props_data.values()
                    if isinstance(pv, dict)
                )
                has_white_html = bool(v.get('_white_preview_html'))
                if has_white_opt and not has_white_preview_map and not has_white_html:
                    white_vk = vk + '_White'
                    if white_vk not in all_vks:
                        warnings.append(f'  ⚠️  {fn} [{vk}]: 有 Color=White 选项但缺少 `{white_vk}` 变体，White 切换将无效')

    # ── 03 business/ variant key 一致性校验 ─────────────────────────────────────
    biz_dir = os.path.join(BASE, '03 business')
    if os.path.isdir(biz_dir):
        for biz_module in sorted(os.listdir(biz_dir)):
            module_dir = os.path.join(biz_dir, biz_module)
            if not os.path.isdir(module_dir):
                continue
            for biz_fn in sorted(os.listdir(module_dir)):
                if not biz_fn.endswith('.json') or biz_fn.startswith('_'):
                    continue
                try:
                    biz_data = json.loads(open(os.path.join(module_dir, biz_fn), encoding='utf-8').read())
                except Exception:
                    continue
                for bvk, bvdata in (biz_data.get('variants') or {}).items():
                    fn_str = biz_fn.replace('.json', '')
                    biz_fn_name = figma_name_biz = bvdata.get('figma_name', '')
                    if not figma_name_biz or '👻' not in figma_name_biz:
                        continue
                    # key 含中文字符：提示改为 ASCII 命名
                    if re.search(r'[^\x00-\x7F]', bvk):
                        warnings.append(f'  ⚠️  {biz_module}/{biz_fn} [{bvk}]: key 含中文字符，建议改为 ASCII 命名')
                    expected = _derive_expected_key(figma_name_biz)
                    # 只在期望 key 是合法标识符（仅含字母/数字/下划线）时才警告
                    if expected and expected != bvk and re.match(r'^[\w]+$', expected):
                        warnings.append(f'  ⚠️  {biz_module}/{biz_fn} [{bvk}]: key 与 figma_name 不符，建议改为 "{expected}"')

    if warnings:
        print('\n── 组件校验警告 ──')
        for w in warnings:
            print(w)
    else:
        print('✓ 组件校验通过（图标名、Button/Icon 结构、CSS 变量）')


# ── Figma API 批量截图（截图命令） ───────────────────────────────────────────

def fetch_previews(force=False):
    """
    扫描 02 components/*.json 和 03 business/**/*.json，
    收集所有带 figma_key 的变体，按 figma_file 分组后批量调用 Figma API，
    并行下载预览图（PNG base64）写回各 JSON 的 preview_html 字段。

    需要：
      FIGMA_TOKEN    — Figma Personal Access Token（环境变量或文件头填写）
      FIGMA_FILE_KEY — 默认文件 key（JSON 没有 figma_file 字段时使用）

    每个 JSON 可用 "figma_file" 字段覆盖全局文件 key，实现跨文件批量截图。

    用法：
      python generate.py 截图           # 仅补全缺失的 preview_html
      python generate.py 截图 --force   # 全量刷新（覆盖已有）
    """
    try:
        import urllib.request, base64, time
        from concurrent.futures import ThreadPoolExecutor, as_completed
    except ImportError:
        print('❌ 标准库不可用，无法抓取 Figma 预览')
        return

    token = FIGMA_TOKEN
    if not token:
        print('❌ 请设置 FIGMA_TOKEN 环境变量，或在 generate.py 头部填写')
        return

    default_file_key = FIGMA_FILE_KEY
    headers = {'X-Figma-Token': token}

    # ── 1. 扫描所有 JSON，收集待截图项 ──────────────────────────────────────
    # pending[file_key] = [(path, vk, figma_key), ...]
    pending = {}

    scan_dirs = [os.path.join(BASE, '02 components')]
    biz_root = os.path.join(BASE, '03 business')
    if os.path.isdir(biz_root):
        for sub in sorted(os.listdir(biz_root)):
            sub_path = os.path.join(biz_root, sub)
            if os.path.isdir(sub_path):
                scan_dirs.append(sub_path)

    for scan_dir in scan_dirs:
        if not os.path.isdir(scan_dir):
            continue
        for fn in sorted(os.listdir(scan_dir)):
            if not fn.endswith('.json') or fn.startswith('_'):
                continue
            path = os.path.join(scan_dir, fn)
            try:
                with open(path, encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                continue

            file_key = data.get('figma_file') or default_file_key
            if not file_key:
                continue

            for vk, vdata in (data.get('variants') or {}).items():
                fk = vdata.get('figma_key')
                if not fk:
                    continue
                if not force and vdata.get('preview_html'):
                    continue
                pending.setdefault(file_key, []).append((path, vk, fk))

    if not pending:
        print('✓ 无需截图（所有变体已有 preview_html，或无 figma_key）')
        return

    total_count = sum(len(v) for v in pending.values())
    print(f'📸 待截图：{total_count} 个变体，涉及 {len(pending)} 个 Figma 文件\n')

    # ── 2. 每个 figma_file 调一次 API，解析 component key → node_id ──────────
    key_to_nodeid = {}  # (file_key, figma_key) → node_id

    for file_key, items in pending.items():
        needed = {fk for _, _, fk in items}
        print(f'  🔍 {file_key}：解析 {len(needed)} 个组件 key …')
        url = f'https://api.figma.com/v1/files/{file_key}/components'
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                comp_list = json.loads(resp.read())
            matched = 0
            for comp in (comp_list.get('meta', {}).get('components') or []):
                ck = comp.get('key', '')
                nid = comp.get('node_id', '')
                if ck in needed and nid:
                    key_to_nodeid[(file_key, ck)] = nid
                    matched += 1
            print(f'     → 匹配 {matched}/{len(needed)} 个')
        except Exception as e:
            print(f'  ⚠️  {file_key}：获取组件列表失败 → {e}')
        time.sleep(0.3)

    # ── 3. 每个 figma_file 批量请求图片 URL（每批最多 200 个节点）─────────────
    img_urls = {}  # (file_key, node_id) → image_url

    for file_key, items in pending.items():
        node_ids = list({key_to_nodeid[(file_key, fk)]
                         for _, _, fk in items
                         if (file_key, fk) in key_to_nodeid})
        if not node_ids:
            continue
        for i in range(0, len(node_ids), 200):
            batch = node_ids[i:i+200]
            url = (f'https://api.figma.com/v1/images/{file_key}'
                   f'?ids={",".join(batch)}&format=png&scale=2')
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=20) as resp:
                    img_data = json.loads(resp.read())
                for nid, src in (img_data.get('images') or {}).items():
                    if src:
                        img_urls[(file_key, nid)] = src
            except Exception as e:
                print(f'  ⚠️  {file_key}：获取图片 URL 失败 → {e}')
            time.sleep(0.2)

    # ── 4. 并行下载，写回 JSON ────────────────────────────────────────────────
    tasks = []  # (path, vk, img_src)
    for file_key, items in pending.items():
        for path, vk, fk in items:
            nid = key_to_nodeid.get((file_key, fk))
            src = img_urls.get((file_key, nid)) if nid else None
            if src:
                tasks.append((path, vk, src))

    print(f'\n  ⬇️  并行下载 {len(tasks)} 张图片 …')

    def _download(args):
        path, vk, src = args
        try:
            with urllib.request.urlopen(src, timeout=20) as r:
                b64 = base64.b64encode(r.read()).decode('ascii')
            return path, vk, f'<img src="data:image/png;base64,{b64}" style="width:375px;display:block" />', None
        except Exception as e:
            return path, vk, None, str(e)

    path_changes = {}  # path → {vk: preview_html}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_download, t): t for t in tasks}
        done = 0
        for fut in as_completed(futures):
            path, vk, preview, err = fut.result()
            done += 1
            if err:
                print(f'  ⚠️  [{vk}] 下载失败 → {err}')
            else:
                path_changes.setdefault(path, {})[vk] = preview
                print(f'  ✓ [{done}/{len(tasks)}] {os.path.basename(path)} · {vk}')

    total_fetched = 0
    for path, changes in path_changes.items():
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        for vk, preview in changes.items():
            if 'variants' in data and vk in data['variants']:
                data['variants'][vk]['preview_html'] = preview
                total_fetched += 1
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'\n✓ 截图完成，共抓取 {total_fetched} 个变体预览（{len(path_changes)} 个文件已更新）')
    if total_fetched and os.path.exists(DS_HTML):
        write_components_html()
        print('✓ COMPONENTS_DATA 已重新注入')


repaired = repair_component_slots()
if repaired and os.path.exists(DS_HTML):
    if '_comps' not in dir():
        _comps, _ref_map = _load_components()
    write_components_html(_comps, _ref_map)
if '_comps' not in dir():
    _comps, _ref_map = _load_components()
validate_components(_comps, _ref_map)

# 截图 / --fetch-previews 入口（放在 validate 之后）
if '截图' in sys.argv or '--fetch-previews' in sys.argv:
    force_flag = '--force' in sys.argv or '强制' in sys.argv
    fetch_previews(force=force_flag)
