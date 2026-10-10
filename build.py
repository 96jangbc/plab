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
        if name == 'en' and dirpath == CONTENT:
            continue
        full = os.path.join(dirpath, name)
        if os.path.isdir(full):
            sub = build_tree(full, (rel + '/' + name) if rel else name)
            idx = os.path.join(full, 'index.md')
            dlink = ((rel + '/' + name) if rel else name) + '/index.html' if os.path.exists(idx) else None
            items.append(('dir', name, sub, dlink))
        elif name.endswith('.md'):
            meta, _ = parse(full)
            link = (rel + '/' if rel else '') + name[:-3] + '.html'
            items.append(('file', link, title_of(meta, full)))
    return items

def render_nav(tree, prefix=""):
    out = ['<ul class="tree">']
    for item in tree:
        kind, a, b = item[0], item[1], item[2]
        dlink = item[3] if len(item) > 3 else None
        if kind == 'dir':
            label = esc(re.sub(r'^\d+[-_]','',a))
            if dlink:
                out.append('<li class="dir"><a href="%s">%s</a>%s</li>' % (esc(prefix + dlink), label, render_nav(b, prefix)))
            else:
                out.append('<li class="dir"><span>%s</span>%s</li>' % (label, render_nav(b, prefix)))
        else:
            out.append('<li class="file"><a href="%s">%s</a></li>' % (esc(prefix + a), esc(b)))
    out.append('</ul>')
    return '\n'.join(out)

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    year = datetime.date.today().year
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
                navp = render_nav(tree, up)
                is_index = (rel == 'index.md')
                if lang == 'ko':
                    toggle = ('<a class="lang" href="%sen/%s">\U0001F1FA\U0001F1F8 English</a>' % (up, relhtml)) if os.path.exists(os.path.join(EN, rel)) else ''
                    foot = "© %d jangbc's AI life · 지니(Genie)와 함께 만든 기록" % year
                else:
                    toggle = '<a class="lang" href="%s../%s">\U0001F1F0\U0001F1F7 한국어</a>' % (up, relhtml)
                    foot = "© %d jangbc's AI life · Made with 지니(Genie)" % year
                cblock = '' if is_index else comment_block.replace('{data_lang}', lang)
                ttl = t if is_index else t + " · jangbc's AI life"
                doc = f'''<!doctype html><html lang="{'ko' if lang == 'ko' else 'en'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(ttl)}</title>
<link rel="stylesheet" href="{up}assets/style.css"></head><body>
<header class="top"><a class="brand" href="{up}index.html">🧞 jangbc's AI life</a><span class="hright">{toggle}<span class="visits"><img alt="visitors" src="https://hits.sh/96jangbc.github.io/polestar-overlay-lab.svg?label=%EB%B0%A9%EB%AC%B8&amp;color=86b300&amp;labelColor=3a3f47"></span></span></header>
<div class="wrap"><aside class="side">{navp}</aside>
<main class="content">{md_to_html(body)}{cblock}</main></div>
<footer class="foot">{foot}</footer>
</body></html>'''
                dst = os.path.join(out_dir, relhtml)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'w', encoding='utf-8').write(doc)
                pages += 1
        return pages

    pages = run(KO, OUT, 'ko')
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
