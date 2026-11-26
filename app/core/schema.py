from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """API 요청·응답 스키마의 공통 베이스. JSON 필드는 camelCase로 주고받는다.

    응답은 항상 response_model로 돌려준다. dict를 직접 반환하면 snake_case가 섞인다.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
