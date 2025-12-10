import mcp.types as types
from .utils import make_anki_request


async def suspend_cards(card_ids: list[int]) -> list[types.TextContent]:
    """Suspend cards by their card IDs.

    Args:
        card_ids: List of card IDs to suspend.

    Returns:
        TextContent indicating success or failure.
    """
    if not card_ids:
        return [
            types.TextContent(
                type="text",
                text="No card IDs provided. Please specify at least one card ID to suspend.",
            )
        ]

    result = await make_anki_request("suspend", cards=card_ids)

    if not result["success"]:
        return [
            types.TextContent(
                type="text",
                text=f"Failed to suspend cards: {result['error']}",
            )
        ]

    if result["result"]:
        return [
            types.TextContent(
                type="text",
                text=f"Successfully suspended {len(card_ids)} card(s).",
            )
        ]
    else:
        return [
            types.TextContent(
                type="text",
                text="No cards were suspended (all cards were already suspended).",
            )
        ]


async def unsuspend_cards(card_ids: list[int]) -> list[types.TextContent]:
    """Unsuspend cards by their card IDs.

    Args:
        card_ids: List of card IDs to unsuspend.

    Returns:
        TextContent indicating success or failure.
    """
    if not card_ids:
        return [
            types.TextContent(
                type="text",
                text="No card IDs provided. Please specify at least one card ID to unsuspend.",
            )
        ]

    result = await make_anki_request("unsuspend", cards=card_ids)

    if not result["success"]:
        return [
            types.TextContent(
                type="text",
                text=f"Failed to unsuspend cards: {result['error']}",
            )
        ]

    if result["result"]:
        return [
            types.TextContent(
                type="text",
                text=f"Successfully unsuspended {len(card_ids)} card(s).",
            )
        ]
    else:
        return [
            types.TextContent(
                type="text",
                text="No cards were unsuspended (no cards were previously suspended).",
            )
        ]
