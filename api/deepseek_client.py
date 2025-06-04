"""Client module for interacting with DeepSeek recommendation API."""
from __future__ import annotations

import os
from typing import List

import requests

API_URL = "https://api.deepseek.com/search"  # hypothetical endpoint


def recommend_articles(prompt: str, limit: int = 5) -> List[str]:
    """Query DeepSeek for article recommendations.

    Parameters
    ----------
    prompt: str
        Query constructed from title, abstract and keywords.
    limit: int
        Number of recommendations to request.

    Returns
    -------
    List[str]
        List of article IDs recommended by DeepSeek.
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not configured")

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
    except Exception:
        return []
