"""1단계 후보 조회 (BE-1)."""

from .schemas import Candidate


async def fetch_candidates(age: str, kdc: list[str], k: int = 30) -> list[Candidate]:
    """연령·분야별 최근 1년 인기 대출에서 후보 k권을 고른다.

    - 분야마다 loanItemSrch 1회(최대 3회), 분야당 k/len(kdc)권씩
    - 부가기호 첫 자리 5·6·7(학습참고서·아동)은 뺀다
    - (정규화한 서명, 저자)가 같으면 vol이 비었거나 1인 권, 그다음 대출이 많은 권만 남긴다
    - 실패하면 UpstreamUnavailable("data4library")
    """
    raise NotImplementedError
