---
title: OpenCode Go Model Analysis & Picks
---
# 🤖 OpenCode Go Model Analysis & Picks

Notes on which models are worth using on **OpenCode Go** (a $10/mo subscription for coding agents),
judged from the point of view of an **always-on AI assistant (agent)** — i.e. what is *efficient*.

## What "efficient" means here
In long sessions an agent **re-reads its context** every turn, so the real cost is driven by the **cache-read price**.

1. **Cache-read price** (most important)
2. **Monthly limit headroom**
3. **Image support** (screenshot analysis)
4. **Context size**
5. **Korean language quality**
6. **Privacy** (not used for training)

## Models at a glance (Go)
| Model | In/Out ($/1M) | Cache read | Monthly limit | Note |
|---|---|---|---|---|
| **DeepSeek V4.1 Flash** | 0.15 / 0.60 | **0.003** | $60 | cheapest cache · image · 1M |
| GLM-5.3-Flash | 0.15 / 0.50 | 0.03 | $60 | cheap · strong at code |
| Mimo-V2.6-Flash | 0.14 / 0.28 | 0.0028 | $60 | ultra-cheap bulk |
| GPT 6 Luna | 0.10 / 0.50 | 0.01 | $15 | small limit |
| Claude Haiku 5.5 | 0.10 / 0.50 | 0.01 | $15 | small limit |
| Kimi K3 | 3.00 / 15.00 | 0.30 | $15 | smartest · pricey |
| GLM-5.3 | 1.40 / 4.40 | 0.26 | $15 | high performance |
| Grok 4.7 / 4.6 | 2.00 / 6.00 | 0.50 | $15 | pricey |
| LongCat 2.5 / Step 5 Preview | free | — | unlimited | limited-time free |

## Conclusion (by use case)
- **Main · always-on agent**: `deepseek-v4.1-flash` — cheapest cache + $60 limit + image + 1M context
- **Coding tasks**: `kimi-k2.7-code` (code-specialized, $60 limit)
- **Automations / bulk**: `glm-5.3-flash` or `mimo-v2.6-flash` to spread the quota
- **Hard reasoning only**: `kimi-k3` · `glm-5.3` (only $15/mo — use sparingly)
- **Avoid**: `muse-spark-1.2/1.3-contributor` — prompts are used to train models ⚠️

## Privacy
- Most models are **not used for training**. DeepSeek is **ZDR (0-day retention)**; Grok/GPT/Claude keep data 30 days for abuse monitoring.
- ⚠️ **Muse Spark Contributor** uses your prompts and outputs to **train Meta models** (hence the steep discount).

## Notes
- Model ID format: `opencode-go/<model-id>` (e.g. `opencode-go/kimi-k3`)
- Quota rule: per-model monthly dollar limit = **20% per 5h · 50% weekly · 100% monthly**
- Docs: <https://opencode.ai/docs/ko/go/>

> This reflects the state of things when written. Models, prices, and limits change often — check the docs.
