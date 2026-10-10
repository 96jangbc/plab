#!/usr/bin/env python3
# Minimal static-site generator: content/**.md -> site/**.html with a tree nav.
import os, re, html, shutil, datetime

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

def build_tree(dirpath, rel=''):
    items = []
    for name in sorted(os.listdir(dirpath)):
        full = os.path.join(dirpath, name)
        if os.path.isdir(full):
            sub = build_tree(full, (rel + '/' + name) if rel else name)
            items.append(('dir', name, sub))
        elif name.endswith('.md'):
            meta, _ = parse(full)
            link = (rel + '/' if rel else '') + name[:-3] + '.html'
            items.append(('file', link, title_of(meta, full)))
    return items

def render_nav(tree, prefix=""):
    out = ['<ul class="tree">']
    for kind, a, b in tree:
        if kind == 'dir':
            out.append('<li class="dir"><span>%s</span>%s</li>' % (esc(re.sub(r'^\d+[-_]','',a)), render_nav(b, prefix)))
        else:
            out.append('<li class="file"><a href="%s">%s</a></li>' % (esc(prefix + a), esc(b)))
    out.append('</ul>')
    return '\n'.join(out)

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    tree = build_tree(CONTENT)
    nav = render_nav(tree)
    year = datetime.date.today().year
    pages = []
    for dp, _, fs in os.walk(CONTENT):
        for f in fs:
            if not f.endswith('.md'): continue
            src = os.path.join(dp, f)
            rel = os.path.relpath(src, CONTENT)
            relhtml = rel[:-3] + '.html'
            meta, body = parse(src)
            depth = rel.count(os.sep)
            up = '../' * depth
            t = title_of(meta, src)
            navp = render_nav(tree, up)
            doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t)} · Polestar4 오버레이 랩</title>
<link rel="stylesheet" href="{up}assets/style.css"></head><body>
<header class="top"><a class="brand" href="{up}index.html">🚗 Polestar4 오버레이 랩</a></header>
<div class="wrap"><aside class="side">{navp}</aside>
<main class="content">{md_to_html(body)}</main></div>
<footer class="foot">© {year} Polestar4 오버레이 랩 · 지니(Genie)와 함께 만든 기록</footer>
</body></html>'''
            dst = os.path.join(OUT, relhtml)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'w', encoding='utf-8').write(doc)
            pages.append(relhtml)
    # index.html from content/index.md if present, else list
    idx_src = os.path.join(CONTENT, 'index.md')
    if os.path.exists(idx_src):
        meta, body = parse(idx_src)
        doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Polestar4 오버레이 랩</title>
<link rel="stylesheet" href="assets/style.css"></head><body>
<header class="top"><a class="brand" href="index.html">🚗 Polestar4 오버레이 랩</a></header>
<div class="wrap"><aside class="side">{nav}</aside>
<main class="content">{md_to_html(body)}</main></div>
<footer class="foot">© {year} Polestar4 오버레이 랩 · 지니(Genie)와 함께 만든 기록</footer>
</body></html>'''
        open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(doc)
    src_assets = os.path.join(ROOT, "assets")
    if os.path.isdir(src_assets):
        shutil.copytree(src_assets, os.path.join(OUT, "assets"))
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('built', len(pages) + 1, 'pages')

if __name__ == '__main__':
    main()
