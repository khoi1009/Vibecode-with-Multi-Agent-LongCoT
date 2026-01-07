"""
Context Compaction Utilities
Manage token budgets and context size for agent handoff
"""

from typing import Dict, List, Any
import json


def compact_context(context: Dict[str, Any], max_tokens: int = 4000) -> Dict[str, Any]:
    """
    Compact context to fit within token budget

    Args:
        context: Original context dictionary
        max_tokens: Maximum tokens (approximate)

    Returns:
        Compacted context
    """
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4

    compacted = {}

    for key, value in context.items():
        if isinstance(value, str):
            # String values - truncate if too long
            if len(value) > max_chars:
                compacted[key] = value[:max_chars] + f"\n... [truncated {len(value) - max_chars} chars]"
            else:
                compacted[key] = value
        elif isinstance(value, dict):
            # Nested dict - compact recursively
            compacted[key] = compact_context(value, max_tokens // 2)
        elif isinstance(value, list):
            # List - keep first few items if too many
            if len(value) > 10:
                compacted[key] = value[:5] + [f"... ({len(value) - 5} more items)"]
            else:
                compacted[key] = value
        else:
            # Other types - keep as is
            compacted[key] = value

    return compacted


def summarize_messages(messages: List[Dict[str, Any]], max_messages: int = 5) -> List[Dict[str, Any]]:
    """
    Summarize message history

    Args:
        messages: List of message dictionaries
        max_messages: Maximum messages to keep

    Returns:
        Summarized messages
    """
    if len(messages) <= max_messages:
        return messages

    # Keep first few and last few
    kept = messages[:max_messages // 2]
    kept.append({
        "type": "summary",
        "message": f"... ({len(messages) - max_messages} more messages) ..."
    })
    kept.extend(messages[-max_messages // 2:])

    return kept


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return len(text) // 4
