from modules.reader.text import TextReader


def test_text_reader_reads_files(tmp_path):
    file = tmp_path / "application.log"

    file.write_text(
        "2026-09-13 INFO 200 GET /api/health",
        encoding="utf-8",
    )

    component = TextReader({
        "encoding": "utf-8",
    })

    result = component.execute([str(file)])

    assert len(result) == 1
    assert result[0]["source"] == str(file)
    assert result[0]["content"] == (
        "2026-09-13 INFO 200 GET /api/health"
    )
