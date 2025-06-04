import requests
from django.conf import settings

DEEPSEEK_ENDPOINT = getattr(settings, 'DEEPSEEK_ENDPOINT', 'https://api.deepseek.example/recommend')


def recommend_similar_papers(abstract):
    """Return list of recommended paper IDs using DeepSeek service."""
    payload = {"prompt": f"Recommend academic papers similar to this abstract: {abstract}"}
    try:
        response = requests.post(DEEPSEEK_ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('ids', [])
    except Exception:
        return []
