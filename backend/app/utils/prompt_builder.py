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
        "You are a helpful AI assistant. Use the previous conversation and any scraped "
        "page content to understand what the user wants. Be concise but clear, accurate, "
        "and helpful. If you don't know something, say so."
    )
    prompt_parts.append(system_instruction)
    prompt_parts.append("\n")
    
    # Add scraped content if available
    if scraped_text:
        prompt_parts.append("\n--- Web Page Content ---")
        prompt_parts.append("\nHere is content scraped from a related web page. Use it if relevant, ignore if not:")
        prompt_parts.append(f"\n{scraped_text}")
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
