
import json
from pathlib import Path

import pytest

@pytest.fixture
def sample_data_dir(tmp_path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    (data_dir / "test.csv").write_text(
        "id,name,amount\n"
        "1,alpha,10.5\n"
        "2,beta,20.0\n",
        encoding="utf-8",
    )

    (data_dir / "test.json").write_text(
        json.dumps([
            {"item_id": 1, "status": "active"},
            {"item_id": 2, "status": "pending", "extra": True},
        ]),
        encoding="utf-8",
    )

    (data_dir / "test.ndjson").write_text(
        '{"item_id":1,"status":"active"}\n'
        '{"item_id":2,"status":"pending","extra":true}\n',
        encoding="utf-8",
    )

    (data_dir / "test_pipe.txt").write_text(
        "id|name|amount\n"
        "1|alpha|10.5\n"
        "2|beta|20.0\n",
        encoding="utf-8",
    )

    (data_dir / "test_semicolon.txt").write_text(
        "id;name;amount\n"
        "1;alpha;10.5\n"
        "2;beta;20.0\n",
        encoding="utf-8",
    )

    (data_dir / "test_key_value.txt").write_text(
        "id=1;name=alpha;active=true\n"
        "id=2;name=beta;active=false\n",
        encoding="utf-8",
    )

    (data_dir / "test_plain.txt").write_text(
        "Application started.\n"
        "Loading configuration.\n"
        "Application ready.\n",
        encoding="utf-8",
    )

    (data_dir / "test_empty.txt").write_text(
        "",
        encoding="utf-8",
    )

    (data_dir / "test_invalid.ndjson").write_text(
        '{"id":1}\n'
        'invalid-json\n'
        '{"id":2}\n',
        encoding="utf-8",
    )

    return data_dir