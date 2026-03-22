"""GitHub profil skorlama mantığı."""
from typing import Dict, Any, List


def calculate_github_score(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """GitHub JSON'dan ham skor ve detayları hesapla."""
    public_repos = user_data.get("public_repos", 0)
    total_stars = sum(r.get("stars", 0) for r in user_data.get("repos", []))
    languages = set(user_data.get("languages", []))
    pop_langs = {
        "python": 30, "java": 20, "c#": 20, "javascript": 15,
        "html": 10, "css": 8, "cpp": 18, "go": 15
    }
    main_lang_bonus = sum(pop_langs.get(str(l).lower(), 5) for l in languages)
    readme_count = sum(1 for r in user_data.get("repos", []) if r.get("has_readme"))
    forks = sum(r.get("forks", 0) for r in user_data.get("repos", []))
    followers = user_data.get("followers", 0)

    score = (
        10 * public_repos
        + 2 * total_stars
        + main_lang_bonus
        + 3 * readme_count
        + 0.5 * forks
        + 2 * followers
    )
    return {
        "score": int(score),
        "public_repos": public_repos,
        "total_stars": total_stars,
        "main_lang_bonus": main_lang_bonus,
        "readme_count": readme_count,
        "forks": forks,
        "followers": followers,
        "languages": list(languages),
    }
