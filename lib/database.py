"""
Database module — JSON file-based storage for product analysis history.
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from models.product_schema import ProductRecord, ProductMetadata
from lib.logger import logger


DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
DB_FILE = os.path.join(DB_DIR, "products_db.json")


def _ensure_db():
    """Ensure the database file exists."""
    Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)


def save_record(description: str, metadata: ProductMetadata, product_name: str = None) -> ProductRecord:
    """Save a product analysis result to the database."""
    _ensure_db()

    record = ProductRecord(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now().isoformat(),
        product_name=product_name,
        description=description[:500],  # Store truncated description
        metadata=metadata,
    )

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        data = []

    data.insert(0, record.model_dump())  # newest first

    # Keep only last 100 records
    data = data[:100]

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

    logger.info(f"Saved record {record.id} — {metadata.primary_category}/{metadata.sub_category}")
    return record


def get_history(limit: int = 20) -> List[dict]:
    """Retrieve recent product analysis records."""
    _ensure_db()

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    return data[:limit]


def clear_history() -> int:
    """Clear all stored records. Returns count of deleted records."""
    _ensure_db()

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        count = len(data)
    except (json.JSONDecodeError, FileNotFoundError):
        count = 0

    with open(DB_FILE, "w") as f:
        json.dump([], f)

    logger.info(f"Cleared {count} records from database")
    return count
