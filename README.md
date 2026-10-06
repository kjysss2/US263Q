# 26.3Q 실적발표 캘린더 (GitHub Pages)

`data/calendar.json`에 등록된 2026년 3분기 실적발표 일정을 주간 그리드로 보여주는 정적 캘린더입니다. 참고 사이트와 같은 `장전 / 장후 / 시간미정` 구조를 사용합니다.

## 배포

1. GitHub 저장소에서 **Settings → Pages**로 이동합니다.
2. **Branch: main / (root)**를 선택합니다.
3. `https://kjysss2.github.io/US263Q/`에서 확인합니다.

## 일정 데이터

일정은 `data/calendar.json`에서 관리합니다.

```json
{
  "date": "2026-10-08",
  "session": "before",
  "name": "펩시코",
  "ticker": "PEP",
  "source": "https://공식-IR-출처"
}
```

- `session: before`: 장 시작 전 발표
- `session: after`: 장 마감 후 발표
- `session: tba`: 발표 세션 미확인
- `focus: true`: 반도체·장비 관련 관심주(파란 점)

현재 데이터는 2026-09-28 KST 기준으로 관리합니다. 회사가 날짜를 발표하지 않은 종목은 예상일을 임의로 넣지 않고, 공식 일정이 확인되면 `calendar.json`에 추가합니다.

## Notion Transcript 연동

사이트의 `Transcript` 링크는 Notion의 [26.3Q 미국DB](https://app.notion.com/p/0850296c0da54d53b3a62bf62ab932e0?v=c87e351e89654701aa26b8c271c116fd)에서 읽어 `data/notion-transcripts.json`에 반영합니다. 회사 페이지 제목은 `티커 - ...` 형식으로 작성하면 해당 티커와 자동으로 연결됩니다.

GitHub Actions가 비공개 Notion DB를 읽으려면 다음 준비가 필요합니다.

1. Notion에서 해당 DB를 API 연동(Integration)과 공유합니다.
2. GitHub 저장소 `US263Q`의 **Settings → Secrets and variables → Actions**에서 `NOTION_TOKEN`이라는 Repository secret을 추가합니다.
3. **Actions → Notion Transcript 링크 자동 업데이트 → Run workflow**를 눌러 즉시 실행하거나, 자동 실행을 기다립니다.

워크플로는 매시 7분, 27분, 47분(하루 종일 20분 간격)에 실행됩니다. GitHub Actions의 정각 부하를 피하기 위해 정각이 아닌 시각을 사용하며, 변경된 Transcript 데이터가 있을 때만 커밋합니다. 브라우저 화면은 5분마다 새 데이터를 다시 확인합니다.

## 참고

- 모든 `IR` 링크는 각 회사의 공식 투자자 페이지 또는 공식 발표자료로 연결됩니다.
- 사이트는 별도 빌드 과정 없이 GitHub Pages에서 `index.html`을 바로 제공합니다.
