#!/bin/bash
set -e
S="/Users/jangbc/.openclaw/workspace/polestar-site"; cd "$S"
python3 update_briefings.py
python3 build.py
git add -A
git -c user.name="Genie" -c user.email="genie@local" commit -m "자동 업데이트 $(date '+%Y-%m-%d %H:%M')" >/dev/null 2>&1 || { echo "변경 없음"; exit 0; }
git push origin main && echo "푸시 완료 $(date '+%F %T')"
