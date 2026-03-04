"""
AI Engine — Google Gemini integration for product categorization.
Handles API calls, response parsing, and retry logic.
"""
import os
import json
import time
from pathlib import Path

import google.generativeai as genai

from lib.logger import logger
from lib.text_processor import prepare_description
from models.product_schema import ProductMetadata


# Load the system prompt
PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPT_DIR, "system_prompt.txt")


def _load_system_prompt() -> str:
    """Load the system prompt from file."""
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        return f.read().strip()


# Valid primary categories
VALID_CATEGORIES = ["Electronics", "Sustainable Living", "Fashion", "Home Decor"]


class GeminiEngine:
    """Wraps Google Gemini API for product categorization."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found! Set it in .env or as an environment variable. "
                "Get a free key at https://aistudio.google.com/app/apikey"
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=_load_system_prompt(),
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
                response_mime_type="application/json",
            ),
        )
        logger.info("Gemini AI engine initialized (model: gemini-2.5-flash)")

    def categorize_product(
        self, description: str, product_name: str = None, retries: int = 3
    ) -> ProductMetadata:
        """
        Analyze a product description and return structured metadata.

        Args:
            description: Product description text
            product_name: Optional product name for better accuracy
            retries: Number of retry attempts on rate-limit errors

        Returns:
            ProductMetadata with categories, tags, and sustainability filters
        """
        prompt_input = prepare_description(description, product_name)
        logger.info(f"Analyzing product: {(product_name or description[:60])!r}")

        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt_input)
                raw_text = response.candidates[0].content.parts[0].text
                result = self._parse_response(raw_text)
                logger.info(
                    f"Result: {result.primary_category}/{result.sub_category} "
                    f"({len(result.seo_tags)} tags, {len(result.sustainability_filters)} filters)"
                )
                return result

            except Exception as e:
                error_name = type(e).__name__
                if "ResourceExhausted" in error_name or "429" in str(e):
                    wait = 6 + (attempt * 4)
                    logger.warning(
                        f"Rate limit hit (attempt {attempt + 1}/{retries}). Waiting {wait}s before retry..."
                    )
                    time.sleep(wait)
                elif attempt < retries - 1:
                    logger.warning(f"Error on attempt {attempt + 1}: {e}. Retrying...")
                    time.sleep(1)
                else:
                    logger.error(f"All {retries} attempts failed: {e}")
                    raise

        raise RuntimeError("All retry attempts exhausted")

    def _parse_response(self, raw_text: str) -> ProductMetadata:
        """Parse Gemini's JSON response into ProductMetadata."""
        try:
            # Clean response — strip markdown code fences if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)

            # Validate primary category is from predefined list
            category = data.get("primary_category", "")
            if category not in VALID_CATEGORIES:
                # Find closest match
                best = min(
                    VALID_CATEGORIES,
                    key=lambda c: self._levenshtein(c.lower(), category.lower()),
                )
                logger.warning(f"AI returned '{category}', corrected to '{best}'")
                data["primary_category"] = best

            # Ensure seo_tags has 5-10 items
            tags = data.get("seo_tags", [])
            if len(tags) < 5:
                logger.warning(f"Only {len(tags)} tags generated, expected 5-10")
            data["seo_tags"] = tags[:10]  # cap at 10

            return ProductMetadata(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}\nRaw: {raw_text}")
            raise ValueError(f"AI returned invalid JSON: {e}")

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        """Simple Levenshtein distance for fuzzy category matching."""
        if len(s1) < len(s2):
            return GeminiEngine._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]