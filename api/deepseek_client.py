"""Client utilities for interacting with the DeepSeek API."""

from __future__ import annotations

import logging
import os
from typing import List

import requests


DEEPSEEK_ENDPOINT = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/recommend")


def get_deepseek_recommendations(prompt: str) -> List[str]:
    """Return a list of recommendations from the DeepSeek API.

    Parameters
    ----------
    prompt : str
        The input text containing the article title and abstract.

    Returns
    -------
    list[str]
        A list of article identifiers or keywords returned by DeepSeek. If the
        API call fails or no API key is present, an empty list is returned.
    """

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logging.error("DEEPSEEK_API_KEY environment variable not set.")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {"prompt": prompt}

    try:
        response = requests.post(DEEPSEEK_ENDPOINT, json=data, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:  # network or http errors
        logging.exception("DeepSeek API request failed: %s", exc)
        return []

    try:
        payload = response.json()
    except ValueError as exc:
        logging.exception("Unable to decode DeepSeek response: %s", exc)
        return []

    recommendations = payload.get("data") or payload.get("recommendations")
    if isinstance(recommendations, list):
        return recommendations

    logging.error("DeepSeek response did not contain a recommendation list.")
    return []
