import json
import sys

# Kullanıcı adı argümanı veya JSON yolu
if len(sys.argv) > 1:
    user_json = sys.argv[1]
else:
    user_json = "github_elifaysan.json"

with open(user_json, "r", encoding="utf-8") as f:
    user_data = json.load(f)

# Gelişmiş skor hesaplama fonksiyonu
def calculate_github_score(user_data):
    # Temel metrikler
    public_repos = user_data.get("public_repos", 0)
    total_stars = sum(repo.get("stars", 0) for repo in user_data.get("repos", []))
    languages = set(user_data.get("languages", []))
    main_lang_bonus = 0
    pop_langs = {"python": 30, "java": 20, "c#": 20, "javascript": 15, "html": 10, "css": 8, "cpp": 18, "go": 15}
    for l in languages:
        main_lang_bonus += pop_langs.get(str(l).lower(), 5)  # Az bilinenlere az puan

    readme_count = sum(1 for repo in user_data.get("repos", []) if repo.get("has_readme"))
    forks = sum(repo.get("forks", 0) for repo in user_data.get("repos", []))
    followers = user_data.get("followers", 0)

    # Basit birleştirilmiş skor (yüzlü band)
    score = 10*public_repos + 2*total_stars + main_lang_bonus + 3*readme_count + 0.5*forks + 2*followers
    details = {
        "public_repos": public_repos,
        "total_stars": total_stars,
        "main_lang_bonus": main_lang_bonus,
        "readme_count": readme_count,
        "forks": forks,
        "followers": followers,
        "score": int(score)
    }
    return details

# Skor ve detayları ekrana bas
github_score_results = calculate_github_score(user_data)
print("----- GITHUB SKOR ANALİZİ -----")
for k,v in github_score_results.items():
    print(f"{k}: {v}")

