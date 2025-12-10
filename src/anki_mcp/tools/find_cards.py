import mcp.types as types
from .utils import make_anki_request


async def find_cards(query: str, limit: int = 100) -> list[types.TextContent]:
    """Find cards matching a query in Anki.

    Args:
        query: Anki search query (e.g., "deck:Default", "is:suspended").
        limit: Maximum number of card IDs to return (default 100).

    Returns:
        TextContent with matching card IDs.
    """
    result = await make_anki_request("findCards", query=query)

    if not result["success"]:
        return [
            types.TextContent(
                type="text",
                text=f"Failed to find cards: {result['error']}",
            )
        ]

    card_ids = result["result"]

    if not card_ids:
        return [
            types.TextContent(
                type="text",
                text=f"No cards found matching query: '{query}'",
            )
        ]

    total_count = len(card_ids)
    limited_ids = card_ids[:limit]

    if total_count > limit:
        header = f"Showing {len(limited_ids)} of {total_count} card IDs matching query: '{query}' (use a more specific query or increase limit to see more)"
    else:
        header = f"Found {total_count} card(s) matching query: '{query}'"

    card_ids_text = "\n".join(str(cid) for cid in limited_ids)

    return [
        types.TextContent(
            type="text",
            text=f"{header}\n\nCard IDs:\n{card_ids_text}",
        )
    ]
