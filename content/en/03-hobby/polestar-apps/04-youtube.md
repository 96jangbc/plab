---
title: YouTube Overlay
---
# 📺 YouTube Overlay

Puts a **floating YouTube window** on top of the car screen. You can watch videos while driving or waiting.

## What is this app?
The car's built-in YouTube app takes over the whole screen, making it hard to watch alongside navigation. This app puts YouTube in a **small window** so you can see it layered on top of navigation.

## Key features
- Enter a YouTube link/video ID → **embed playback**, plus browsing the m.youtube.com home
- **Move** (drag header) · **resize** (pinch/◢) · **fullscreen toggle** (returns precisely to the previous size)
- Window position ▼▲ / fullscreen margin ↓↑ buttons

## How to use
1. Launch the app → turn on the overlay
2. Type a YouTube URL/ID into the address bar → play
3. ⛶ for fullscreen, ⛶ again to return to the original size

## Limitations
- **The car's built-in (native) app UI can't be placed in an overlay** → so this is built with the YouTube **web version**
- Google sign-in and DRM videos are blocked, and some videos have embed restrictions

## Technical notes
- Overlay WebView: JS + DOM storage + autoplay
- `MATCH_PARENT` windows ignore `lp.y` → fullscreen margins are adjusted via the **window's inner topMargin**

## Screenshots
![YouTube overlay zoomed in](../../assets/img/youtube-zoom.jpg)

![YouTube overlay - playing](../../assets/img/youtube-1.jpg)

![YouTube overlay - over navigation](../../assets/img/youtube-2.jpg)

![YouTube fullscreen](../../assets/img/youtube-4.jpg)

![YouTube home](../../assets/img/youtube-3.jpg)
