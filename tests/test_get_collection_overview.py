import pytest
from anki_mcp.tools.get_collection_overview import get_collection_overview


@pytest.mark.asyncio
async def test_get_collection_overview_success(monkeypatch):
    # Mock successful responses for decks, models, tags, and fields
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": True, "result": ["Default", "Custom Deck"]}
        elif action == "modelNames":
            return {"success": True, "result": ["Basic", "Cloze"]}
        elif action == "getTags":
            return {"success": True, "result": ["vocabulary", "grammar", "test"]}
        elif action == "modelFieldNames":
            return {"success": True, "result": ["Front", "Back"]}
        elif action == "modelFieldDescriptions":
            return {"success": True, "result": ["Front side", "Back side"]}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()

    assert len(result) >= 5  # decks, models, tags, and 2 model field sets
    assert result[0].text == "\nAvailable decks in Anki (2):\n- Default\n- Custom Deck"
    assert result[1].text == "\nAvailable note models in Anki (2):\n- Basic\n- Cloze"
    assert result[2].text == "\nTags used in Anki (3): vocabulary, grammar, test"
    assert result[3].text == "\nFields for model 'Basic' (2):\n  - Front: Front side\n  - Back: Back side"
    assert result[4].text == "\nFields for model 'Cloze' (2):\n  - Front: Front side\n  - Back: Back side"


@pytest.mark.asyncio
async def test_get_collection_overview_deck_failure(monkeypatch):
    # Mock failed response for decks
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": False, "error": "Failed to connect to Anki"}
        return {"success": True, "result": []}
    
    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()
    assert len(result) == 1
    assert result[0].text == "\nFailed to retrieve decks: Failed to connect to Anki"


@pytest.mark.asyncio
async def test_get_collection_overview_model_failure(monkeypatch):
    # Mock successful response for decks but failed for models
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": True, "result": ["Default"]}
        elif action == "modelNames":
            return {"success": False, "error": "Failed to retrieve models"}
        return {"success": True, "result": []}
    
    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()
    assert len(result) == 1  # The implementation returns immediately on model failure
    assert result[0].text == "\nFailed to retrieve models: Failed to retrieve models"


@pytest.mark.asyncio
async def test_get_collection_overview_field_failures(monkeypatch):
    # Mock successful responses for decks and models but failed for fields
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": True, "result": ["Default"]}
        elif action == "modelNames":
            return {"success": True, "result": ["Basic"]}
        elif action == "getTags":
            return {"success": True, "result": []}
        elif action == "modelFieldNames":
            return {"success": False, "error": "Failed to retrieve field names"}
        elif action == "modelFieldDescriptions":
            return {"success": True, "result": []}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()
    assert len(result) == 3  # One for decks, one for models, one for the field error
    assert "\nAvailable decks in Anki" in result[0].text
    assert "\nAvailable note models in Anki" in result[1].text
    assert "\nFailed to retrieve field names for 'Basic'" in result[2].text 

@pytest.mark.asyncio
async def test_get_collection_overview_field_description_failure(monkeypatch):
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": True, "result": ["Default"]}
        elif action == "modelNames":
            return {"success": True, "result": ["Basic"]}
        elif action == "getTags":
            return {"success": True, "result": []}
        elif action == "modelFieldNames":
            return {"success": True, "result": ["Front", "Back"]}
        elif action == "modelFieldDescriptions":
            return {"success": False, "error": "Failed to retrieve field descriptions"}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()
    assert len(result) == 3  # One for decks, one for models, one for the field error (no tags since empty)
    assert "\nFailed to retrieve field descriptions for 'Basic'" in result[2].text


@pytest.mark.asyncio
async def test_get_collection_overview_tags_failure(monkeypatch):
    """Test handling of tags retrieval failure."""
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": True, "result": ["Default"]}
        elif action == "modelNames":
            return {"success": True, "result": ["Basic"]}
        elif action == "getTags":
            return {"success": False, "error": "Failed to retrieve tags"}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()
    assert len(result) == 1
    assert "\nFailed to retrieve tags: Failed to retrieve tags" in result[0].text


@pytest.mark.asyncio
async def test_get_collection_overview_empty_tags(monkeypatch):
    """Test handling of empty tags list (no tags section should be added)."""
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": True, "result": ["Default"]}
        elif action == "modelNames":
            return {"success": True, "result": ["Basic"]}
        elif action == "getTags":
            return {"success": True, "result": []}
        elif action == "modelFieldNames":
            return {"success": True, "result": ["Front", "Back"]}
        elif action == "modelFieldDescriptions":
            return {"success": True, "result": ["", ""]}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()
    # Should not include tags section when empty
    texts = [r.text for r in result]
    assert not any("Tags used in Anki" in t for t in texts)


@pytest.mark.asyncio
async def test_get_collection_overview_fields_without_descriptions(monkeypatch):
    """Test fields are displayed correctly when descriptions are empty."""
    async def mock_anki_request(action, **kwargs):
        if action == "deckNames":
            return {"success": True, "result": ["Default"]}
        elif action == "modelNames":
            return {"success": True, "result": ["Basic"]}
        elif action == "getTags":
            return {"success": True, "result": ["test"]}
        elif action == "modelFieldNames":
            return {"success": True, "result": ["Front", "Back"]}
        elif action == "modelFieldDescriptions":
            return {"success": True, "result": ["", ""]}  # Empty descriptions
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_collection_overview.make_anki_request", mock_anki_request)

    result = await get_collection_overview()
    # Fields should be listed without colon and description
    field_text = result[3].text
    assert "  - Front\n" in field_text or "  - Front" in field_text
    assert ": " not in field_text.split("Fields for model")[1]  # No descriptions after field names 
