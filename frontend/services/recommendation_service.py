"""Business logic for generating article recommendations."""

from collections import OrderedDict
from typing import List, Dict

from api.models import Article, Library
from api.deepseek_client import recommend_articles as deepseek
from frontend.reccom import get_similar_items


def recommend_with_fallback(prompt: str, limit: int = 20) -> List[str]:
    """Return a list of recommended article ids.

    The DeepSeek API is preferred when configured. If it returns no results
    we fall back to the local TF-IDF recommender.
    """
    ids = deepseek(prompt, limit=limit)
    if not ids:
        ids = get_similar_items(prompt, 1, limit)
    return ids


def library_recommendations(library: Library) -> List[Dict]:
    """Return recommendations for all articles in a library."""
    arts = []
    for art in library.articles.all():
        rec = get_similar_items(
            f"{art.title} {art.abstract} {art.source} {art.type}",
            get_scores=True,
        )
        for idx, a in enumerate(Article.objects.filter(pk__in=rec[:, 0])):
            arts.append({"title": a.title, "id": a.pk, "score": float(rec[idx, 1])})
    return sorted(arts, key=lambda item: item["score"], reverse=True)


def summarize_reader_data(article: Article) -> Dict:
    """Collapse detailed reader statistics into friendly categories."""
    data = article.get_json()
    readers_raw = data.get("reader_count_by_academic_status", {})
    subject_raw = data.get("reader_count_by_subject_area", {})

    readers: Dict[str, int] = {}
    for key, val in readers_raw.items():
        if key in {"Proffesor", "Researcher", "Librarian"}:
            readers["Proffesor/ Researcher/ Librarian"] = readers.get(
                "Proffesor/ Researcher/ Librarian", 0
            ) + val
        elif key in {"Lecturer", "Lecturer > Senior Lecturer", "Student  > Doctoral Student"}:
            readers["Senior Lecturer/ Lecturer/ Doctorate"] = readers.get(
                "Senior Lecturer/ Lecturer/ Doctorate", 0
            ) + val
        elif key in {
            "Student  > Master",
            "Student  > Bachelor",
            "Student  > Postgraduate",
            "Student  > Ph. D. Student",
        }:
            readers["Postgrads/ Masters/ Bachelors"] = readers.get(
                "Postgrads/ Masters/ Bachelors", 0
            ) + val
        else:
            readers["Others"] = readers.get("Others", 0) + val

    subject: Dict[str, int] = {}
    for key, val in subject_raw.items():
        if key in {"Design", "Philosophy", "Linguistics", "Arts and Humanities"}:
            subject["Arts and Humanities/ Design/ Philosophy"] = subject.get(
                "Arts and Humanities/ Design/ Philosophy", 0
            ) + val
        elif key in {"Engineering", "Chemical Engineering"}:
            subject["Engineering"] = subject.get("Engineering", 0) + val
        elif key in {
            "Environmental Science",
            "Energy",
            "Earth and Planetary Sciences",
            "Materials Science",
        }:
            subject["Environment/ Planetary Sciences/ Energy"] = subject.get(
                "Environment/ Planetary Sciences/ Energy", 0
            ) + val
        elif key in {"Psychology", "Neuroscience"}:
            subject["Psychology/ Neuroscience"] = subject.get(
                "Psychology/ Neuroscience", 0
            ) + val
        elif key in {"Social Sciences"}:
            subject["Social Sciences"] = subject.get("Social Sciences", 0) + val
        elif key in {
            "Mathematics",
            "Physics and Astronomy",
            "Chemistry",
            "Computer Science",
        }:
            subject["Mathematics/ Physics/ Chemistry/ Computers"] = subject.get(
                "Mathematics/ Physics/ Chemistry/ Computers", 0
            ) + val
        elif key in {
            "Medicine and Dentistry",
            "Immunology and Microbiology",
            "Agricultural and Biological Sciences",
        }:
            subject["Medicine/ Biology/ Agricultural Sciences"] = subject.get(
                "Medicine/ Biology/ Agricultural Sciences", 0
            ) + val
        elif key in {
            "Nursing and Health Proffesions",
            "Pharmacology, Toxicology and Pharmaceutical Science",
            "Veterinary Science and Veterinary Medicine",
        }:
            subject["Nursing/ Pharmacology/ Toxicology/ Veterinary"] = subject.get(
                "Nursing/ Pharmacology/ Toxicology/ Veterinary", 0
            ) + val
        elif key in {"Economics, Econometrics and Finance", "Business, Management and Accounting"}:
            subject[
                "Business/ Management/ Accounting/ Economics"
            ] = subject.get(
                "Business/ Management/ Accounting/ Economics", 0
            ) + val
        elif key in {"Sports and Recreations"}:
            subject["Sports and Recreation"] = subject.get("Sports and Recreation", 0) + val

    subject = OrderedDict(
        sorted(subject.items(), key=lambda x: x[1], reverse=True)[:4]
    )
    return {"readers": readers, "readers_by_sub": subject}


