---
title: AAOS 오버레이 앱 개발 노트
---
# AAOS 오버레이 앱 개발 노트

폴스타 4(Android Automotive)에 사이드로드 오버레이 앱을 만들며 얻은 실전 팁.

## 1. 오버레이 권한은 targetSdk 22로
Android 12 기반 AAOS에는 "다른 앱 위에 표시" 설정 화면이 없다. `targetSdk 22`면 설치 시 `SYSTEM_ALERT_WINDOW`가 자동 부여된다. (Android 14+는 이런 낮은 target 설치를 막으므로, 차가 pre-14인지 먼저 확인)

## 2. 차량 데이터는 리플렉션으로
`android.car` 스텁에 컴파일하면 버전 차이로 런타임 크래시(`ClassNotFoundException`). `Class.forName("android.car.Car")` → `createCar` → `getCarManager("property")` 후 `VehiclePropertyIds` 필드로 ID 조회.

읽을 수 있는 것(실측): `GEAR_SELECTION`, `PERF_VEHICLE_SPEED`, `EV_BATTERY_LEVEL`, `WHEEL_TICK`, `IGNITION_STATE`, `PARKING_BRAKE_ON`, `RANGE_REMAINING` 등.
차단된 것: 도어(`DOOR_POS`)·안전벨트(`SEAT_BELT_BUCKLED`) → Signature|Privileged 권한 필요.

## 3. 오버레이 창 배치 함정
- 창은 **화면 맨 위(y=0)** 에 배치되고 차 상단 상태바가 그 위를 덮는다 → 헤더가 가려져 드래그 불가.
  → **y를 상태바 높이 이상으로 강제(clamp)** 하고, 이동 버튼도 함께 제공.
- **`MATCH_PARENT` 창은 `lp.y`를 무시**한다 → 전체화면 여백은 창 **안쪽 뷰의 topMargin**으로 조절.
- 헤더를 못 잡는 상황 대비 **버튼으로 창 이동**을 꼭 넣을 것.

## 4. WebView 영상 오버레이
- 오버레이 WebView로 유튜브 embed 재생 가능 (INTERNET, JS + DOM storage + `setMediaPlaybackRequiresUserGesture(false)`).
- **다른 네이티브 앱 UI는 오버레이에 임베드 불가** → 웹버전만 가능.
- 구글 로그인·DRM(넷플릭스 등, Widevine L1)은 WebView에서 차단. (티빙·웨이브는 재생됨)

## 5. 차량 카메라
- EVS(서라운드뷰) API는 시스템 전용 → 서드파티 불가.
- **Camera2 API**로는 열려 있음 → 실차에서 카메라 1개 접근·촬영 성공.

## 6. 텔레그램 봇 전송
- 봇은 **사용자가 `/start`** 해야 보낼 수 있다(`chat not found` 방지).
- 멀티파트 캡션은 반드시 **UTF-8 바이트**로 (`DataOutputStream.writeBytes`는 ISO-8859-1이라 한글·이모지 깨짐 → 400).
- 실패 시 **응답 본문을 표시**하면 진단이 빠르다.
