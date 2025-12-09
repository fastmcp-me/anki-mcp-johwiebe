import mcp.types as types
from typing import Optional
from .utils import make_anki_request

async def get_stats(
    stat_type: str = "reviews", 
    deck_name: Optional[str] = None, 
    time_range: str = "month",
    include_cards: bool = False
) -> list[types.TextContent]:
    """
    Get comprehensive statistics from Anki
    
    Parameters:
    - stat_type: Type of statistics to retrieve (reviews, retention, due, difficulty)
    - deck_name: Optional deck name to filter statistics
    - time_range: Time range for statistics (day, week, month, year)
    - include_cards: Whether to include card-level details (only applicable for some stat types)
    """
    results = []
    error_messages = []
    
    # Handle review statistics (original functionality)
    if stat_type == "reviews" or stat_type == "all":
        review_result = await make_anki_request("getNumCardsReviewedByDay")
        if review_result["success"]:
            review_data = review_result["result"]
            # Format the review data for better readability
            formatted_data = "\n".join([f"{day}: {count} cards" for day, count in review_data])
            results.append(f"Cards reviewed by day:\n{formatted_data}")
        else:
            error_messages.append(f"Failed to retrieve review statistics: {review_result['error']}")
    
    # Handle card difficulty statistics
    if stat_type == "difficulty" or stat_type == "all":
        # First find cards in the specified deck
        query = f"deck:{deck_name}" if deck_name else ""
        note_ids_result = await make_anki_request("findNotes", query=query)
        
        if note_ids_result["success"] and note_ids_result["result"]:
            # Get card IDs from these notes
            cards_info_result = await make_anki_request("notesInfo", notes=note_ids_result["result"][:100])
            
            if cards_info_result["success"]:
                # Extract card IDs
                card_ids = []
                for note in cards_info_result["result"]:
                    card_ids.extend(note.get("cards", []))
                
                # Get ease factors
                ease_result = await make_anki_request("getEaseFactors", cards=card_ids)
                
                if ease_result["success"]:
                    # Calculate average ease factor
                    ease_factors = ease_result["result"]
                    avg_ease = sum(ease_factors) / len(ease_factors) if ease_factors else 0
                    
                    ease_data = f"Average ease factor: {avg_ease:.2f}\n"
                    
                    # Include individual card ease factors if requested
                    if include_cards and card_ids and len(card_ids) == len(ease_factors):
                        ease_data += "Individual card ease factors:\n"
                        ease_data += "\n".join([f"Card {card_id}: {ease}" 
                                             for card_id, ease in zip(card_ids, ease_factors)])
                    
                    results.append(ease_data)
                else:
                    error_messages.append(f"Failed to retrieve ease factors: {ease_result['error']}")
            else:
                error_messages.append(f"Failed to retrieve cards info: {cards_info_result['error']}")
        else:
            error_messages.append(f"Failed to find notes or no notes found: {note_ids_result.get('error', 'No notes found')}")
    
    # Handle due card statistics
    if stat_type == "due" or stat_type == "all":
        # Get deck configuration if deck specified
        if deck_name:
            deck_stats_result = await make_anki_request("getDeckStats", decks=[deck_name])
            
            if deck_stats_result["success"]:
                deck_stats = deck_stats_result["result"]
                due_data = f"Due cards in {deck_name}:\n"
                for stat in deck_stats:
                    due_data += f"New: {stat.get('new_count', 0)}\n"
                    due_data += f"Learning: {stat.get('learn_count', 0)}\n"
                    due_data += f"Review: {stat.get('review_count', 0)}\n"
                results.append(due_data)
            else:
                error_messages.append(f"Failed to retrieve deck statistics: {deck_stats_result['error']}")
    
    # Handle retention statistics
    if stat_type == "retention" or stat_type == "all":
        # This would require additional Anki Connect API calls or custom implementation
        # For now, we'll include a placeholder
        results.append("Retention statistics are not directly available through the AnkiConnect API.")
    
    # Combine results and errors
    if results:
        combined_results = "\n\n".join(results)
    else:
        combined_results = "No statistics available for the requested parameters."
    
    if error_messages:
        combined_results += "\n\nErrors encountered:\n" + "\n".join(error_messages)
    
    return [
        types.TextContent(
            type="text",
            text=combined_results,
        )
    ]