"""Write the API's OpenAPI document to sdk/openapi.json (the input for the generated SDK).

    python scripts/export_openapi.py
"""

import json
from pathlib import Path

from app.main import app

target = Path(__file__).resolve().parents[2] / "sdk" / "openapi.json"
target.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {target}")
