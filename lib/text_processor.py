"""
Text Processor — cleans and prepares product descriptions for AI analysis.
"""
import re
import html


def clean_text(text: str) -> str:
    """Strip HTML tags, decode entities, normalize whitespace."""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate_for_ai(text: str, max_chars: int = 3000) -> str:
    """Smart truncation preserving sentence boundaries."""
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    # Try to break at the last sentence boundary
    last_period = truncated.rfind(".")
    last_newline = truncated.rfind("\n")
    break_point = max(last_period, last_newline)

    if break_point > max_chars * 0.5:
        return truncated[: break_point + 1].strip()

    return truncated.strip() + "..."


def prepare_description(description: str, product_name: str = None) -> str:
    """Prepare the full prompt input from description + optional product name."""
    cleaned = clean_text(description)
    truncated = truncate_for_ai(cleaned)

    if product_name:
        return f"Product Name: {product_name}\n\nProduct Description: {truncated}"
    return f"Product Description: {truncated}"
