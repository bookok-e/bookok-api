"""openapi.json 생성: uv run python -m app.openapi_export > openapi.json"""

import json

from app.main import app

if __name__ == "__main__":
    print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))
