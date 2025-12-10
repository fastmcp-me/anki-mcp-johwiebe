import mcp.types as types
from .utils import make_anki_request
from datetime import datetime


def _format_note(note: dict) -> str:
    """Format a single note for display."""
    tags = ", ".join(note["tags"]) if note["tags"] else "(no tags)"
    mod_time = datetime.fromtimestamp(note["mod"]).strftime("%Y-%m-%d %H:%M:%S")

    fields_text = [
        f"  - {name}: {data['value']}"
        for name, data in note["fields"].items()
    ]

    return (
        f"Note ID: {note['noteId']}\n"
        f"Model: {note['modelName']}\n"
        f"Tags: {tags}\n"
        f"Modified: {mod_time}\n"
        f"Fields:\n" + "\n".join(fields_text) + "\n"
    )


async def find_notes(query: str, limit: int = 20) -> list[types.TextContent]:
    result = await make_anki_request("notesInfo", query=query)

    if not result["success"]:
        return [
            types.TextContent(
                type="text",
                text=f"Failed to retrieve notes: {result['error']}",
            )
        ]

    notes = result["result"]

    if not notes:
        return [
            types.TextContent(
                type="text",
                text=f"No notes found matching query: '{query}'",
            )
        ]

    total_count = len(notes)
    limited_notes = notes[:limit]
    notes_info = [_format_note(note) for note in limited_notes]

    if total_count > limit:
        header = f"Showing {len(limited_notes)} of {total_count} notes matching query: '{query}' (use a more specific query or increase limit to see more)"
    else:
        header = f"Found {total_count} notes matching query: '{query}'"

    return [
        types.TextContent(
            type="text",
            text=header + "\n\n" + "\n\n".join(notes_info),
        )
    ]
