"""정보나루 Open API 클라이언트 (BE-1). 호출 규칙은 docs/05-roles.md."""


async def call(endpoint: str, params: dict) -> dict:
    """정보나루 API를 호출해 JSON 본문을 돌려준다.

    authKey와 format=json(기본은 XML)을 붙이고 3초 타임아웃.
    재시도는 타임아웃·연결 오류에만 1회. HTTP 200이어도 본문이 오류면
    UpstreamUnavailable("data4library")를 던진다.
    """
    raise NotImplementedError
