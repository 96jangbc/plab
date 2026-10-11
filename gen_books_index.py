#!/usr/bin/env python3
# content/04-books/*.md 를 스캔해 읽은책 인덱스를 자동 생성한다.
import os, re
BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, 'content/04-books')
HEAD = """---
title: 읽은책
nav: Books
---
# 📚 읽은책

읽은 책을 **표지 + 간단 요약**으로 기록합니다.

## 기록 양식
- **표지** 이미지 · **제목 · 저자 · 출판사** · **한 줄 요약** + **3~5줄 요약** · **읽은 시기 / 별점**

"""
rows_ing, rows_done = [], []
for f in sorted(os.listdir(D)):
    if not f.endswith('.md') or f == 'index.md':
        continue
    p = os.path.join(D, f)
    s = open(p, encoding='utf-8').read()
    t = re.search(r'^title:\s*(.+)$', s, re.M)
    title = (t.group(1).strip() if t else f[:-3])
    a = re.search(r'\*\*저자\*\*:\s*([^|\n]+)', s)
    author = (a.group(1).strip() if a else '')
    st = re.search(r'\*\*상태\*\*:\s*([^\n]+)', s)
    status = (st.group(1) if st else '')
    rd = re.search(r'>\s*읽[^\n:]*:\s*([^\n(]+)', s)
    when = (rd.group(1).strip() if rd else '')
    star = '★★★★★' if '★★★★★' in s else ('★★★★☆' if '★★★★☆' in s else '')
    line = '- **[%s](%s.html)** — %s%s%s' % (
        title, f[:-3], author,
        (' · ' + star) if star else '',
        (' (%s)' % when) if when else '')
    (rows_ing if '읽는 중' in status else rows_done).append(line)
out = HEAD
if rows_ing:
    out += '## 📖 읽는 중\n' + '\n'.join(rows_ing) + '\n\n'
out += '## ✅ 읽은 책\n' + ('\n'.join(rows_done) if rows_done else '- (아직 없음)') + '\n'
open(os.path.join(D, 'index.md'), 'w', encoding='utf-8').write(out)
print('index generated:', len(rows_ing), 'reading /', len(rows_done), 'done')
