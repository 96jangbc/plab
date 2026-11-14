---
title: Overlay Keyboard
---
# ⌨️ Overlay Keyboard

**Turn the car's built-in keyboard into a floating half-width keyboard.** Position, size and opacity are all adjustable in real time.

## What it is
The Polestar 4's stock keyboard takes up the **entire screen width**. Type one character in a search box and the whole bottom half of the screen is gone. This app floats a keyboard at **half the screen width**, so you can type while still seeing the content behind it.

As in the screenshot, it appears as a **half-width card** above the search field, and expands up to 95% when needed.

![Overlay keyboard running](../../assets/img/kboverlay-1.jpg)

## Features
- **Half-width (1/2) floating keyboard** — 50% by default, 95% when expanded
- **Hangul composition** — choseong/jungseong/jongseong, compound vowels (ㅘㅙㅚㅝㅞㅟㅢ), double finals (ㄳㄵㄺㅄ …)
- **⇧ double-consonant linkage** — the row actually changes to `ㅃㅉㄸㄲㅆ` and active keys are highlighted by color
- **8 display settings** — theme / font weight / font size / horizontal position / bottom margin / opacity / width / key height
- **Everything updates live** — move a slider and the keyboard changes instantly

## Usage
1. Open the app → **"Enable keyboard"** → turn on "Overlay Keyboard" in the list
2. **"Select overlay keyboard"** → pick it in the picker
3. Tap any input field and the half-width keyboard appears

## Style
Two themes. Light is the stock look (light gray keys, dark text); dark is a borderless deep gray.

| | Light | Dark |
|---|---|---|
| Card | #F4F5F7 | #16191E |
| Keys | #E9EAEC | #2A2F37 |
| Text | Black | White |

## Lessons learned

### 1) Backspace "sometimes" not working — the real cause was final consonants
Managing Hangul composition state internally meant that when **the app committed the composition first**, our state drifted out of sync and nothing happened.

The deeper bug: **single final consonants were left in place**, so deleting `안` returned `안` again — looking like nothing happened.

```
안 → 안   (bug)
안 → 아 → ㅇㅏ → deleted   (fixed)
앉 → 안 → 아 → ㅇㅏ → deleted
값 → 갑 → 가 → ㄱㅏ → deleted
```

**Fix**: decide based on the **actual text on screen**, not internal state. Step down one level: final → vowel → initial → delete.

### 2) Long-press kept deleting after release
Repeat work was stored in the view's `setTag`, so rapid taps **overwrote the previous task** and cancellation failed.

**Fix**: a single global handler for repeats, always stopped on touch-up or when the keyboard hides.

### 3) 100% opacity still showed through
The slider only changed the card alpha, but **the key colors themselves had alpha baked in (90%, 30%)**, so even 100% was translucent.

**Fix**: made every color fully opaque (FF) so the slider is the only opacity control.

### 4) An overlay IME is a full-width window with a transparent background
The input method window must span the full width; we draw a **transparent background with a half-width card on top**. The window background must be transparent and `setDimAmount(0)` turns off the surrounding dim.

## Notes
- Built on Android's IME (InputMethodService), so it **behaves like a system keyboard**
- Polestar 4 runs `targetSdk 22`, so no extra permission prompts are needed
- You can always switch back to the stock keyboard in settings
