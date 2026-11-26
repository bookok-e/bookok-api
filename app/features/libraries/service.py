from .schemas import Holding


async def find_holdings(isbn13: str, dtl_region: str, limit: int = 5) -> list[Holding]:
    """libSrchByBook(isbn, region=dtl_region 앞 2자리, dtl_region, pageSize=limit) 후
    도서관마다 bookExist를 병렬로 불러 hasBook이 아닌 곳은 뺀다.

    hasBook·loanAvailable은 Y/true → True, N/false → False, 그 밖은 None으로 읽는다.
    """
    raise NotImplementedError
