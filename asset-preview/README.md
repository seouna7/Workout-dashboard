# 자산 퀘스트 · 게임형 자산관리 대시보드

매일 1분, 퀘스트를 찍으며 자산·증시·적립식을 관리하는 초보자용 웹 대시보드입니다.
빌드 도구 없이 `index.html` 한 파일로 동작하고, GitHub Pages(`main` 루트)에서 바로 열립니다.

## 무엇이 들어 있나

| 영역 | 내용 |
| --- | --- |
| 히어로 | 레벨 링/XP 바, 연속 스트릭, 총자산, 비트코인 총 보유량 |
| 내 자산 한눈에 | 5개 카테고리 도넛(SVG) + 비중·금액, 행을 눌러 금액 수정 |
| 자산 추이 | 금액을 수정할 때마다 기록이 쌓이고 선 그래프로 표시 |
| 오늘의 증시 | S&P500·나스닥100·코스피·원/달러·BTC·VOO·QLD·SOXL, 전일 대비, 52주 고점 대비 위치, 30일 스파크라인 |
| 매달 14일 적립식 | 다음 적립일 D-day, VOO 80 / QLD 20 금액 분배와 주수 계산, 월별 적립 스탬프(+50 XP) |
| SOXL 레이더 | 감시선 $25, 1~4차 구간($22~23 / $19 / $16 / $13), 게이지와 단계별 체크 |
| 오늘의 1분 퀘스트 | 3종 체크(+10 XP), 도장 애니메이션, 레벨업 축하, 스트릭 |
| 1분 머니 팁 | 초보자용 팁 20개를 날짜별로 순환 |

## 데이터와 프라이버시

- 실제 자산 금액은 저장소에 **평문으로 존재하지 않습니다.** `data/vault.enc.json`은
  AES-GCM-256(PBKDF2-SHA256 200k)으로 암호화된 암호문이고, 복호화 키는 URL 조각
  `#k=...`에만 있습니다. 조각(fragment)은 서버로 전송되지 않으므로 방문 기록·서버 로그에
  키가 남지 않습니다.
- 키가 없으면 앱은 **샘플 데모 모드**(예시 1,000만 원)로 열립니다. 데모에서 수정한 값도
  이 브라우저에만 저장되어 실제 데이터와 섞이지 않습니다.
- 금액·퀘스트·XP는 `localStorage`에만 저장됩니다. 서버 전송은 없습니다.
- 상단/하단의 `JSON 내보내기·가져오기·초기화`로 백업과 복원이 가능합니다.
- `robots.txt`와 `<meta name="robots" content="noindex, nofollow">`로 검색 노출을 막았습니다.

키를 바꾸려면 저장소 밖에 시드 JSON을 두고 다음을 실행합니다.

```bash
python scripts/build_vault.py seed.json              # 새 키 생성
python scripts/build_vault.py seed.json --key KEY    # 기존 키 유지
```

## 증시 데이터 자동 갱신

- `scripts/update_market.py`가 yfinance로 지수·환율·ETF 시세를 받아 `data/market.json`을
  다시 씁니다.
- `.github/workflows/update-market.yml`이 하루 두 번(한국 장 마감 후 07:40 UTC, 미국 장 마감
  후 22:30 UTC) 실행하고 `contents: write`로 결과를 커밋합니다. 수동 실행은
  `Actions → update-market → Run workflow`.
- 브라우저는 `market.json`을 1분 캐시로 읽고, 실패하면 마지막 캐시로 표시합니다.

## 배포

`Settings → Pages → Build and deployment → Source: Deploy from a branch → main / (root)`.
