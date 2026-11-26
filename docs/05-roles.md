# 역할분담

FE 1명, BE 3명. 추천 기능(`POST /api/recommendations`) 구현에 필요한 일만 배정하고, 나머지는 미배정(TBD)으로 둔다. 백엔드는 외부 API 기준(정보나루·예스24·LLM)으로 나눠다. 폴더는 설계 문서 > 프로젝트 구조 기준.

| 담당 | 맡는 일(추천) | 폴더 |
| --- | --- | --- |
| FE | 입력 폼, 추천 결과 화면(책 카드, 고민 미반영·조건 완화 안내). mock으로 먼저 개발 | `features/recommend-form`, `features/results`, `shared/` |
| BE-1 정보나루 | 1단계 후보 조회, 추천 흐름 연결(장애 시 대체·`degraded` 기록) | `integrations/data4library`, `recommendations/` `router` `schemas` `service` `candidates` |
| BE-2 예스24 | 2\~3단계 책 정보·쪽수 필터(초당 10회 제한), 추천 결과 저장(요청·책 테이블, DB 연결, 마이그레이션) | `integrations/yes24`, `recommendations/` `books` `repository` `models`, `core`(DB), `migrations` |
| BE-3 LLM | 4단계 임베딩·유사도 3권, 5단계 추천 이유 생성·검사·템플릿, 평가 세트 | `integrations/llm`, `recommendations/` `rank` `explain` `tests/eval` |

## 미배정(TBD)

| 작업 | 폴더 | 메모 |
| --- | --- | --- |
| 소장 도서관(API·화면) | `features/libraries`(백·프런트) | 정보나루 클라이언트를 함께 씀 |
| 피드백·클릭(API·화면) | `features/engagement`(백·프런트), 피드백·클릭 테이블 | 추천 결과 저장 후 시작 가능 |
| 90일 삭제 작업 | `jobs/purge.py` | 출시 전까지 |
| 배포·서버 IP 등록 | `deploy/`, 고정 IP 서버 | 개발 중에는 하루 500건으로 충분. IP 등록은 출시 전 필수 |
|  |  |  |

## 인터페이스(0일차 고정)

BE-1의 `service.py`가 아래 함수를 차례로 부른다. 0일차에 타입과 본문이 `raise NotImplementedError`인 스텁을 커밋하고, 이후 시그니처는 BE 3명이 합의해서만 바꾼다. 내부 타입은 snake\_case다(camelCase는 API 스키마만).

**타입** (`recommendations/schemas.py`)

```python
class Candidate(BaseModel):   # 정보나루 loanItemSrch doc 1건
    isbn13: str
    title: str                # bookname
    authors: str
    vol: str | None           # 권차, 시리즈가 아니면 None
    class_no: str | None      # KDC, 빈 값 있음
    addition_symbol: str | None  # ISBN 부가기호(첫 자리 5·6·7 = 학습참고서·아동)
    loan_count: int
    ranking: int              # 동순위 있음

class Book(BaseModel):        # 예스24 itemDetail(detail=Y) 1건 + 대출 정보
    isbn13: str
    title: str                # title
    author: str               # author
    publisher: str            # publisher
    cover_url: str            # cover (정보나루 bookImageURL은 쓰지 않음)
    buy_url: str              # link
    intro: str | None         # contentDetail.bookIntroduction
    toc: str | None           # contentDetail.tableOfContents
    pages: int | None         # pages (detail=Y에서만 옴)
    loan_count: int           # Candidate에서 이어받음(대출순 대체용)

class Pick(BaseModel):
    book: Book
    score: float | None       # 대출순 대체면 None

class Reason(BaseModel):
    isbn13: str
    text: str
    type: Literal["llm", "template"]

# libraries/schemas.py (소장 조회, 담당 TBD)
class Library(BaseModel):     # libSrchByBook lib 1건
    lib_code: str
    name: str                 # libName
    address: str
    homepage: str | None

class Holding(BaseModel):
    library: Library
    loan_available: bool | None   # bookExist, 확인 실패면 None
```

**함수**

```python
# integrations/data4library/client.py (BE-1)
async def call(endpoint: str, params: dict) -> dict
# candidates.py (BE-1)
async def fetch_candidates(age: str, kdc: list[str], k: int = 30) -> list[Candidate]
# books.py (BE-2)
async def fetch_books(cands: list[Candidate]) -> list[Book]
def filter_pages(books: list[Book], page_range: str) -> list[Book]
# rank.py (BE-3)
async def rank(concern: str, books: list[Book], n: int = 3) -> list[Pick]
# explain.py (BE-3)
async def explain(concern: str, picks: list[Pick]) -> list[Reason]
# repository.py (BE-2)
async def save_recommendation(request_id: UUID, req: RecommendRequest, picks: list[Pick],
                              reasons: list[Reason], meta: RunMeta) -> None
# libraries/service.py (TBD)
async def find_holdings(isbn13: str, dtl_region: str, limit: int = 5) -> list[Holding]
```

**장애 규칙**: 외부 API 실패는 `core/errors.py`의 `UpstreamUnavailable(source)` 하나로 알린다(`source`: `data4library` / `yes24` / `embedding` / `llm`). 대체는 `service.py`에서만 한다.

| 함수 | 실패하면 | service.py의 처리 |
| --- | --- | --- |
| `fetch_candidates` | 예외 | 503 `upstream_unavailable` |
| `fetch_books` | 실패한 책은 빼고 반환, 전부 실패면 예외 | 예외면 503 |
| `rank` | 예외 | 대출순 3권(`score=None`), `degraded`에 `embedding` |
| `explain` | 예외 없음. LLM 실패·검사 실패는 내부에서 `template` | — |
| `save_recommendation` | 예외 | 로그만 남기고 응답은 그대로(그 요청의 피드백·클릭만 404) |

- `request_id`는 `service.py`가 먼저 만든다. 저장이 실패해도 응답에 넣기 위해서다
- `RunMeta`는 `selection`, `embedding_model`, `llm_model`, `latency_ms`, `degraded`를 담는다(데이터 모델의 요청 행)
- 정보나루 `call`은 `authKey`와 `format=json`(기본은 XML)을 붙이고, 3초 타임아웃. 재시도는 타임아웃·연결 오류에만 1회(호출 한도를 아끼려고). HTTP 200이어도 본문이 오류면 예외
- 예스24는 `searchType=ISBN13&detail=Y`로 부른다(쪽수는 detail=Y에서만). 404 `GOODS_002`는 그 책만 제외, 502·504는 1회 재시도
- 소개·목차를 입력 길이에 맞게 자르는 것은 BE-3, `fetch_books`는 원문 그대로 넘긴다

**정보나루 호출 규칙** (매뉴얼 v20260620, 인기대출 CSV 예시 기준)

| 함수 | 호출 | 파라미터 |
| --- | --- | --- |
| `fetch_candidates` | 분야마다 `loanItemSrch` 1회(최대 3회) | `age`(연령 코드), `kdc`(1개), `startDt`(1년 전), `pageSize=60` |
| `find_holdings` | `libSrchByBook` 1회 + 도서관마다 `bookExist`(최대 5회, 병렬) | `isbn`(isbn13 아님), `region`(세부지역 앞 2자리, 필수), `dtl_region`, `pageSize=5` / `libCode`, `isbn13` |

| CSV 열 | API 키 | `Candidate` |
| --- | --- | --- |
| 순위 | `ranking` | `ranking` |
| 서명 | `bookname` | `title` |
| 저자 | `authors` | `authors` |
| 권 | `vol` | `vol` |
| ISBN | `isbn13` | `isbn13` |
| KDC | `class_no` | `class_no` |
| 대출건수 | `loan_count` | `loan_count` |

- **분야별 호출**: `kdc=1;8`처럼 한 번에 보낼 수도 있지만, 순위가 합쳐져 문학 같은 큰 분야가 다른 분야를 밀어낼 수 있다. 분야마다 60권씩 받아 거른 뒤, 후보는 분야 수와 상관없이 총 k권(30권)으로 둔다. 분야당 k/분야 수권(나머지는 앞 분야)씩 고르고, 부족한 분야의 몫은 다른 분야의 다음 순위로 채운다. 후보를 분야 수만큼 늘리지 않는 것은 예스24 조회(초당 10회)가 응답 시간을 정하기 때문이다. 최종 3권은 분야와 상관없이 유사도로만 고른다(`;` 인코딩 문제도 피함)
- **거르기**: 부가기호 첫 자리가 5·6(학습참고서)·7(아동)인 책은 뺀다. `addCode` 파라미터 대신 서버에서 거르는 것은 부가기호가 빈 책까지 빠지지 않게 하려고
- **중복 제거**: (정규화한 서명, 저자)가 같으면 한 권만 남긴다. `vol`이 비거나 1인 권을 우선하고, 그다음 대출이 많은 권(CSV에서 '흔한남매' 1\~21권이 상위를 채움)
- **소장 조회**: `libSrchByBook`에는 대출 가능 여부가 없어 `bookExist`를 따로 부른다. `hasBook`이 아니오면 그 도서관은 뺀다. `hasBook`·`loanAvailable` 값은 `Y`/`true`는 True, `N`/`false`는 False, 그 밖은 None으로 읽는다(매뉴얼에 형식 없음)
- **호출 수**: 추천 1건은 정보나루 1\~3회, 책 한 권의 소장 조회는 최대 6회. 프런트는 사용자가 책의 '소장 도서관'을 펼칠 때만 부른다. 동네 입력 후 3권을 모두 펼치면 최대 21회라, IP 등록 전 한도(하루 500건)로는 하루 수십 건뿐이다 → 서버 IP 등록은 출시 전 필수
- **미확인**: JSON 응답의 감싸개 구조와 오류 형식은 매뉴얼에 없다. BE-1은 파서를 쓰기 전에 3개 API의 실제 응답을 받아 `integrations/data4library/fixtures/`에 둔다(CSV는 열 이름이 API와 다른 웹 다운로드 형식). 기본 URL이 `http://`로 적혀 있어 HTTPS 지원도 확인

## 혼자 개발하는 방법

- 각자 `integrations/*/fixtures/`의 샘플 응답으로 개발·테스트한다
- BE-2는 첫날 예스24 샘플 30권을 올려 BE-3이 `rank`·`explain`과 평가 세트를 바로 시작하게 한다
- FE는 API 명세 탭의 예시 응답으로 `mocks/`를 만들어 백엔드 없이 개발한다

## 0일차

| 할 일 | 담당 |
| --- | --- |
| 저장소 2개 골격, 루트 CLAUDE.md | BE-1(백엔드), FE(프런트) |
| `schemas.py` 타입과 위 함수 서명 | BE 3명 함께 |
| openapi.json 초안(추천 API)과 FE mock | BE-1, FE |
| Neon 연결 | BE-2 |
| 키 발급: 정보나루 / 예스24 / 임베딩·LLM | BE-1 / BE-2 / BE-3 |
