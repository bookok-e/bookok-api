"""4단계 임베딩 유사도 순위 (BE-3)."""

from .schemas import Book, Pick


async def rank(concern: str, books: list[Book], n: int = 3) -> list[Pick]:
    """고민과 책(제목·소개·목차 앞부분)을 한 번에 임베딩해 코사인 유사도 상위 n권.

    벡터는 요청이 끝나면 버린다(저장 금지). 실패하면 UpstreamUnavailable("embedding").
    """
    raise NotImplementedError
