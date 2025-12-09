import mcp.types as types
from datetime import datetime, timedelta
from typing import Optional
from .utils import make_anki_request


# Time range to days mapping
TIME_RANGES = {
    "day": 0,
    "week": 7,
    "month": 30,
    "year": 365,
    "all": None
}


async def get_review_stats(time_range: str = "month") -> list[types.TextContent]:
    """
    Get review statistics from Anki showing cards reviewed per day.

    Parameters:
    - time_range: Time range for statistics ("day", "week", "month", "year", "all")
    """
    # Validate and calculate cutoff date
    try:
        cutoff_date = _get_cutoff_date(time_range)
    except ValueError as e:
        return _error_response(str(e))

    # Fetch review data from Anki
    review_result = await make_anki_request("getNumCardsReviewedByDay")
    if not review_result["success"]:
        return _error_response(f"Failed to retrieve review statistics: {review_result['error']}")

    # Filter and format the results
    review_data = review_result["result"]
    filtered_data = _filter_by_date(review_data, cutoff_date)
    formatted_text = _format_review_data(filtered_data)

    return [types.TextContent(type="text", text=formatted_text)]


def _get_cutoff_date(time_range: str) -> Optional[datetime.date]:
    """
    Calculate the cutoff date based on time range.

    Args:
        time_range: The time range identifier

    Returns:
        datetime.date for filtered ranges, or None for "all" (no filtering)

    Raises:
        ValueError: If time_range is not a valid option
    """
    if time_range not in TIME_RANGES:
        valid_options = ', '.join(TIME_RANGES.keys())
        raise ValueError(f"Invalid time_range '{time_range}'. Valid options: {valid_options}")

    days = TIME_RANGES[time_range]
    if days is None:
        return None

    today = datetime.now().date()
    return today if days == 0 else today - timedelta(days=days)


def _filter_by_date(review_data: list, cutoff_date: Optional[datetime.date]) -> list:
    """Filter review data by cutoff date."""
    if cutoff_date is None:
        return review_data

    return [
        (date_str, count) for date_str, count in review_data
        if _parse_date(date_str) >= cutoff_date
    ]


def _format_review_data(filtered_data: list) -> str:
    """Format filtered review data into readable text."""
    if not filtered_data:
        return "No reviews found for the specified time range."

    total_cards = sum(count for _, count in filtered_data)
    formatted_lines = [f"  {date_str}: {count} cards" for date_str, count in filtered_data]

    header = f"Cards reviewed ({len(filtered_data)} days, {total_cards} total reviews):\n"
    return header + "\n".join(formatted_lines)


def _error_response(message: str) -> list[types.TextContent]:
    """Create an error response."""
    return [types.TextContent(type="text", text=message)]


def _parse_date(date_str: str) -> datetime.date:
    """Parse date string from Anki format to date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        # If parsing fails, return a very old date so it gets filtered out
        return datetime(1900, 1, 1).date()
