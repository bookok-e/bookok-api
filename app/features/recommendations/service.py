"""추천 흐름 연결 (BE-1). 장애 시 대체는 여기서만 한다."""

import logging
import time
from uuid import uuid4

from app.core.config import settings
from app.core.errors import UpstreamUnavailable

from . import books, candidates, explain, rank, repository
from .schemas import (
    Book,
    Pick,
    RecommendItem,
    RecommendRequest,
    RecommendResponse,
    RunMeta,
)

N = 3
log = logging.getLogger(__name__)


def loan_order(books_: list[Book], n: int) -> list[Pick]:
    """임베딩 장애 시 대체: 대출 많은 순 n권."""
    top = sorted(books_, key=lambda b: b.loan_count, reverse=True)[:n]
    return [Pick(book=b) for b in top]


async def recommend(req: RecommendRequest) -> RecommendResponse:
    started = time.monotonic()
    request_id = uuid4()  # 저장이 실패해도 응답에 넣기 위해 먼저 만든다
    degraded: list[str] = []

    cands = await candidates.fetch_candidates(req.age_group, req.kdc)
    found = books.filter_pages(await books.fetch_books(cands), req.page_range)

    try:
        picks = await rank.rank(req.concern, found, n=N)
        selection = "embedding"
    except UpstreamUnavailable:
        picks = loan_order(found, N)
        selection = "loan_order"
        degraded.append("embedding")

    reasons = await explain.explain(req.concern, picks)

    meta = RunMeta(
        selection=selection,
        embedding_model=settings.embedding_model if selection == "embedding" else None,
        llm_model=settings.llm_model,
        latency_ms=int((time.monotonic() - started) * 1000),
        degraded=degraded,
    )
    try:
        await repository.save_recommendation(request_id, req, picks, reasons, meta)
    except Exception:
        # 추천은 돌려주고, 이 요청의 피드백·클릭만 404가 된다
        log.exception("save_recommendation failed request_id=%s", request_id)

    by_isbn = {r.isbn13: r for r in reasons}
    items = [
        RecommendItem(
            isbn=p.book.isbn13,
            title=p.book.title,
            author=p.book.author,
            cover_url=p.book.cover_url,
            pages=p.book.pages,
            reason=by_isbn[p.book.isbn13].text,
            reason_type=by_isbn[p.book.isbn13].type,
            buy_url=p.book.buy_url,
        )
        for p in picks
    ]
    # relax_suggestions(결과 N권 미만일 때 조건 완화 제안)는 아직 없음: API 명세 참고
    return RecommendResponse(
        request_id=request_id,
        concern_applied=selection == "embedding",
        items=items,
    )
