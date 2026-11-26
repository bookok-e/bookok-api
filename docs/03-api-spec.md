# API 명세

백엔드(FastAPI)가 프런트엔드에 여는 API 요약이다. 기준은 백엔드 OpenAPI(`openapi.json`)이고, 코드 값은 정보나루 코드 체계(Open API 탭)를 따른다.

## 엔드포인트

| 메서드·경로 | 역할 |
| --- | --- |
| `POST /api/recommendations` | 추천 결과 |
| `GET /api/books/{isbn}/libraries?region=` | 소장 도서관·대출 가능 여부 |
| `POST /api/feedback` | 추천 피드백(책별 좋아요/별로, 책당 1회) |
| `POST /api/clicks` | 링크 클릭 기록(구매·소장 도서관) |

## 추천

```json
// POST /api/recommendations 요청
{
  "ageGroup": "30",
  "kdc": ["1", "8"],
  "pageRange": "201-350",
  "concern": "이직을 고민 중인데 용기가 나지 않아요"
}
```

```json
// 응답 200
{
  "requestId": "6f1c2e7a-…",
  "concernApplied": true,
  "items": [
    {
      "isbn": "9791100000000",
      "title": "…",
      "author": "…",
      "coverUrl": "…",
      "pages": 248,
      "reason": "…",
      "reasonType": "llm",
      "buyUrl": "…"
    }
  ],
  "relaxSuggestions": [
    { "field": "pageRange", "value": "any", "extraCount": 4 }
  ]
}
```

**요청 필드**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `ageGroup` | string | 필수 | 정보나루 연령 코드: 20 / 30 / 40 / 50 / 60(60세 이상) |
| `kdc` | string\[\] (1\~3개) | 필수 | KDC 대주제 코드 0\~9, 중복 없이 |
| `pageRange` | string | 필수 | `0-200` / `201-350` / `351+` / `any` |
| `concern` | string | 필수 | 고민. 빈 문자열 불가, 길이 상한은 팀 결정 |

**응답 필드**

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `requestId` | string(uuid) | 추천 요청 ID. 피드백·클릭에 씀 |
| `concernApplied` | boolean | `false`면 임베딩 장애로 대출순 3권(프런트는 고민 미반영을 알림) |
| `items` | Item\[\] (0\~3개) | 추천 책, 순위 순 |
| `items[].isbn` | string(13자리) | ISBN-13 |
| `items[].title` | string | 제목 |
| `items[].author` | string | 저자 |
| `items[].coverUrl` | string(URL) | 예스24 표지 |
| `items[].pages` | integer \| null | 쪽수. 예스24에 없으면 `null` |
| `items[].reason` | string | 추천 이유 |
| `items[].reasonType` | string | `llm` / `template`(LLM 장애·검사 실패 시 템플릿 문장) |
| `items[].buyUrl` | string(URL) | 예스24 상품 상세 링크. 출처 표기와 함께 표시 |
| `relaxSuggestions` | RelaxSuggestion\[\] | 결과가 3권 미만일 때만 채움, 아니면 빈 배열 |
| `relaxSuggestions[].field` | string | 넓힐 입력 필드 이름(예: `pageRange`) |
| `relaxSuggestions[].value` | string | 바꿀 값 |
| `relaxSuggestions[].extraCount` | integer | 그렇게 바꾸면 늘어나는 권수 |

## 소장 도서관

```json
// GET /api/books/9791100000000/libraries?region=11230 응답 200
{
  "status": "ok",
  "baseDate": "2026-11-23",
  "libraries": [
    { "name": "…도서관", "address": "…", "homepage": "…", "loanAvailable": true }
  ]
}
```

**요청**

| 위치 | 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- | --- |
| 경로 | `isbn` | string(13자리) | 필수 | 추천 결과의 ISBN |
| 쿼리 | `region` | string | 필수 | 정보나루 세부지역 코드 5자리(dtl\_region, 코드표에 있는 값만). 동네를 입력했고 사용자가 책의 소장 도서관을 펼칠 때만 호출 |

**응답 필드**

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `status` | string | `ok` / `none`(소장처 없음) / `unavailable`(정보나루 장애) |
| `baseDate` | string(YYYY-MM-DD) | 대출 가능 여부 기준일(전날) |
| `libraries` | Library\[\] (0\~5개) | 소장 도서관 |
| `libraries[].name` | string | 도서관 이름 |
| `libraries[].address` | string | 주소 |
| `libraries[].homepage` | string(URL) \| null | 도서관 홈페이지. 클릭 target=library가 이동하는 곳 |
| `libraries[].loanAvailable` | boolean | `baseDate` 기준 대출 가능 여부 |

## 추천 피드백

```json
// POST /api/feedback 요청
{
  "requestId": "6f1c2e7a-…",
  "isbn": "9791100000000",
  "vote": "up"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `requestId` | string(uuid) | 필수 | 추천 응답의 `requestId` |
| `isbn` | string(13자리) | 필수 | 그 추천에 있던 책 |
| `vote` | string | 필수 | `up`(좋아요) / `down`(별로) |

- 성공하면 204(본문 없음). 책당 1회, 수정·취소 없음. 추천 조건은 서버가 저장된 요청에서 찾으므로 보내지 않는다

## 링크 클릭

```json
// POST /api/clicks 요청
{
  "requestId": "6f1c2e7a-…",
  "isbn": "9791100000000",
  "target": "buy"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `requestId` | string(uuid) | 필수 | 추천 응답의 `requestId` |
| `isbn` | string(13자리) | 필수 | 누른 링크의 책 |
| `target` | string | 필수 | `buy`(예스24) / `library`(소장 도서관) |

- 성공하면 204(본문 없음). 같은 책을 여러 번 눌러도 매번 기록한다
- 프런트는 `navigator.sendBeacon`으로 보내고 응답을 기다리지 않는다. 실패해도 이동은 막지 않는다

## 공통 규칙·오류

| HTTP | 경우 | 본문 |
| --- | --- | --- |
| 400 | 입력 검증 실패 | `{"error": "invalid_input", "field": "kdc"}` |
| 429 | 요청 제한 초과 | `{"error": "rate_limited"}` |
| 503 | 외부 API 장애로 결과를 만들 수 없음 | `{"error": "upstream_unavailable"}` |
| 404 | 피드백·클릭 대상 추천·도서가 없음 | `{"error": "not_found"}` |
| 409 | 같은 책에 피드백을 이미 보냄 | `{"error": "already_submitted"}` |

- **필드 표기**: JSON 필드는 camelCase다. 백엔드 스키마는 공통 베이스 모델(`alias_generator=to_camel`, `populate_by_name=True`)을 상속하고, 응답은 항상 `response_model`로 돌려준다(dict를 직접 반환하면 snake\_case가 섞임). 값(`invalid_input`, `loan_order` 등)과 쿼리 파라미터(`region`)는 그대로 쓴다
- 입력 검증은 서버에서도 하고, IP 기준 요청 제한을 둔다(IP·사용자 식별자는 저장하지 않음)
- 일부 장애는 오류 대신 200으로 돌려주고 필드로 알린다(`concernApplied`, `status: unavailable`)
