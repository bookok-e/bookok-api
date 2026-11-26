"""2~3단계 책 정보·쪽수 필터 (BE-2)."""

from .schemas import Book, Candidate


async def fetch_books(cands: list[Candidate]) -> list[Book]:
    """예스24 itemDetail(searchType=ISBN13, detail=Y)을 병렬로 부른다(초당 10회 이하).

    404 GOODS_002인 책은 빼고 반환, 502·504는 1회 재시도.
    전부 실패하면 UpstreamUnavailable("yes24"). 소개·목차는 원문 그대로 넘긴다.
    """
    raise NotImplementedError


def filter_pages(books: list[Book], page_range: str) -> list[Book]:
    """구간 밖의 책을 뺀다. 쪽수가 없으면 page_range가 "any"일 때만 남긴다."""
    raise NotImplementedError
