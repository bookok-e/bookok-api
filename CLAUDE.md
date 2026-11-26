# bookok-api

독서 추천 서비스 백엔드(FastAPI). 기획·설계는 `docs/`, 계약의 기준은 코드다.

## 명령

- 설치: `uv sync`
- 테스트: `uv run pytest` (기능 하나만: `uv run pytest app/features/recommendations`)
- 실행: `uv run uvicorn app.main:app --reload`
- OpenAPI 재생성: `uv run python -m app.openapi_export > openapi.json` (API 스키마를 바꾸면 필수, 테스트가 확인)

## 구조와 의존 규칙

- `app/features/<기능>/`: router, schemas, service, 단계 파일, tests를 한 폴더에
- `app/integrations/<외부 API>/`: 기능끼리 공유하는 외부 API 클라이언트와 `fixtures/`
- `app/core/`: 설정, 공통 스키마(`CamelModel`), 오류(`UpstreamUnavailable`)
- 허용 방향은 `features → integrations, core`뿐. 기능끼리 import하지 않는다

## 계약

- 추천 단계 함수의 시그니처와 `schemas.py`의 타입은 BE 3명이 합의해서만 바꾼다(`docs/05-roles.md`)
- 내부 타입은 snake_case, API 스키마는 `CamelModel`을 상속해 camelCase로 나간다. 라우터는 항상 `response_model`을 쓴다
- 외부 API 실패는 `UpstreamUnavailable(source)`로 알리고, 대체(대출순 3권 등)는 각 기능의 `service.py`에서만 한다
- `explain`은 예외를 던지지 않는다(실패하면 템플릿 이유)

## 하지 말 것

- 고민 원문(`concern`)을 로그에 남기지 않는다
- 예스24 데이터(제목·소개·목차·표지)와 임베딩 벡터를 DB에 저장하지 않는다(약관)
- 정보나루 `bookImageURL`을 쓰지 않는다(영리·AI 이용 금지)
- `openapi.json`을 손으로 고치지 않는다
- API 키를 커밋하지 않는다(`.env`, 예시는 `.env.example`)
