import pytest
from anki_mcp.tools.suspend_cards import suspend_cards, unsuspend_cards


@pytest.mark.asyncio
async def test_suspend_cards_success(monkeypatch):
    """Test successful card suspension."""
    async def mock_anki_request(action, **kwargs):
        assert action == "suspend"
        assert kwargs["cards"] == [1234, 5678]
        return {"success": True, "result": True}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await suspend_cards([1234, 5678])

    assert len(result) == 1
    assert "Successfully suspended 2 card(s)" in result[0].text


@pytest.mark.asyncio
async def test_suspend_cards_already_suspended(monkeypatch):
    """Test suspending cards that are already suspended."""
    async def mock_anki_request(action, **kwargs):
        assert action == "suspend"
        return {"success": True, "result": False}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await suspend_cards([1234])

    assert len(result) == 1
    assert "No cards were suspended" in result[0].text
    assert "already suspended" in result[0].text


@pytest.mark.asyncio
async def test_suspend_cards_api_failure(monkeypatch):
    """Test handling of API errors during suspension."""
    async def mock_anki_request(action, **kwargs):
        return {"success": False, "error": "Card not found"}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await suspend_cards([9999])

    assert len(result) == 1
    assert "Failed to suspend cards: Card not found" in result[0].text


@pytest.mark.asyncio
async def test_suspend_cards_empty_list():
    """Test suspending with empty card list."""
    result = await suspend_cards([])

    assert len(result) == 1
    assert "No card IDs provided" in result[0].text


@pytest.mark.asyncio
async def test_suspend_cards_single_card(monkeypatch):
    """Test suspending a single card."""
    async def mock_anki_request(action, **kwargs):
        assert action == "suspend"
        assert kwargs["cards"] == [1234]
        return {"success": True, "result": True}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await suspend_cards([1234])

    assert len(result) == 1
    assert "Successfully suspended 1 card(s)" in result[0].text


@pytest.mark.asyncio
async def test_unsuspend_cards_success(monkeypatch):
    """Test successful card unsuspension."""
    async def mock_anki_request(action, **kwargs):
        assert action == "unsuspend"
        assert kwargs["cards"] == [1234, 5678]
        return {"success": True, "result": True}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await unsuspend_cards([1234, 5678])

    assert len(result) == 1
    assert "Successfully unsuspended 2 card(s)" in result[0].text


@pytest.mark.asyncio
async def test_unsuspend_cards_not_suspended(monkeypatch):
    """Test unsuspending cards that were not suspended."""
    async def mock_anki_request(action, **kwargs):
        assert action == "unsuspend"
        return {"success": True, "result": False}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await unsuspend_cards([1234])

    assert len(result) == 1
    assert "No cards were unsuspended" in result[0].text
    assert "no cards were previously suspended" in result[0].text


@pytest.mark.asyncio
async def test_unsuspend_cards_api_failure(monkeypatch):
    """Test handling of API errors during unsuspension."""
    async def mock_anki_request(action, **kwargs):
        return {"success": False, "error": "Card not found"}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await unsuspend_cards([9999])

    assert len(result) == 1
    assert "Failed to unsuspend cards: Card not found" in result[0].text


@pytest.mark.asyncio
async def test_unsuspend_cards_empty_list():
    """Test unsuspending with empty card list."""
    result = await unsuspend_cards([])

    assert len(result) == 1
    assert "No card IDs provided" in result[0].text


@pytest.mark.asyncio
async def test_unsuspend_cards_single_card(monkeypatch):
    """Test unsuspending a single card."""
    async def mock_anki_request(action, **kwargs):
        assert action == "unsuspend"
        assert kwargs["cards"] == [1234]
        return {"success": True, "result": True}

    monkeypatch.setattr("anki_mcp.tools.suspend_cards.make_anki_request", mock_anki_request)

    result = await unsuspend_cards([1234])

    assert len(result) == 1
    assert "Successfully unsuspended 1 card(s)" in result[0].text
