#!/usr/bin/env python3
import subprocess, json, datetime, os
JOBS = {
  "02-invest/us-market": ("761e4c4e-74a4-4100-acba-385245542828", "미국 증시"),
  "01-tech/pem":  ("4e3262f1-b3f4-4641-ad29-279851d25a6a", "PEM 수전해"),
}
base = os.path.dirname(os.path.abspath(__file__))
for sub, (jobid, label) in JOBS.items():
    try:
        out = subprocess.run(["openclaw","automations","runs",jobid], capture_output=True, text=True, timeout=90).stdout
        d = json.loads(out)
    except Exception as e:
        print(sub, "fetch fail", e); continue
    d2 = os.path.join(base, "content", sub); os.makedirs(d2, exist_ok=True)
    seen = set()
    for e in d.get("entries", []):
        summ = (e.get("summary") or "").strip()
        if not summ: continue
        day = datetime.datetime.fromtimestamp(e["ts"]/1000).strftime("%Y-%m-%d")
        if day in seen: continue
        seen.add(day)
        fp = os.path.join(d2, day + ".md")
        if os.path.exists(fp): continue
        open(fp,"w",encoding="utf-8").write(f"---\ntitle: {label} {day}\n---\n\n{summ}\n")
    print(sub, "ok")
