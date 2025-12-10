import mcp.server.stdio
from mcp.server.fastmcp import FastMCP

from anki_mcp.tools.get_collection_overview import get_collection_overview
from anki_mcp.tools.add_or_update_notes import add_or_update_notes
from anki_mcp.tools.get_review_stats import get_review_stats
from anki_mcp.tools.find_notes import find_notes
from anki_mcp.tools.find_cards import find_cards
from anki_mcp.tools.suspend_cards import suspend_cards, unsuspend_cards

app = FastMCP("anki")

# Register tools with the app
app.tool(name="get-collection-overview", description="Get comprehensive information about the Anki collection including decks, models, and fields")(get_collection_overview)
app.tool(name="get-review-stats", description="Get review statistics from Anki showing cards reviewed per day, with optional time range filtering")(get_review_stats)
app.tool(name='find-notes', description='Find notes matching a query in Anki')(find_notes)
app.tool(name='find-cards', description='Find card IDs matching a query in Anki')(find_cards)
app.tool(name='add-or-update-notes', description="Add new notes or update existing ones in Anki")(add_or_update_notes)
app.tool(name='suspend-cards', description="Suspend cards by their card IDs")(suspend_cards)
app.tool(name='unsuspend-cards', description="Unsuspend cards by their card IDs")(unsuspend_cards)

if __name__ == "__main__":
    # Initialize and run the server
    import mcp
    mcp.run(transport='stdio')