#!/usr/bin/env python3
# Minimal static-site generator: content/**.md -> site/**.html with a tree nav.
import os, re, html, shutil, datetime, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "docs")

def esc(s): return html.escape(s, quote=False)

def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
    return s

def md_to_html(md):
    out, i, lines = [], 0, md.split('\n')
    def close_list(stack):
        while stack: out.append('</%s>' % stack.pop())
    lst = []
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith('```'):
            close_list(lst)
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].strip().startswith('```'):
                buf.append(esc(lines[j])); j += 1
            out.append('<pre><code>' + '\n'.join(buf) + '</code></pre>')
            i = j + 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            close_list(lst); n = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (n, inline(m.group(2)), n)); i += 1; continue
        if re.match(r'^\s*(-{3,}|\*{3,})\s*$', ln):
            close_list(lst); out.append('<hr>'); i += 1; continue
        m = re.match(r'^\s*[-*]\s+(.*)$', ln)
        if m:
            if not lst or lst[-1] != 'ul': close_list(lst); lst.append('ul'); out.append('<ul>')
            out.append('<li>%s</li>' % inline(m.group(1))); i += 1; continue
        m = re.match(r'^\s*\d+\.\s+(.*)$', ln)
        if m:
            if not lst or lst[-1] != 'ol': close_list(lst); lst.append('ol'); out.append('<ol>')
            out.append('<li>%s</li>' % inline(m.group(1))); i += 1; continue
        m = re.match(r'^\s*>\s?(.*)$', ln)
        if m:
            close_list(lst); out.append('<blockquote>%s</blockquote>' % inline(m.group(1))); i += 1; continue
        if ln.strip().startswith('|') and i+1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
            close_list(lst)
            hdr = [c.strip() for c in ln.strip().strip('|').split('|')]
            out.append('<table><thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in hdr) + '</tr></thead><tbody>')
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                out.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in cells) + '</tr>'); i += 1
            out.append('</tbody></table>'); continue
        if ln.strip() == '':
            close_list(lst); i += 1; continue
        close_list(lst); out.append('<p>%s</p>' % inline(ln)); i += 1
    close_list(lst)
    return '\n'.join(out)

def parse(path):
    txt = open(path, encoding='utf-8').read()
    meta = {}
    if txt.startswith('---'):
        end = txt.find('\n---', 3)
        if end > 0:
            for line in txt[3:end].strip().split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1); meta[k.strip()] = v.strip().strip('"')
            txt = txt[end+4:]
    return meta, txt

def title_of(meta, path):
    if meta.get('title'): return meta['title']
    base = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r'^\d+[-_]', '', base).replace('-', ' ').replace('_', ' ')

USE_EN_LABELS = False

def nav_field(path):
    try:
        m, _ = parse(path)
        return m.get('nav')
    except Exception:
        return None

def label_for(relpath, fallback):
    if USE_EN_LABELS:
        en = os.path.join(CONTENT, 'en', relpath)
        if os.path.exists(en):
            m, _ = parse(en)
            if m.get('title'):
                return m['title']
    # explicit nav label on the KO file wins if present
    return fallback
    return fallback

DATE_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')

def build_tree(dirpath, rel=''):
    items = []
    dated = []
    for name in sorted(os.listdir(dirpath)):
        if name == 'en' and dirpath == CONTENT:
            continue
        full = os.path.join(dirpath, name)
        if os.path.isdir(full):
            sub = build_tree(full, (rel + '/' + name) if rel else name)
            idx = os.path.join(full, 'index.md')
            dlink = ((rel + '/' + name) if rel else name) + '/index.html' if os.path.exists(idx) else None
            dlabel = None
            if os.path.exists(idx):
                _m2, _ = parse(idx)
                dlabel = _m2.get('nav') or label_for(((rel + '/' + name) if rel else name) + '/index.md', _m2.get('title'))
            items.append(('dir', name, sub, dlink, dlabel))
        elif name.endswith('.md'):
            if name == 'index.md' and rel:
                continue  # 섹션 인덱스는 트리 요약(summary)에서 이미 링크됨
            base = name[:-3]
            m = DATE_RE.match(base)
            link = (rel + '/' if rel else '') + base + '.html'
            if m:
                dated.append((int(m.group(1)), int(m.group(2)), link))
            else:
                meta, _ = parse(full)
                frel = (rel + '/' + name) if rel else name
                items.append(('file', link, nav_field(full) or label_for(frel, title_of(meta, full))))
    if dated:
        years = {}
        for y, mo, link in dated:
            years.setdefault(y, {}).setdefault(mo, []).append(('file', link, link.split('/')[-1][:-5]))
        yn = []
        for y in sorted(years, reverse=True):
            mn = [('ymm', datetime.date(2000, mo, 1).strftime('%b'), years[y][mo]) for mo in sorted(years[y], reverse=True)]
            yn.append(('ym', str(y), mn))
        items.extend(yn)
    return items

def nav_has(tree, prefix, cur):
    if not cur:
        return False
    for item in tree:
        if item[0] in ('dir', 'ym', 'ymm'):
            if nav_has(item[2], prefix, cur):
                return True
        elif item[0] == 'file' and item[1] == cur:
            return True
    return False

def render_nav(tree, prefix="", cur=None):
    out = ['<ul class="tree">']
    for item in tree:
        kind = item[0]
        if kind in ('dir', 'ym', 'ymm'):
            sub = item[2]
            op = ' open' if nav_has(sub, prefix, cur) else ''
            if kind == 'dir':
                dlink = item[3] if len(item) > 3 else None
                dlabel = item[4] if len(item) > 4 else None
                label = esc(dlabel) if dlabel else esc(re.sub(r'^\d+[-_]', '', item[1]))
                head = ('<a href="%s">%s</a>' % (esc(prefix + dlink), label)) if dlink else ('<span>%s</span>' % label)
            else:
                head = '<span>%s</span>' % esc(item[1])
            out.append('<li class="dir"><details%s><summary>%s</summary>%s</details></li>'
                       % (op, head, render_nav(sub, prefix, cur)))
        else:
            link, title = item[1], item[2]
            cc = ' class="cur"' if (cur and link == cur) else ''
            out.append('<li class="file"><a%s href="%s">%s</a></li>' % (cc, esc(prefix + link), esc(title)))
    out.append('</ul>')
    return '\n'.join(out)

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    year = datetime.date.today().year
    try:
        ASSET_V = hashlib.md5(open(os.path.join(ROOT, 'assets', 'style.css'), 'rb').read()).hexdigest()[:8]
    except Exception:
        ASSET_V = '1'
    comment_block = '''<section class="comments"><h3>\U0001F4AC 댓글</h3>
<script src="https://giscus.app/client.js"
  data-repo="96jangbc/polestar-overlay-lab"
  data-repo-id="R_kgDOVDlG9A"
  data-category="Announcements"
  data-category-id="DIC_kwDOVDlG9M4DHfgF"
  data-mapping="pathname"
  data-strict="0"
  data-reactions-enabled="1"
  data-emit-metadata="0"
  data-input-position="bottom"
  data-theme="light"
  data-lang="{data_lang}"
  data-loading="lazy"
  crossorigin="anonymous"
  async></script>
<noscript>댓글을 보려면 JavaScript를 켜 주세요.</noscript></section>'''
    KO, EN = CONTENT, os.path.join(CONTENT, 'en')

    def run(root, out_dir, lang):
        tree = build_tree(root)
        pages = 0
        for dp, _, fs in os.walk(root):
            for f in fs:
                if not f.endswith('.md'):
                    continue
                src = os.path.join(dp, f)
                rel = os.path.relpath(src, root)
                relhtml = rel[:-3] + '.html'
                meta, body = parse(src)
                depth = rel.count(os.sep)
                up = '../' * depth
                t = title_of(meta, src)
                navp = render_nav(tree, up, relhtml)
                is_index = (rel == 'index.md')
                if lang == 'ko':
                    toggle = ('<a class="lang" href="%sen/%s">\U0001F1FA\U0001F1F8 English</a>' % (up, relhtml)) if os.path.exists(os.path.join(EN, rel)) else ''
                    foot = "© %d jangbc's AI life · Claw와 함께 만든 기록" % year
                else:
                    toggle = '<a class="lang" href="%s../%s">\U0001F1F0\U0001F1F7 한국어</a>' % (up, relhtml)
                    foot = "© %d jangbc's AI life · Made with Claw" % year
                cblock = '' if is_index else comment_block.replace('{data_lang}', lang)
                ttl = t if is_index else t + " · jangbc's AI life"
                doc = f'''<!doctype html><html lang="{'ko' if lang == 'ko' else 'en'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(ttl)}</title>
<link rel="stylesheet" href="{up}assets/style.css?v={ASSET_V}">
<meta property="og:title" content="jangbc's AI life">
<meta property="og:description" content="AI · PEMWE · 투자 · Polestar4 — 좋아하는 것들을 파고드는 개인 블로그">
<meta property="og:image" content="https://96jangbc.github.io/polestar-overlay-lab/assets/img/hero-p4-light.png">
<link rel="icon" type="image/png" href="{up}assets/img/favicon-32.png?v={ASSET_V}">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png?v={ASSET_V}"></head><body>
<header class="top"><a class="brand" href="{up}index.html"><img class="logo" src="{up}assets/img/logo.png?v={ASSET_V}" alt=""> jangbc's AI life</a><span class="hright">{toggle}<span class="visits"><img alt="visitors" src="https://hits.sh/96jangbc.github.io/polestar-overlay-lab.svg?label=Views&amp;color=86b300&amp;labelColor=3a3f47"></span></span></header>
<div class="wrap"><aside class="side">{navp}</aside>
<main class="content">{md_to_html(body)}{cblock}</main></div>
<footer class="foot">{foot}</footer>
</body></html>'''
                dst = os.path.join(out_dir, relhtml)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'w', encoding='utf-8').write(doc)
                pages += 1
        return pages

    global USE_EN_LABELS
    USE_EN_LABELS = True
    pages = run(KO, OUT, 'ko')
    USE_EN_LABELS = False
    epages = run(EN, os.path.join(OUT, 'en'), 'en') if os.path.isdir(EN) else 0
    src_assets = os.path.join(ROOT, "assets")
    if os.path.isdir(src_assets):
        shutil.copytree(src_assets, os.path.join(OUT, "assets"))
        if os.path.isdir(EN):
            shutil.copytree(src_assets, os.path.join(OUT, "en", "assets"))
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('built', pages + epages, 'pages (ko %d / en %d)' % (pages, epages))

if __name__ == '__main__':
    main()
