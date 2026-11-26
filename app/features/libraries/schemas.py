"""소장 조회 계약 (담당 TBD). 호출 규칙은 docs/05-roles.md."""

from pydantic import BaseModel


class Library(BaseModel):
    """정보나루 libSrchByBook lib 1건."""

    lib_code: str
    name: str  # libName
    address: str
    homepage: str | None = None


class Holding(BaseModel):
    library: Library
    loan_available: bool | None = None  # bookExist, 확인 실패면 None
