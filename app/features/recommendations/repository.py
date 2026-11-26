"""추천 결과 저장 (BE-2). 테이블은 docs/02-design.md > 데이터 모델."""

from uuid import UUID

from .schemas import Pick, Reason, RecommendRequest, RunMeta


async def save_recommendation(
    request_id: UUID,
    req: RecommendRequest,
    picks: list[Pick],
    reasons: list[Reason],
    meta: RunMeta,
) -> None:
    """요청 1행과 책 행을 한 트랜잭션으로 쓴다. 실패하면 예외(service가 로그만 남김)."""
    raise NotImplementedError
