import sys
import json
import glob
import os

# Kullanım: python fusion_score.py <cv_txt> <github_json>
# Parametreler verilmezse otomatik örneklerle çalışır
cv_score_path = sys.argv[1] if len(sys.argv) > 1 else "cvler/Elif-AYSAN_CV.txt"
github_score_path = sys.argv[2] if len(sys.argv) > 2 else "github_elifaysan.json"

# --- CV Skorunu tekrar hesapla (güncel fonksiyon: cv_edu_skill_score.py'daki ile aynı mantık!)
def extract_skills_anywhere(text, target_skills=None):
    if target_skills is None:
        target_skills = ["python", "sql", "java", "c#", "html", "css", "flutter", "unity", "aws", "azure", "docker", "kubernetes", "linux", "git"]
    t = text.lower()
    matched_skills = []
    for skill in target_skills:
        if skill in t and skill not in matched_skills:
            matched_skills.append(skill)
    return matched_skills

def extract_education_and_skills(text):
    education_lines = []
    keywords_edu = ["bachelor", "master", "university", "degree", "lisans", "yüksek lisans", "üniversite", "diploma", "mezun", "okul"]
    lines = text.splitlines()
    for line in lines:
        if any(key in line.lower() for key in keywords_edu):
            education_lines.append(line.strip())
    return education_lines

def calculate_cv_score(education_lines, matched_skills, school_weights=None, skill_score=20):
    if school_weights is None:
        school_weights = {
            'istanbul teknik üniversitesi': 100,
            'boğaziçi üniversitesi': 100,
            'hacettepe': 90,
            'kocaeli üniversitesi': 80
        }
    school_score = 40
    for line in education_lines:
        for s, weight in school_weights.items():
            if s in line.lower():
                school_score = weight
    skills_score = skill_score * len(matched_skills)
    cv_score = school_score + skills_score
    return cv_score

with open(cv_score_path, "r", encoding="utf-8") as f:
    cv_text = f.read()
edu = extract_education_and_skills(cv_text)
skills = extract_skills_anywhere(cv_text)
cv_score = calculate_cv_score(edu, skills)

# --- GitHub skoru ---
def calculate_github_score(user_data):
    public_repos = user_data.get("public_repos", 0)
    total_stars = sum(repo.get("stars", 0) for repo in user_data.get("repos", []))
    languages = set(user_data.get("languages", []))
    main_lang_bonus = 0
    pop_langs = {"python": 30, "java": 20, "c#": 20, "javascript": 15, "html": 10, "css": 8, "cpp": 18, "go": 15}
    for l in languages:
        main_lang_bonus += pop_langs.get(str(l).lower(), 5)
    readme_count = sum(1 for repo in user_data.get("repos", []) if repo.get("has_readme"))
    forks = sum(repo.get("forks", 0) for repo in user_data.get("repos", []))
    followers = user_data.get("followers", 0)
    score = 10*public_repos + 2*total_stars + main_lang_bonus + 3*readme_count + 0.5*forks + 2*followers
    return int(score)

with open(github_score_path, "r", encoding="utf-8") as f:
    user_data = json.load(f)
github_score = calculate_github_score(user_data)

# FUSION SCORE (ağırlıklar ayarlanabilir)
def fusion_score(cv_score, github_score, cv_weight=0.4, gh_weight=0.6):
    return int(cv_weight*cv_score + gh_weight*github_score)

result = {
    "CV_skoru": cv_score,
    "GitHub_skoru": github_score,
    "Fusion_skoru": fusion_score(cv_score, github_score),
    "Fusion_skoru (CV %60 + GitHub %40)": fusion_score(cv_score, github_score, cv_weight=0.6, gh_weight=0.4)
}

print("==== FUSION (CV+GitHub) UYGUNLUK ANALİZ SONUÇLARI ====")
for k, v in result.items():
    print(f"{k}: {v}")

