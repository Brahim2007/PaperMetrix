"""Utility functions for TF‑IDF based recommendations."""

import os
import pickle
from typing import List, Tuple

import numpy as np
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from api.models import Article


TFIDF_MATRIX_PATH = os.path.join(settings.BASE_DIR, "tfidf.pickle")
TFIDF_FIT_PATH = os.path.join(settings.BASE_DIR, "tfidf_fit.pickle")

TFIDF_MATRIX = None
TFIDF_FIT = None
ARTICLE_IDS: List[int] = []


def rebuild_tfidf_matrix() -> None:
    """Recompute the TF‑IDF matrix and persist it to disk."""
    global TFIDF_MATRIX, TFIDF_FIT, ARTICLE_IDS

    ARTICLE_IDS = []
    joined: List[str] = []
    for art in Article.objects.all():
        ARTICLE_IDS.append(art.pk)
        joined.append(f"{art.title} {art.abstract} {art.source} {art.type}")

    tf = TfidfVectorizer(analyzer="word", ngram_range=(1, 3), min_df=1, stop_words="english")
    TFIDF_FIT = tf.fit(joined)
    TFIDF_MATRIX = TFIDF_FIT.transform(joined)

    with open(TFIDF_MATRIX_PATH, "wb") as f:
        pickle.dump(TFIDF_MATRIX, f)
    with open(TFIDF_FIT_PATH, "wb") as f:
        pickle.dump(TFIDF_FIT, f)


def load_tfidf_matrix() -> None:
    """Load the TF‑IDF matrix from disk or build it if missing."""
    global TFIDF_MATRIX, TFIDF_FIT, ARTICLE_IDS

    if os.path.exists(TFIDF_MATRIX_PATH) and os.path.exists(TFIDF_FIT_PATH):
        ARTICLE_IDS = list(Article.objects.values_list("pk", flat=True))
        try:
            with open(TFIDF_MATRIX_PATH, "rb") as f:
                TFIDF_MATRIX = pickle.load(f)
            with open(TFIDF_FIT_PATH, "rb") as f:
                TFIDF_FIT = pickle.load(f)
            if TFIDF_MATRIX.shape[0] != len(ARTICLE_IDS):
                rebuild_tfidf_matrix()
        except Exception:
            rebuild_tfidf_matrix()
    else:
        rebuild_tfidf_matrix()


def get_similar_items(query: str, start: int = 0, end: int = 50, get_scores: bool = False):
    """Return article ids (and optionally scores) similar to the query."""
    if TFIDF_MATRIX is None or TFIDF_FIT is None:
        load_tfidf_matrix()

    que = TFIDF_FIT.transform([query])
    sim_ = cosine_similarity(TFIDF_MATRIX, que).reshape(-1)
    similar_indices = sim_.argsort()[::-1][start:end]
    if get_scores:
        return np.array([(ARTICLE_IDS[i], sim_[i]) for i in similar_indices])
    return [ARTICLE_IDS[i] for i in similar_indices]


# Load the matrix when the module is imported so recommendations are fast.

