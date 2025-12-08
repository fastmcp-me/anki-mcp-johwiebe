import mcp.server.stdio
from mcp.server.fastmcp import FastMCP

from anki_mcp.tools.get_collection_overview import get_collection_overview
from anki_mcp.tools.add_or_update_notes import add_or_update_notes
from anki_mcp.tools.get_stats import get_stats
from anki_mcp.tools.find_notes import find_notes

app = FastMCP("anki")

# Register tools with the app
app.tool(name="get-collection-overview", description="Get comprehensive information about the Anki collection including decks, models, and fields")(get_collection_overview)
app.tool(name="get-stats", description="Get comprehensive statistics from Anki")(get_stats)
app.tool(name='find-notes', description='Find notes matching a query in Anki')(find_notes)
app.tool(name='add-or-update-notes', description="Add new notes or update existing ones in Anki")(add_or_update_notes)

if __name__ == "__main__":
    # Initialize and run the server
    import mcp
    mcp.run(transport='stdio')