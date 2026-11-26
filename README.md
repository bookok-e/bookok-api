# bookok-api

연령·분야·분량과 고민을 받아 정보나루 인기 대출 도서 중 고민에 맞는 3권을 고르고, 추천 이유·소장 도서관·구매 링크와 함께 돌려주는 백엔드.

- 기획·설계: [docs/](docs/README.md)
- 개발 규칙과 명령: [CLAUDE.md](CLAUDE.md)

## 시작하기

```bash
uv sync
cp .env.example .env   # 키 입력
uv run pytest
uv run uvicorn app.main:app --reload
```

## 현재 상태

인터페이스 계약(타입, 단계 함수 시그니처, 추천 흐름 연결)만 있다. 단계 함수는 `NotImplementedError` 스텁이며 담당은 `docs/05-roles.md`.
