from github import Github
import sys
import json

# Kulanıcı adı parametreli olsun, argüman verilmezse örnek kullanıcı çek
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = "torvalds"  # Örnek; değiştirilebilir

# --TOKEN ZORUNLU DEĞİLSE public API ile çalışır, çok sorgu yapılacaksa Github Token eklenebilir
# g = Github("ACCESS_TOKEN_HERE")
g = Github()

user = g.get_user(username)

# Temel bilgiler
user_data = {
    "login": user.login,
    "name": user.name,
    "bio": user.bio,
    "public_repos": user.public_repos,
    "followers": user.followers,
    "following": user.following,
    "blog": user.blog,
    "location": user.location,
}

# Repoları, dilleri, description özetleri

def list_languages_and_repos(user):
    lang_set = set()
    repo_infos = []
    for repo in user.get_repos():
        lang = repo.language
        if lang: lang_set.add(lang)
        # README.md olup olmadığını güvenli kontrol et
        try:
            files_in_root = [f.name for f in repo.get_contents("")]
            has_readme = "README.md" in [name.upper() for name in files_in_root]
        except Exception:
            has_readme = False
        repo_infos.append({
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "language": lang,
            "has_readme": has_readme
        })
    return lang_set, repo_infos

languages, repos_info = list_languages_and_repos(user)

user_data["languages"] = list(languages)
user_data["repos"] = repos_info

# Kaydet veya ekrana yazdır
outname = f"github_{username}.json"
with open(outname, "w", encoding="utf-8") as f:
    json.dump(user_data, f, ensure_ascii=False, indent=2)

print(f"{username} için Github verisi {outname} dosyasına kaydedildi.")
