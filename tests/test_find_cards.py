import pytest
from anki_mcp.tools.find_cards import find_cards


@pytest.mark.asyncio
async def test_find_cards_success(monkeypatch):
    """Test successful card search with multiple results."""
    mock_card_ids = [1494723142483, 1494703460437, 1494703479525]

    async def mock_anki_request(action, **kwargs):
        assert action == "findCards"
        assert kwargs["query"] == "deck:Test"
        return {"success": True, "result": mock_card_ids}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    result = await find_cards("deck:Test")

    assert len(result) == 1
    text = result[0].text
    assert "Found 3 card(s) matching query: 'deck:Test'" in text
    assert "1494723142483" in text
    assert "1494703460437" in text
    assert "1494703479525" in text


@pytest.mark.asyncio
async def test_find_cards_no_results(monkeypatch):
    """Test search that returns no matching cards."""
    async def mock_anki_request(action, **kwargs):
        assert action == "findCards"
        return {"success": True, "result": []}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    result = await find_cards("deck:NonExistent")

    assert len(result) == 1
    assert "No cards found matching query: 'deck:NonExistent'" in result[0].text


@pytest.mark.asyncio
async def test_find_cards_api_failure(monkeypatch):
    """Test handling of API errors."""
    async def mock_anki_request(action, **kwargs):
        return {"success": False, "error": "Invalid search query"}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    result = await find_cards("invalid:query")

    assert len(result) == 1
    assert "Failed to find cards: Invalid search query" in result[0].text


@pytest.mark.asyncio
async def test_find_cards_single_result(monkeypatch):
    """Test search returning a single card."""
    async def mock_anki_request(action, **kwargs):
        return {"success": True, "result": [1234567890123]}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    result = await find_cards("is:suspended")

    assert len(result) == 1
    text = result[0].text
    assert "Found 1 card(s) matching query: 'is:suspended'" in text
    assert "1234567890123" in text


@pytest.mark.asyncio
async def test_find_cards_limit_results(monkeypatch):
    """Test that results are limited when exceeding the limit parameter."""
    # Create 150 mock card IDs
    mock_card_ids = list(range(1000000000000, 1000000000150))

    async def mock_anki_request(action, **kwargs):
        return {"success": True, "result": mock_card_ids}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    # Test with default limit (100)
    result = await find_cards("deck:Test")

    text = result[0].text
    assert "Showing 100 of 150 card IDs" in text
    assert "use a more specific query or increase limit to see more" in text
    # Should have first 100 IDs but not the rest
    assert "1000000000000" in text
    assert "1000000000099" in text
    assert "1000000000100" not in text


@pytest.mark.asyncio
async def test_find_cards_custom_limit(monkeypatch):
    """Test that custom limit parameter works."""
    mock_card_ids = list(range(1000000000000, 1000000000050))

    async def mock_anki_request(action, **kwargs):
        return {"success": True, "result": mock_card_ids}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    # Test with custom limit of 10
    result = await find_cards("deck:Test", limit=10)

    text = result[0].text
    assert "Showing 10 of 50 card IDs" in text
    assert "1000000000000" in text
    assert "1000000000009" in text
    assert "1000000000010" not in text


@pytest.mark.asyncio
async def test_find_cards_under_limit(monkeypatch):
    """Test that no truncation message appears when results are under limit."""
    mock_card_ids = [1234, 5678, 9012]

    async def mock_anki_request(action, **kwargs):
        return {"success": True, "result": mock_card_ids}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    result = await find_cards("deck:Test", limit=10)

    text = result[0].text
    assert "Found 3 card(s) matching query: 'deck:Test'" in text
    assert "Showing" not in text
    assert "increase limit" not in text


@pytest.mark.asyncio
async def test_find_cards_special_characters_in_query(monkeypatch):
    """Test search with special characters in query."""
    async def mock_anki_request(action, **kwargs):
        assert kwargs["query"] == "is:suspended deck:\"My Deck\""
        return {"success": True, "result": []}

    monkeypatch.setattr("anki_mcp.tools.find_cards.make_anki_request", mock_anki_request)

    result = await find_cards("is:suspended deck:\"My Deck\"")

    assert len(result) == 1
    assert "No cards found" in result[0].text
