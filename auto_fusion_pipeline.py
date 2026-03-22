import re
import sys
import os
import subprocess
import json

def extract_github_username(text):
    # Sadece github.com/ ile tam bağlantı varsa kullanıcı adını al (en az 4 karakter)
    match = re.search(r"github\.com/([A-Za-z0-9-]{4,})", text)
    if match:
        username = match.group(1)
        # Sonraki karakterde boşluk, nokta, virgül, parantez varsa kırp
        username = re.split(r"[\s,.\)\)\]/]", username)[0]
        return username
    # Alternatif: github: elifaysan (4+ harfli ve unvan olmayan)
    match2 = re.search(r"github[:\s]+([A-Za-z0-9-]{4,})", text, re.I)
    if match2:
        username = match2.group(1).lower()
        banned = {'data','science','python','developer','engineer','java','dotnet','devops','network'}
        if username not in banned:
            return username
    return None

cv_path = sys.argv[1] if len(sys.argv) > 1 else "cvler/Elif-AYSAN_CV.txt"

with open(cv_path, "r", encoding="utf-8") as f:
    cv_text = f.read()

github_username = extract_github_username(cv_text)
if not github_username:
    print("[!] CV'de güvenilir github kullanıcı adı/bağlantısı bulunamadı.")
    print("[!] Sadece CV skoru hesaplanacak!")
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
    edu = extract_education_and_skills(cv_text)
    skills = extract_skills_anywhere(cv_text)
    cv_score = calculate_cv_score(edu, skills)
    print(f"[>>>] CV Skoru: {cv_score}")
    sys.exit(0)
print(f"[+] Github kullanıcı adı: {github_username}")

# Scraper ile GitHub verisini indir
json_filename = f"github_{github_username}.json"
if not os.path.exists(json_filename):
    print(f"[+] GitHub verisi indiriliyor: {github_username}")
    subprocess.run([sys.executable, "github_scraper.py", github_username], check=True)
else:
    print(f"[!] GitHub verisi zaten var: {json_filename}")

print("[+] Fusion skoru hesaplanıyor...")
subprocess.run([sys.executable, "fusion_score.py", cv_path, json_filename], check=True)
