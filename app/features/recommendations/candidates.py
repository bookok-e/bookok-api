"""1단계 후보 조회 (BE-1)."""

from .schemas import Candidate


async def fetch_candidates(age: str, kdc: list[str], k: int = 30) -> list[Candidate]:
    """연령·분야별 최근 1년 인기 대출에서 후보 k권을 고른다.

    - 분야마다 loanItemSrch 1회(최대 3회, pageSize=60)
    - 후보는 분야 수와 상관없이 총 k권. 분야당 k // len(kdc)권(나머지는 앞 분야부터 1권씩)을
      대출순으로 고르고, 거른 뒤 부족한 분야의 몫은 다른 분야의 다음 순위로 채운다
    - 부가기호 첫 자리 5·6·7(학습참고서·아동)은 뺀다
    - (정규화한 서명, 저자)가 같으면 vol이 비었거나 1인 권, 그다음 대출이 많은 권만 남긴다
    - 최종 3권은 rank가 분야와 상관없이 유사도로 고른다(분야별 몫 없음)
    - 실패하면 UpstreamUnavailable("data4library")
    """
    raise NotImplementedError
