"""단계 함수를 가짜로 바꿔 service.py의 연결·대체 규칙과 API 계약을 확인한다.

각 단계를 실제로 구현하면 그 단계의 테스트는 같은 폴더에 따로 둔다.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.core.errors import UpstreamUnavailable
from app.features.recommendations import books, candidates, explain, rank, repository
from app.features.recommendations.schemas import Book, Candidate, Pick, Reason, RecommendRequest
from app.features.recommendations.service import recommend
from app.main import app

BOOKS = [
    Book(isbn13=f"97911000000{i:02d}", title=f"책{i}", author="저자", publisher="출판사",
         cover_url="c", buy_url="b", pages=200, loan_count=100 - i)
    for i in range(5)
]
REQ = RecommendRequest(age_group="30", kdc=["1", "8"], page_range="any", concern="이직 고민")


@pytest.fixture
def fakes(monkeypatch):
    saved = {}

    async def fetch_candidates(age, kdc, k=30):
        return [Candidate(isbn13=b.isbn13, title=b.title, authors="저자", loan_count=b.loan_count, ranking=i + 1)
                for i, b in enumerate(BOOKS)]

    async def fetch_books(cands):
        return BOOKS

    async def rank_(concern, books_, n=3):
        return [Pick(book=b, score=0.9 - i / 10) for i, b in enumerate(reversed(books_))][:n]

    async def explain_(concern, picks):
        return [Reason(isbn13=p.book.isbn13, text=f"{p.book.title} 이유", type="llm") for p in picks]

    async def save(request_id, req, picks, reasons, meta):
        saved.update(request_id=request_id, meta=meta, picks=picks)

    monkeypatch.setattr(candidates, "fetch_candidates", fetch_candidates)
    monkeypatch.setattr(books, "fetch_books", fetch_books)
    monkeypatch.setattr(books, "filter_pages", lambda b, r: b)
    monkeypatch.setattr(rank, "rank", rank_)
    monkeypatch.setattr(explain, "explain", explain_)
    monkeypatch.setattr(repository, "save_recommendation", save)
    return saved


def test_normal_flow_uses_embedding_rank(fakes):
    res = asyncio.run(recommend(REQ))
    assert [i.isbn for i in res.items] == [BOOKS[4].isbn13, BOOKS[3].isbn13, BOOKS[2].isbn13]
    assert res.concern_applied is True
    assert fakes["meta"].selection == "embedding"
    assert fakes["request_id"] == res.request_id


def test_embedding_failure_falls_back_to_loan_order(fakes, monkeypatch):
    async def broken(concern, books_, n=3):
        raise UpstreamUnavailable("embedding")

    monkeypatch.setattr(rank, "rank", broken)
    res = asyncio.run(recommend(REQ))
    assert [i.isbn for i in res.items] == [b.isbn13 for b in BOOKS[:3]]
    assert res.concern_applied is False
    assert fakes["meta"].selection == "loan_order"
    assert fakes["meta"].degraded == ["embedding"]
    assert all(p.score is None for p in fakes["picks"])


def test_save_failure_still_returns_result(fakes, monkeypatch):
    async def broken(*args):
        raise RuntimeError("db down")

    monkeypatch.setattr(repository, "save_recommendation", broken)
    res = asyncio.run(recommend(REQ))
    assert len(res.items) == 3


def test_api_is_camel_case(fakes):
    body = TestClient(app).post("/api/recommendations", json={
        "ageGroup": "30", "kdc": ["1"], "pageRange": "any", "concern": "고민"}).json()
    assert set(body) == {"requestId", "concernApplied", "items", "relaxSuggestions"}
    assert set(body["items"][0]) == {"isbn", "title", "author", "coverUrl", "pages", "reason", "reasonType", "buyUrl"}


@pytest.mark.parametrize("payload, field", [
    ({"ageGroup": "30s", "kdc": ["1"], "pageRange": "any", "concern": "x"}, "ageGroup"),
    ({"ageGroup": "30", "kdc": ["1", "1"], "pageRange": "any", "concern": "x"}, "kdc"),
    ({"ageGroup": "30", "kdc": ["1"], "pageRange": "any", "concern": ""}, "concern"),
])
def test_invalid_input_is_400(payload, field):
    res = TestClient(app).post("/api/recommendations", json=payload)
    assert res.status_code == 400
    assert res.json() == {"error": "invalid_input", "field": field}


def test_upstream_failure_is_503(fakes, monkeypatch):
    async def broken(age, kdc, k=30):
        raise UpstreamUnavailable("data4library")

    monkeypatch.setattr(candidates, "fetch_candidates", broken)
    res = TestClient(app).post("/api/recommendations", json={
        "ageGroup": "30", "kdc": ["1"], "pageRange": "any", "concern": "고민"})
    assert res.status_code == 503
    assert res.json() == {"error": "upstream_unavailable"}
