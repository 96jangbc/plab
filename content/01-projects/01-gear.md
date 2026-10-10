---
title: 기어 오버레이
---
# 🧭 기어 오버레이
- **패키지**: `com.jangbc.gearoverlay` · **최종 버전**: v0.7.1
- **표시**: R N D P + **H**(오토홀드)
## 기능
- 기어 표시 + 변속 알람(내 음원), 폴링 250ms
- 오토홀드(H): 바퀴 정지(WHEEL_TICK)+D/R 기어로 감지 → H 형광노랑(#CCFF00)
## 기술 포인트
- `GEAR_SELECTION` 리플렉션 (raw 1=N 2=R 4=P 8=D)
- 오토홀드 표준 속성 없음 → 바퀴 회전으로 합성

## 스크린샷

![기어 오버레이 R N D P H](../assets/img/gear-1.jpg)
