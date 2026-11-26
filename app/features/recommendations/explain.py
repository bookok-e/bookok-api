"""5단계 추천 이유 생성·검사 (BE-3)."""

from .schemas import Pick, Reason


async def explain(concern: str, picks: list[Pick]) -> list[Reason]:
    """책마다 고민과 연결한 추천 이유를 만든다. picks와 같은 순서로 돌려준다.

    예외를 던지지 않는다. LLM 실패나 검사 실패(입력에 없는 고유명사·숫자)면
    그 책은 type="template" 문장으로 바꾼다.
    """
    raise NotImplementedError
