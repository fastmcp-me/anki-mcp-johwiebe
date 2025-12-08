import pytest
from anki_mcp.tools.find_notes import find_notes


@pytest.mark.asyncio
async def test_find_notes_success(monkeypatch):
    """Test successful note search with multiple results."""
    mock_notes = [
        {
            "noteId": 1234,
            "modelName": "Basic",
            "tags": ["test", "example"],
            "fields": {
                "Front": {"value": "What is Python?", "order": 0},
                "Back": {"value": "A programming language", "order": 1}
            },
            "mod": 1700000000
        },
        {
            "noteId": 5678,
            "modelName": "Cloze",
            "tags": [],
            "fields": {
                "Text": {"value": "{{c1::Python}} is a language", "order": 0}
            },
            "mod": 1700000001
        }
    ]

    async def mock_anki_request(action, **kwargs):
        assert action == "notesInfo"
        assert kwargs["query"] == "deck:Test"
        return {"success": True, "result": mock_notes}

    monkeypatch.setattr("anki_mcp.tools.find_notes.make_anki_request", mock_anki_request)

    result = await find_notes("deck:Test")

    assert len(result) == 1
    text = result[0].text
    assert "Found 2 notes matching query: 'deck:Test'" in text
    assert "Note ID: 1234" in text
    assert "Note ID: 5678" in text
    assert "Model: Basic" in text
    assert "Model: Cloze" in text
    assert "Tags: test, example" in text
    assert "Tags: (no tags)" in text
    assert "Front: What is Python?" in text
    assert "Back: A programming language" in text


@pytest.mark.asyncio
async def test_find_notes_no_results(monkeypatch):
    """Test search that returns no matching notes."""
    async def mock_anki_request(action, **kwargs):
        assert action == "notesInfo"
        return {"success": True, "result": []}

    monkeypatch.setattr("anki_mcp.tools.find_notes.make_anki_request", mock_anki_request)

    result = await find_notes("deck:NonExistent")

    assert len(result) == 1
    assert "No notes found matching query: 'deck:NonExistent'" in result[0].text


@pytest.mark.asyncio
async def test_find_notes_api_failure(monkeypatch):
    """Test handling of API errors."""
    async def mock_anki_request(action, **kwargs):
        return {"success": False, "error": "Invalid search query"}

    monkeypatch.setattr("anki_mcp.tools.find_notes.make_anki_request", mock_anki_request)

    result = await find_notes("invalid:query")

    assert len(result) == 1
    assert "Failed to retrieve notes: Invalid search query" in result[0].text


@pytest.mark.asyncio
async def test_find_notes_long_field_truncation(monkeypatch):
    """Test that long field values are truncated at 100 characters."""
    long_value = "A" * 150  # 150 characters
    mock_notes = [
        {
            "noteId": 1234,
            "modelName": "Basic",
            "tags": [],
            "fields": {
                "Front": {"value": long_value, "order": 0},
                "Back": {"value": "Short", "order": 1}
            },
            "mod": 1700000000
        }
    ]

    async def mock_anki_request(action, **kwargs):
        return {"success": True, "result": mock_notes}

    monkeypatch.setattr("anki_mcp.tools.find_notes.make_anki_request", mock_anki_request)

    result = await find_notes("*")

    text = result[0].text
    # Should be truncated to 97 chars + "..."
    assert "A" * 97 + "..." in text
    assert "A" * 100 not in text


@pytest.mark.asyncio
async def test_find_notes_single_result(monkeypatch):
    """Test search returning a single note."""
    mock_notes = [
        {
            "noteId": 9999,
            "modelName": "Basic",
            "tags": ["unique"],
            "fields": {
                "Front": {"value": "Single question", "order": 0},
                "Back": {"value": "Single answer", "order": 1}
            },
            "mod": 1700000000
        }
    ]

    async def mock_anki_request(action, **kwargs):
        return {"success": True, "result": mock_notes}

    monkeypatch.setattr("anki_mcp.tools.find_notes.make_anki_request", mock_anki_request)

    result = await find_notes("tag:unique")

    assert len(result) == 1
    text = result[0].text
    assert "Found 1 notes matching query: 'tag:unique'" in text
    assert "Note ID: 9999" in text
    assert "Tags: unique" in text


@pytest.mark.asyncio
async def test_find_notes_special_characters_in_query(monkeypatch):
    """Test search with special characters in query."""
    async def mock_anki_request(action, **kwargs):
        assert kwargs["query"] == "front:*test* OR back:\"exact phrase\""
        return {"success": True, "result": []}

    monkeypatch.setattr("anki_mcp.tools.find_notes.make_anki_request", mock_anki_request)

    result = await find_notes("front:*test* OR back:\"exact phrase\"")

    assert len(result) == 1
    assert "No notes found" in result[0].text
