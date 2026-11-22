#!/usr/bin/env python3
"""주간 투자 점검 기록을 파싱해 추세 그래프(SVG)를 생성한다."""
import os, re, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
WEEKLY = os.path.join(ROOT, 'content', '02-invest', 'weekly')
OUT = os.path.join(ROOT, 'assets', 'img', 'invest')

NUM = r'(-?\d+(?:\.\d+)?)'


def num(pattern, txt):
    m = re.search(pattern, txt)
    return float(m.group(1)) if m else None


def parse_file(path):
    txt = open(path, encoding='utf-8').read()
    base = os.path.basename(path)[:-3]
    try:
        d = base  # 2026-10-18
    except Exception:
        return None
    fg = num(r'\|\s*공포·탐욕 지수\s*\|\s*' + NUM, txt)
    vix = num(r'\|\s*VIX \(변동성\)\s*\|\s*' + NUM, txt)
    rsi = num(r'\|\s*RSI\(14\)[^|]*\|\s*' + NUM, txt)
    mdd = num(r'\|\s*MDD \(고점 대비\)\s*\|\s*' + NUM, txt)
    sp = None
    m = re.search(r'-\s*S&P 500 종가:\s*([\d,]+\.?\d*)', txt)
    if m:
        sp = float(m.group(1).replace(',', ''))
    ma200 = None
    # 표 행: "| 200일선 | 이탈 (6910 < 7349) | 이탈 |" — 부등호 방향이 위/이탈에 따라
    # 달라지므로 양방향 모두 받고, 괄호 안 두 번째 숫자를 200일선으로 본다.
    m = re.search(r'\|\s*200일선\s*\|[^|]*\(\s*[\d,]+\s*[<>]\s*([\d,]+)', txt)
    if m:
        ma200 = float(m.group(1).replace(',', ''))
    if ma200 is None:
        # 원자료 줄: "- 200일선: 7,348.58 · 200주선: 5793.22"
        m = re.search(r'200일선:\s*([\d,]+\.?\d*)', txt)
        if m:
            ma200 = float(m.group(1).replace(',', ''))
    sig = 0
    m = re.search(r'신호\s*(\d+)\s*/\s*5', txt)
    if m:
        sig = int(m.group(1))
    return {
        'date': base, 'fg': fg, 'vix': vix, 'rsi': rsi, 'mdd': mdd,
        'sp': sp, 'ma200': ma200, 'sig': sig,
    }


def load():
    rows = []
    for p in sorted(glob.glob(os.path.join(WEEKLY, '2026-*.md'))):
        r = parse_file(p)
        if r and r['fg'] is not None:
            rows.append(r)
    # 연속 중복 제거 (같은 값이면 같은 주차를 두 번 기록한 것)
    dedup = []
    for r in rows:
        if dedup:
            prev = dedup[-1]
            same = all(r[k] == prev[k] for k in ('fg', 'vix', 'rsi', 'mdd', 'sp', 'ma200', 'sig'))
            if same:
                continue
        dedup.append(r)
    return dedup


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def line_chart(title, series, threshold=None, threshold_label='', unit='', color='#2563eb',
               width=760, height=250, decimals=1, area=True):
    """series: [(label, value)] — 값이 None이면 건너뛴다."""
    pts = [(l, v) for l, v in series if v is not None]
    pad_l, pad_r, pad_t, pad_b = 52, 18, 34, 34
    iw = width - pad_l - pad_r
    ih = height - pad_t - pad_b

    vals = [v for _, v in pts]
    if threshold is not None:
        vals.append(threshold)
    lo, hi = min(vals), max(vals)
    if hi == lo:
        hi += 1; lo -= 1
    pad = (hi - lo) * 0.12
    lo -= pad; hi += pad

    def X(i):
        if len(pts) == 1:
            return pad_l + iw / 2
        return pad_l + iw * i / (len(pts) - 1)

    def Y(v):
        return pad_t + ih * (1 - (v - lo) / (hi - lo))

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
               f'width="100%" role="img" aria-label="{esc(title)}" '
               f'style="max-width:100%;height:auto;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif">')
    out.append(f'<rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="#ffffff" stroke="#e5e7eb"/>')
    out.append(f'<text x="{pad_l}" y="22" font-size="14" font-weight="700" fill="#111827">{esc(title)}</text>')

    # y 그리드 4단
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        y = Y(v)
        out.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width-pad_r}" y2="{y:.1f}" stroke="#f1f3f5"/>')
        out.append(f'<text x="{pad_l-8}" y="{y+4:.1f}" font-size="10" fill="#9ca3af" text-anchor="end">'
                   f'{v:.{decimals}f}</text>')

    # 임계선
    if threshold is not None:
        ty = Y(threshold)
        out.append(f'<line x1="{pad_l}" y1="{ty:.1f}" x2="{width-pad_r}" y2="{ty:.1f}" '
                   f'stroke="#ef4444" stroke-width="1.4" stroke-dasharray="5 4"/>')
        label = threshold_label or f'기준 {threshold}'
        out.append(f'<text x="{width-pad_r}" y="{ty-6:.1f}" font-size="10" fill="#ef4444" '
                   f'text-anchor="end">{esc(label)}</text>')

    # 면적 + 선
    if pts:
        coords = [(X(i), Y(v)) for i, (_, v) in enumerate(pts)]
        if area and len(coords) > 1:
            d = f'M {coords[0][0]:.1f} {pad_t+ih:.1f} '
            for x, y in coords:
                d += f'L {x:.1f} {y:.1f} '
            d += f'L {coords[-1][0]:.1f} {pad_t+ih:.1f} Z'
            out.append(f'<path d="{d}" fill="{color}" opacity="0.10"/>')
        d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in coords)
        out.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="2.4" '
                   f'stroke-linejoin="round" stroke-linecap="round"/>')
        for i, ((lab, v), (x, y)) in enumerate(zip(pts, coords)):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#fff" stroke="{color}" stroke-width="2">'
                       f'<title>{esc(lab)}: {v:.{decimals}f}{esc(unit)}</title></circle>')
        # 마지막 값 강조
        lx, ly = coords[-1]
        last = pts[-1][1]
        out.append(f'<text x="{lx:.1f}" y="{ly-12:.1f}" font-size="12" font-weight="700" fill="{color}" '
                   f'text-anchor="end">{last:.{decimals}f}{esc(unit)}</text>')

    # x 라벨
    for i, (lab, _) in enumerate(pts):
        x = X(i)
        out.append(f'<text x="{x:.1f}" y="{height-12}" font-size="10" fill="#6b7280" '
                   f'text-anchor="middle">{esc(lab)}</text>')

    out.append('</svg>')
    return '\n'.join(out)


def bar_chart(title, series, max_val=5, width=760, height=250):
    pad_l, pad_r, pad_t, pad_b = 52, 18, 34, 34
    iw = width - pad_l - pad_r
    ih = height - pad_t - pad_b
    n = max(1, len(series))
    slot = iw / n

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" '
           f'role="img" aria-label="{esc(title)}" '
           f'style="max-width:100%;height:auto;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif">',
           f'<rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="#ffffff" stroke="#e5e7eb"/>',
           f'<text x="{pad_l}" y="22" font-size="14" font-weight="700" fill="#111827">{esc(title)}</text>']

    for k in range(max_val + 1):
        y = pad_t + ih * (1 - k / max_val)
        out.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width-pad_r}" y2="{y:.1f}" stroke="#f1f3f5"/>')
        out.append(f'<text x="{pad_l-8}" y="{y+4:.1f}" font-size="10" fill="#9ca3af" text-anchor="end">{k}</text>')

    for i, (lab, v) in enumerate(series):
        bw = slot * 0.46
        x = pad_l + slot * i + (slot - bw) / 2
        h = ih * (v / max_val) if max_val else 0
        y = pad_t + ih - h
        fill = '#ef4444' if v >= 3 else ('#f59e0b' if v >= 1 else '#10b981')
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h,1):.1f}" rx="4" fill="{fill}" opacity="0.85">'
                   f'<title>{esc(lab)}: {v}/5</title></rect>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" font-size="11" font-weight="700" fill="#374151" '
                   f'text-anchor="middle">{v}</text>')
        out.append(f'<text x="{pad_l+slot*i+slot/2:.1f}" y="{height-12}" font-size="10" fill="#6b7280" '
                   f'text-anchor="middle">{esc(lab)}</text>')

    out.append('</svg>')
    return '\n'.join(out)


def main():
    rows = load()
    if not rows:
        print('weekly 데이터 없음'); return
    os.makedirs(OUT, exist_ok=True)

    labels = [r['date'][5:] for r in rows]          # MM-DD

    charts = {
        'fg.svg': line_chart('공포·탐욕 지수', list(zip(labels, [r['fg'] for r in rows])),
                             threshold=20, threshold_label='매수 기준 < 20'),
        'vix.svg': line_chart('VIX 변동성 지수', list(zip(labels, [r['vix'] for r in rows])),
                              threshold=30, threshold_label='매수 기준 ≥ 30', color='#7c3aed'),
        'rsi.svg': line_chart('RSI(14) · S&P 500', list(zip(labels, [r['rsi'] for r in rows])),
                              threshold=30, threshold_label='매수 기준 ≤ 30', color='#0891b2'),
        'mdd.svg': line_chart('MDD (고점 대비 낙폭)', list(zip(labels, [r['mdd'] for r in rows])),
                              threshold=-14, threshold_label='매수 시작 ≤ -14%', unit='%', color='#dc2626'),
        'sp500.svg': line_chart('S&P 500 종가 vs 200일선', list(zip(labels, [r['sp'] for r in rows])),
                                unit='', decimals=0, color='#059669'),
        'signals.svg': bar_chart('충족 신호 수 (0~5)', list(zip(labels, [r['sig'] for r in rows]))),
    }
    for name, svg in charts.items():
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(svg)
    print(f'charts: {len(charts)}개 생성 · 데이터 {len(rows)}주치 ({rows[0]["date"]} ~ {rows[-1]["date"]})')


if __name__ == '__main__':
    main()
