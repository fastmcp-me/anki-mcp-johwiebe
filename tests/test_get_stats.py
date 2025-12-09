import pytest
from anki_mcp.tools.get_stats import get_stats


@pytest.mark.asyncio
async def test_get_stats_reviews_success(monkeypatch):
    """Test retrieving review statistics."""
    review_data = [
        ["2024-01-01", 50],
        ["2024-01-02", 75],
        ["2024-01-03", 60]
    ]

    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": review_data}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="reviews")

    assert len(result) == 1
    text = result[0].text
    assert "Cards reviewed by day:" in text
    assert "2024-01-01: 50 cards" in text
    assert "2024-01-02: 75 cards" in text
    assert "2024-01-03: 60 cards" in text


@pytest.mark.asyncio
async def test_get_stats_reviews_failure(monkeypatch):
    """Test handling of review statistics API failure."""
    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": False, "error": "Anki not connected"}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="reviews")

    assert len(result) == 1
    text = result[0].text
    assert "Failed to retrieve review statistics: Anki not connected" in text


@pytest.mark.asyncio
async def test_get_stats_difficulty_success(monkeypatch):
    """Test retrieving card difficulty (ease factor) statistics."""
    note_ids = [1001, 1002, 1003]
    notes_info = [
        {"noteId": 1001, "cards": [2001, 2002]},
        {"noteId": 1002, "cards": [2003]},
        {"noteId": 1003, "cards": [2004, 2005]}
    ]
    ease_factors = [2500, 2300, 2100, 2700, 2400]  # 5 cards

    async def mock_anki_request(action, **kwargs):
        if action == "findNotes":
            return {"success": True, "result": note_ids}
        elif action == "notesInfo":
            return {"success": True, "result": notes_info}
        elif action == "getEaseFactors":
            assert kwargs["cards"] == [2001, 2002, 2003, 2004, 2005]
            return {"success": True, "result": ease_factors}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="difficulty")

    assert len(result) == 1
    text = result[0].text
    # Average ease: (2500 + 2300 + 2100 + 2700 + 2400) / 5 = 2400
    assert "Average ease factor: 2400.00" in text


@pytest.mark.asyncio
async def test_get_stats_difficulty_with_deck_filter(monkeypatch):
    """Test difficulty stats filtered by deck name."""
    async def mock_anki_request(action, **kwargs):
        if action == "findNotes":
            assert kwargs["query"] == "deck:MyDeck"
            return {"success": True, "result": [1001]}
        elif action == "notesInfo":
            return {"success": True, "result": [{"noteId": 1001, "cards": [2001]}]}
        elif action == "getEaseFactors":
            return {"success": True, "result": [2500]}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="difficulty", deck_name="MyDeck")

    assert len(result) == 1
    assert "Average ease factor: 2500.00" in result[0].text


@pytest.mark.asyncio
async def test_get_stats_difficulty_with_card_details(monkeypatch):
    """Test difficulty stats with individual card details."""
    async def mock_anki_request(action, **kwargs):
        if action == "findNotes":
            return {"success": True, "result": [1001]}
        elif action == "notesInfo":
            return {"success": True, "result": [{"noteId": 1001, "cards": [2001, 2002]}]}
        elif action == "getEaseFactors":
            return {"success": True, "result": [2500, 2300]}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="difficulty", include_cards=True)

    text = result[0].text
    assert "Individual card ease factors:" in text
    assert "Card 2001: 2500" in text
    assert "Card 2002: 2300" in text


@pytest.mark.asyncio
async def test_get_stats_difficulty_no_notes_found(monkeypatch):
    """Test difficulty stats when no notes are found."""
    async def mock_anki_request(action, **kwargs):
        if action == "findNotes":
            return {"success": True, "result": []}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="difficulty")

    text = result[0].text
    assert "Failed to find notes or no notes found" in text


@pytest.mark.asyncio
async def test_get_stats_due_success(monkeypatch):
    """Test retrieving due card statistics for a deck."""
    deck_stats = [
        {
            "deck_id": 1,
            "name": "TestDeck",
            "new_count": 10,
            "learn_count": 5,
            "review_count": 25
        }
    ]

    async def mock_anki_request(action, **kwargs):
        if action == "getDeckStats":
            assert kwargs["decks"] == ["TestDeck"]
            return {"success": True, "result": deck_stats}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="due", deck_name="TestDeck")

    text = result[0].text
    assert "Due cards in TestDeck:" in text
    assert "New: 10" in text
    assert "Learning: 5" in text
    assert "Review: 25" in text


@pytest.mark.asyncio
async def test_get_stats_due_without_deck_name(monkeypatch):
    """Test that due stats without deck_name doesn't make API call."""
    call_count = 0

    async def mock_anki_request(action, **kwargs):
        nonlocal call_count
        call_count += 1
        return {"success": False, "error": "Should not be called"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="due")

    # Due stats requires deck_name, so no API calls should be made
    assert call_count == 0
    assert "No statistics available" in result[0].text


@pytest.mark.asyncio
async def test_get_stats_retention_placeholder(monkeypatch):
    """Test that retention stats returns placeholder message."""
    async def mock_anki_request(action, **kwargs):
        return {"success": False, "error": "Should not be called for retention"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="retention")

    text = result[0].text
    assert "Retention statistics are not directly available" in text


@pytest.mark.asyncio
async def test_get_stats_all_types(monkeypatch):
    """Test retrieving all statistics types at once."""
    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": [["2024-01-01", 50]]}
        elif action == "findNotes":
            return {"success": True, "result": [1001]}
        elif action == "notesInfo":
            return {"success": True, "result": [{"noteId": 1001, "cards": [2001]}]}
        elif action == "getEaseFactors":
            return {"success": True, "result": [2500]}
        elif action == "getDeckStats":
            return {"success": True, "result": [{"new_count": 5, "learn_count": 3, "review_count": 10}]}
        return {"success": False, "error": f"Unexpected action: {action}"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="all", deck_name="TestDeck")

    text = result[0].text
    assert "Cards reviewed by day:" in text
    assert "Average ease factor:" in text
    assert "Due cards in TestDeck:" in text
    assert "Retention statistics are not directly available" in text


@pytest.mark.asyncio
async def test_get_stats_mixed_success_and_errors(monkeypatch):
    """Test that partial failures still return successful results."""
    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": [["2024-01-01", 50]]}
        elif action == "findNotes":
            return {"success": False, "error": "Database error"}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="all")

    text = result[0].text
    # Should contain successful review stats
    assert "Cards reviewed by day:" in text
    assert "2024-01-01: 50 cards" in text
    # Should also contain error message
    assert "Errors encountered:" in text
    assert "Failed to find notes or no notes found" in text


@pytest.mark.asyncio
async def test_get_stats_empty_review_data(monkeypatch):
    """Test handling of empty review data."""
    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": []}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_stats.make_anki_request", mock_anki_request)

    result = await get_stats(stat_type="reviews")

    text = result[0].text
    assert "Cards reviewed by day:" in text
