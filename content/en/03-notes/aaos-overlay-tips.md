---
title: AAOS Overlay App Development Notes
---
# AAOS Overlay App Development Notes

Hands-on tips from building sideloaded overlay apps for the Polestar 4 (Android Automotive).

## 1. Use targetSdk 22 for overlay permission
Android 12-based AAOS has no "Display over other apps" settings screen. With `targetSdk 22`, `SYSTEM_ALERT_WINDOW` is granted automatically at install. (Android 14+ blocks installing with such a low target, so first check whether your car is pre-14.)

## 2. Access vehicle data via reflection
Compiling against the `android.car` stub causes runtime crashes (`ClassNotFoundException`) due to version differences. Use `Class.forName("android.car.Car")` → `createCar` → `getCarManager("property")`, then look up the ID via the `VehiclePropertyIds` field.

What you can read (measured): `GEAR_SELECTION`, `PERF_VEHICLE_SPEED`, `EV_BATTERY_LEVEL`, `WHEEL_TICK`, `IGNITION_STATE`, `PARKING_BRAKE_ON`, `RANGE_REMAINING`, and more.
What's blocked: doors (`DOOR_POS`) · seat belts (`SEAT_BELT_BUCKLED`) → these require Signature|Privileged permission.

## 3. Overlay window placement pitfalls
- The window is placed at the **very top of the screen (y=0)** and the car's top status bar covers it → the header is hidden and can't be dragged.
  → **Force (clamp) y to at least the status bar height**, and also provide move buttons.
- **A `MATCH_PARENT` window ignores `lp.y`** → control fullscreen margins with the **topMargin of the inner view**.
- Always include **button-based window movement** for when the header can't be grabbed.

## 4. WebView video overlays
- YouTube embeds can play in an overlay WebView (INTERNET, JS + DOM storage + `setMediaPlaybackRequiresUserGesture(false)`).
- **Other native app UIs can't be embedded in the overlay** → only web versions work.
- Google sign-in and DRM (Netflix, etc., Widevine L1) are blocked in WebView. (TVING and Wavve do play)

## 5. Vehicle camera
- The EVS (surround view) API is system-only → not available to third parties.
- The **Camera2 API** is open → successfully accessed and captured from one camera on the real car.

## 6. Telegram bot sending
- The bot can only send after **the user runs `/start`** (prevents `chat not found`).
- Multipart captions must always be **UTF-8 bytes** (`DataOutputStream.writeBytes` uses ISO-8859-1, which mangles Korean and emoji → 400).
- On failure, **displaying the response body** makes diagnosis much faster.
