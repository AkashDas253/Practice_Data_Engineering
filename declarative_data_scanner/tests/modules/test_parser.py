from modules.parser.regex import RegexParser


PATTERN = (
    r"(?P<date>\S+)[ \t]+"
    r"(?P<level>\w+)[ \t]+"
    r"(?P<status_code>\d+)[ \t]+"
    r"(?P<method>\w+)[ \t]+"
    r"(?P<path>\S+)"
    r"(?:[ \t]+(?P<message>[^\r\n]*))?"
)


def test_regex_parser_creates_records():
    data = [
        {
            "source": "application.log",
            "content": (
                "2026-09-13 ERROR 500 "
                "GET /api/orders Database failed"
            ),
        }
    ]

    component = RegexParser({
        "pattern": PATTERN,
    })

    result = component.execute(data)

    assert len(result) == 1

    assert result[0]["date"] == "2026-09-13"
    assert result[0]["level"] == "ERROR"
    assert result[0]["status_code"] == "500"
    assert result[0]["method"] == "GET"
    assert result[0]["path"] == "/api/orders"
    assert result[0]["message"] == "Database failed"
    assert result[0]["source"] == "application.log"


def test_regex_parser_parses_multiple_lines():
    data = [
        {
            "source": "application.log",
            "content": "\n".join([
                "2026-09-13 INFO 200 GET /api/users",
                "2026-09-13 ERROR 500 GET /api/orders Database failed",
                "2026-09-13 INFO 200 POST /api/login",
                "2026-09-13 ERROR 503 GET /api/payments Payment unavailable",
            ]),
        }
    ]

    component = RegexParser({
        "pattern": PATTERN,
    })

    result = component.execute(data)

    assert len(result) == 4

    assert result[0]["level"] == "INFO"
    assert result[0]["status_code"] == "200"

    assert result[1]["level"] == "ERROR"
    assert result[1]["status_code"] == "500"
    assert result[1]["message"] == "Database failed"

    assert result[2]["level"] == "INFO"
    assert result[2]["status_code"] == "200"

    assert result[3]["level"] == "ERROR"
    assert result[3]["status_code"] == "503"
    assert result[3]["message"] == "Payment unavailable"
