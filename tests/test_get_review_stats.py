import pytest
from datetime import datetime, timedelta
from anki_mcp.tools.get_review_stats import get_review_stats


@pytest.mark.asyncio
async def test_get_review_stats_basic_success(monkeypatch):
    """Test retrieving basic review statistics."""
    review_data = [
        ["2024-01-01", 50],
        ["2024-01-02", 75],
        ["2024-01-03", 60]
    ]

    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": review_data}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_review_stats.make_anki_request", mock_anki_request)

    # Use time_range="all" to include all historical dates
    result = await get_review_stats(time_range="all")

    assert len(result) == 1
    text = result[0].text
    assert "Cards reviewed" in text
    assert "2024-01-01: 50 cards" in text
    assert "2024-01-02: 75 cards" in text
    assert "2024-01-03: 60 cards" in text
    assert "185 total reviews" in text  # 50 + 75 + 60


@pytest.mark.asyncio
async def test_get_review_stats_time_range_week(monkeypatch):
    """Test filtering review statistics by week."""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    old_date = today - timedelta(days=10)

    review_data = [
        [old_date.strftime("%Y-%m-%d"), 100],  # Should be filtered out
        [week_ago.strftime("%Y-%m-%d"), 50],   # Should be included
        [today.strftime("%Y-%m-%d"), 75]        # Should be included
    ]

    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": review_data}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_review_stats.make_anki_request", mock_anki_request)

    result = await get_review_stats(time_range="week")

    text = result[0].text
    assert "125 total reviews" in text  # 50 + 75 (old_date filtered out)
    assert old_date.strftime("%Y-%m-%d") not in text


@pytest.mark.asyncio
async def test_get_review_stats_time_range_day(monkeypatch):
    """Test filtering review statistics by day (today only)."""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    review_data = [
        [yesterday.strftime("%Y-%m-%d"), 50],  # Should be filtered out
        [today.strftime("%Y-%m-%d"), 75]        # Should be included
    ]

    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": review_data}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_review_stats.make_anki_request", mock_anki_request)

    result = await get_review_stats(time_range="day")

    text = result[0].text
    assert "75 total reviews" in text
    assert yesterday.strftime("%Y-%m-%d") not in text


@pytest.mark.asyncio
async def test_get_review_stats_time_range_all(monkeypatch):
    """Test retrieving all review statistics without time filtering."""
    review_data = [
        ["2023-01-01", 100],
        ["2024-01-01", 50],
        ["2024-12-01", 75]
    ]

    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": review_data}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_review_stats.make_anki_request", mock_anki_request)

    result = await get_review_stats(time_range="all")

    text = result[0].text
    assert "225 total reviews" in text  # All dates included
    assert "2023-01-01: 100 cards" in text


@pytest.mark.asyncio
async def test_get_review_stats_invalid_time_range(monkeypatch):
    """Test handling of invalid time range parameter."""
    result = await get_review_stats(time_range="invalid")

    text = result[0].text
    assert "Invalid time_range" in text
    assert "day, week, month, year, all" in text


@pytest.mark.asyncio
async def test_get_review_stats_api_failure(monkeypatch):
    """Test handling of API failure."""
    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": False, "error": "Anki not connected"}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_review_stats.make_anki_request", mock_anki_request)

    result = await get_review_stats()

    text = result[0].text
    assert "Failed to retrieve review statistics: Anki not connected" in text


@pytest.mark.asyncio
async def test_get_review_stats_empty_data(monkeypatch):
    """Test handling of empty review data."""
    async def mock_anki_request(action, **kwargs):
        if action == "getNumCardsReviewedByDay":
            return {"success": True, "result": []}
        return {"success": False, "error": "Unexpected action"}

    monkeypatch.setattr("anki_mcp.tools.get_review_stats.make_anki_request", mock_anki_request)

    result = await get_review_stats()

    text = result[0].text
    assert "No reviews found" in text
