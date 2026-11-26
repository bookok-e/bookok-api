"""추천 기능의 계약. 내부 타입은 snake_case, API 스키마만 CamelModel.

필드나 시그니처를 바꾸려면 BE 3명이 합의한다(docs/05-roles.md).
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.schema import CamelModel

AgeGroup = Literal["20", "30", "40", "50", "60"]  # 정보나루 연령 코드
Kdc = Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]  # KDC 대주제
PageRange = Literal["0-200", "201-350", "351+", "any"]


# ---- 내부 타입 (단계 함수 사이의 계약) ----

class Candidate(BaseModel):
    """정보나루 loanItemSrch doc 1건."""

    isbn13: str
    title: str  # bookname
    authors: str
    vol: str | None = None  # 권차, 시리즈가 아니면 None
    class_no: str | None = None  # KDC, 빈 값 있음
    addition_symbol: str | None = None  # ISBN 부가기호(첫 자리 5·6·7 = 학습참고서·아동)
    loan_count: int
    ranking: int  # 동순위 있음


class Book(BaseModel):
    """예스24 itemDetail(detail=Y) 1건 + 대출 정보."""

    isbn13: str
    title: str
    author: str
    publisher: str
    cover_url: str  # cover (정보나루 bookImageURL은 쓰지 않음)
    buy_url: str  # link
    intro: str | None = None  # contentDetail.bookIntroduction
    toc: str | None = None  # contentDetail.tableOfContents
    pages: int | None = None  # detail=Y에서만 옴
    loan_count: int  # Candidate에서 이어받음(대출순 대체용)


class Pick(BaseModel):
    book: Book
    score: float | None = None  # 대출순 대체면 None


class Reason(BaseModel):
    isbn13: str
    text: str
    type: Literal["llm", "template"]


class RunMeta(BaseModel):
    """recommendation_request 행에 남기는 실행 정보."""

    selection: Literal["embedding", "loan_order"]
    embedding_model: str | None = None
    llm_model: str | None = None
    latency_ms: int
    degraded: list[str] = Field(default_factory=list)


# ---- API 스키마 (docs/03-api-spec.md) ----

class RecommendRequest(CamelModel):
    age_group: AgeGroup
    kdc: list[Kdc] = Field(min_length=1, max_length=3)
    page_range: PageRange
    concern: str = Field(min_length=1)  # 길이 상한은 팀 결정

    @field_validator("kdc")
    @classmethod
    def unique_kdc(cls, v: list[str]) -> list[str]:
        if len(set(v)) != len(v):
            raise ValueError("kdc must be unique")
        return v


class RecommendItem(CamelModel):
    isbn: str
    title: str
    author: str
    cover_url: str
    pages: int | None
    reason: str
    reason_type: Literal["llm", "template"]
    buy_url: str


class RelaxSuggestion(CamelModel):
    field: str
    value: str
    extra_count: int


class RecommendResponse(CamelModel):
    request_id: UUID
    concern_applied: bool
    items: list[RecommendItem]
    relax_suggestions: list[RelaxSuggestion] = Field(default_factory=list)
