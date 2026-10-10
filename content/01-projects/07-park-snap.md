---
title: 주차 스냅샷
---
# 📷 주차 스냅샷
- **패키지**: `com.jangbc.parksnap` · **최종 버전**: v0.4.2
## 기능
- P 기어 진입 → 카메라 촬영 → 텔레그램 전송(+ 위치 핀 + 지도 링크)
## 배운 것
- 카메라: EVS는 시스템 전용, **Camera2로 접근 가능**(실차 성공)
- 도어(DOOR_POS)는 Signature|Privileged → **P 진입** 트리거로 대체
- 텔레그램 실패 3연타: /start 안함 · 토큰 오타 · 캡션 UTF-8

## 스크린샷

![차량 카메라 촬영 성공(진단)](../assets/img/parksnap-cam.jpg)

![텔레그램 전송 성공](../assets/img/parksnap-tg1.jpg)

![주차 위치(지도)까지 전송](../assets/img/parksnap-tg2.jpg)
