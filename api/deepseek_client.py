"""Utilities for interacting with the DeepSeek recommendation service."""

from __future__ import annotations

import logging
import os
from typing import List

import requests


API_URL = "https://api.deepseek.com/search"  # Hypothetical endpoint.

logger = logging.getLogger(__name__)


def recommend_articles(prompt: str, limit: int = 5) -> List[str]:
    """Return a list of article IDs recommended by DeepSeek.

    Parameters
    ----------
    prompt:
        Text used for the search prompt.
    limit:
        Maximum number of results to return.

    Returns
    -------
    List[str]
        A list of article identifiers sorted by relevance.  An empty list is
        returned if the request fails or no results were found.
    """

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logger.warning("DEEPSEEK_API_KEY not configured")
        return []

    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"query": prompt, "limit": limit},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("ids", [])
    except Exception as exc:  # noqa: BLE001
        logger.exception("DeepSeek request failed: %s", exc)
        return []

