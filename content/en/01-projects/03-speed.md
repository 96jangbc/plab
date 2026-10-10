---
title: Speeding Alert
---
# 🚦 Speeding Alert

An overlay that shows your current speed large and warns you with **color and sound** when you go over the limit you set.

## What is this app?
For when it's hard to keep glancing at the speed on the cluster, this shows big digits on the screen and lets you know with **red + a beep** when you go over **the limit you set**. (It's based on "your own speed," not on speed-camera locations.)

## Key features
- Shows the current speed (km/h) large
- Over the limit: **screen turns red + beep** (every 3 seconds)
- Limit presets: 30/50/60/80/100 · ±5 (the actual warning starts at a tolerance of +3 km/h)

## How to use
1. Launch the app → pick the limit you want → turn on the overlay
2. While driving, it warns automatically when you exceed the limit

## Technical notes
- Speed: use the larger of `PERF_VEHICLE_SPEED` (m/s) / `PERF_VEHICLE_SPEED_DISPLAY` (km/h)
- Note: this doesn't only warn in front of a camera — it alerts whenever you go over the limit
