"""CV skorlama mantığı (eğitim + beceriler)."""
from typing import List, Tuple, Optional, Dict

DEFAULT_SKILLS = [
    "python", "sql", "java", "c#", "html", "css", "flutter", "unity",
    "aws", "azure", "docker", "kubernetes", "linux", "git"
]

DEFAULT_SCHOOL_WEIGHTS = {
    "istanbul teknik üniversitesi": 100,
    "boğaziçi üniversitesi": 100,
    "hacettepe": 90,
    "kocaeli üniversitesi": 80,
}


def extract_skills(text: str, target_skills: Optional[List[str]] = None) -> List[str]:
    if target_skills is None:
        target_skills = DEFAULT_SKILLS
    t = text.lower()
    matched = []
    for skill in target_skills:
        if skill in t and skill not in matched:
            matched.append(skill)
    return matched


def extract_education_lines(text: str) -> List[str]:
    keywords = [
        "bachelor", "master", "university", "degree", "lisans",
        "yüksek lisans", "üniversite", "diploma", "mezun", "okul"
    ]
    lines = text.splitlines()
    return [line.strip() for line in lines if any(k in line.lower() for k in keywords)]


def calculate_cv_score(
    education_lines: List[str],
    matched_skills: List[str],
    school_weights: Optional[Dict[str, int]] = None,
    skill_score: int = 20,
) -> Tuple[int, int, int]:
    """(toplam_skor, okul_skoru, beceri_skoru) döner."""
    if school_weights is None:
        school_weights = DEFAULT_SCHOOL_WEIGHTS
    school_score = 40
    for line in education_lines:
        for school, weight in school_weights.items():
            if school in line.lower():
                school_score = weight
                break
    skills_score = skill_score * len(matched_skills)
    total = school_score + skills_score
    return total, school_score, skills_score


def analyze_cv(text: str) -> dict:
    """CV metninden skor ve detayları hesapla."""
    edu = extract_education_lines(text)
    skills = extract_skills(text)
    total, school, skills_val = calculate_cv_score(edu, skills)
    return {
        "score": total,
        "school_score": school,
        "skills_score": skills_val,
        "matched_skills": skills,
        "education_lines": edu[:5],  # ilk 5 satır
    }
