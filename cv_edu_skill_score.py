import sys
import glob
import os

# CV dosyasından Eğitim ve Skill bölümlerini ayıkla (gelişmiş, başlık aramadan bağımsız)
def extract_education_and_skills(text):
    education_lines = []
    keywords_edu = ["bachelor", "master", "university", "degree", "lisans", "yüksek lisans", "üniversite", "diploma", "mezun", "okul"]
    lines = text.splitlines()
    # Eğitim: Satırlarda eğitimle ilgili anahtar kelime arayalım
    for line in lines:
        if any(key in line.lower() for key in keywords_edu):
            education_lines.append(line.strip())
    return education_lines

def extract_skills_anywhere(text, target_skills=None):
    if target_skills is None:
        target_skills = ["python", "sql", "java", "c#", "html", "css", "flutter", "unity", "aws", "azure", "docker", "kubernetes", "linux", "git"]
    t = text.lower()
    matched_skills = []
    for skill in target_skills:
        if skill in t and skill not in matched_skills:
            matched_skills.append(skill)
    return matched_skills

# Basit skorlama fonksiyonu: eğitim puanları geliştirilmiş

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
    return cv_score, school_score, matched_skills, skills_score

if __name__ == "__main__":
    # Komut satırı ile CV dosyası verildiyse onu kullan; verilmezse 'cvler' klasöründeki tüm txt dosyalarını analiz et
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if not os.path.isabs(input_path) and not os.path.exists(input_path):
            input_path = os.path.join("cvler", input_path)
        filenames = [input_path]
    else:
        filenames = glob.glob("cvler/*.txt")

    for cvfile in filenames:
        with open(cvfile, "r", encoding="utf-8") as f:
            text = f.read()
        edu = extract_education_and_skills(text)
        skills = extract_skills_anywhere(text)
        score, sch_score, matched_skills, skills_score = calculate_cv_score(edu, skills)
        print(f"====== {cvfile} ======")
        print("--- Eğitim ---")
        for e in edu:
            print(e)
        print("--- Beceriler ---")
        print(", ".join(skills))
        print("Okul Skoru:", sch_score)
        print("Eşleşen Skills:", matched_skills)
        print("Skill Skoru:", skills_score)
        print("Toplam CV Skoru:", score)
        print("\n==================\n")
