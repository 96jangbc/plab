---
title: Shortcut Dock
---
# 🔗 Shortcut Dock

A **shortcut dock** floating on the screen. Keep your app icons together and launch them with a single tap.

## What is this app?
To open an app you use often, you have to dig through the app list every time. This app floats your **favorite apps like a dock**, so you can launch them with one tap.

## Key features
- Pick from the installed app list to add to the dock / remove with ✕
- Set the **grid (rows × columns)**: 1–8 rows × 1–6 columns
- Shows icon + name, drag the header to move · pinch to resize

## How to use
1. Launch the app → "Load installed apps" → tap the apps you want
2. Adjust the grid with "rows/columns +−"
3. Turn on the overlay → tap a dock button → the app launches

## Technical points
- With overlay permission, you can **launch other apps (launcher intent)**
- Query the app list with `queryIntentActivities(MAIN/LAUNCHER)`
- If there are more shortcuts than slots, it shows "+N (not enough slots)"
