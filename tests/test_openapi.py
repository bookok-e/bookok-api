import json
from pathlib import Path

from app.main import app


def test_openapi_json_is_up_to_date():
    """스키마를 바꾸면 openapi.json도 다시 만든다(README 참고). 프런트 타입의 원천이다."""
    committed = json.loads((Path(__file__).parents[1] / "openapi.json").read_text())
    assert committed == app.openapi()
