from modules.processing.filter import FilterProcessor


def test_filter_keeps_matching_records():
    data = [
        {"level": "ERROR", "message": "Database failed"},
        {"level": "INFO", "message": "Request completed"},
        {"level": "ERROR", "message": "Service unavailable"},
    ]

    component = FilterProcessor({
        "field": "level",
        "equals": "ERROR",
    })

    result = component.execute(data)

    assert len(result) == 2

    assert result[0]["message"] == "Database failed"
    assert result[1]["message"] == "Service unavailable"


def test_filter_returns_empty_when_nothing_matches():
    data = [
        {"level": "INFO"},
        {"level": "WARN"},
    ]

    component = FilterProcessor({
        "field": "level",
        "equals": "ERROR",
    })

    result = component.execute(data)

    assert result == []
