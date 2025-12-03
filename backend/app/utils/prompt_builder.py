"""
Prompt construction utilities for the AI model.
"""
from typing import Optional


def build_prompt(
    history: list[dict],
    user_message: str,
    scraped_text: Optional[str] = None
) -> str:
    """
    Build a comprehensive prompt including system instructions, history, and optional scraped content.
    
    Args:
        history: List of previous messages with 'role' and 'content' keys
        user_message: Current user message
        scraped_text: Optional scraped web page content
    
    Returns:
        Formatted prompt string for the AI model
    """
    prompt_parts = []
    
    # System instruction
    system_instruction = (
        "You are a helpful AI assistant with access to real-time web search results. "
        "Use the previous conversation and any search results or scraped content to provide "
        "accurate, up-to-date information. Be concise but clear, accurate, and helpful. "
        "If you don't know something, say so. When using search results, cite the sources."
    )
    prompt_parts.append(system_instruction)
    prompt_parts.append("\n")
    
    # Add scraped content or search results if available
    if scraped_text:
        if "search results:" in scraped_text.lower():
            prompt_parts.append("\n--- REAL-TIME SEARCH RESULTS ---")
            prompt_parts.append("\nThe following are CURRENT, UP-TO-DATE search results from the web.")
            prompt_parts.append("\nUSE THIS INFORMATION to answer the user's question with the latest data:")
        else:
            prompt_parts.append("\n--- Web Page Content ---")
            prompt_parts.append("\nHere is content scraped from a related web page. Use it if relevant, ignore if not:")
        prompt_parts.append(f"\n{scraped_text}")
        if "search results:" in scraped_text.lower():
            prompt_parts.append("\n--- END OF SEARCH RESULTS ---\n")
        else:
            prompt_parts.append("\n--- End of Web Page Content ---\n")
    
    # Add conversation history
    if history:
        prompt_parts.append("\n--- Conversation History ---")
        for msg in history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "user":
                prompt_parts.append(f"\nUser: {content}")
            elif role == "assistant":
                prompt_parts.append(f"\nAssistant: {content}")
        prompt_parts.append("\n--- End of History ---\n")
    
    # Add current user message
    prompt_parts.append(f"\nUser: {user_message}")
    prompt_parts.append("\n\nAssistant:")
    
    return "".join(prompt_parts)
