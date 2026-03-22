"""Açıklanabilirlik modülü: skor gerekçelerini metin olarak üretir."""
from typing import Dict, Any, List


def explain_cv_score(cv_result: Dict[str, Any]) -> List[str]:
    """CV skorunun nedenlerini madde madde açıkla."""
    reasons = []
    score = cv_result.get("score", 0)
    school = cv_result.get("school_score", 40)
    skills_val = cv_result.get("skills_score", 0)
    skills = cv_result.get("matched_skills", [])

    if school > 40:
        reasons.append(f"Eğitim puanı: {school} (tanınmış üniversite tespit edildi)")
    else:
        reasons.append(f"Eğitim puanı: {school} (varsayılan temel puan)")

    if skills:
        reasons.append(f"Beceri puanı: {skills_val} – CV'de bulunan teknolojiler: {', '.join(skills)}")
    else:
        reasons.append("Beceri puanı: 0 – Aranan teknolojilerden eşleşme bulunamadı")

    reasons.append(f"Toplam CV skoru: {score} (eğitim + beceriler)")
    return reasons


def explain_github_score(gh_result: Dict[str, Any]) -> List[str]:
    """GitHub skorunun nedenlerini madde madde açıkla."""
    reasons = []
    s = gh_result.get("score", 0)
    repos = gh_result.get("public_repos", 0)
    stars = gh_result.get("total_stars", 0)
    readme = gh_result.get("readme_count", 0)
    forks = gh_result.get("forks", 0)
    followers = gh_result.get("followers", 0)
    langs = gh_result.get("languages", [])
    lang_bonus = gh_result.get("main_lang_bonus", 0)

    reasons.append(f"Public repo sayısı: {repos} (×10 puan)")
    reasons.append(f"Toplam yıldız: {stars} (×2 puan)")
    reasons.append(f"README'li repo: {readme} (×3 puan)")
    reasons.append(f"Fork sayısı: {forks} (×0.5 puan)")
    reasons.append(f"Takipçi: {followers} (×2 puan)")
    if langs:
        reasons.append(f"Dil bonusu: {lang_bonus} – Kullanılan diller: {', '.join(langs)}")
    reasons.append(f"Toplam GitHub skoru: {s}")
    return reasons


def explain_fusion(
    cv_score: int,
    gh_score: int,
    fusion_score: int,
    cv_weight: float = 0.4,
    gh_weight: float = 0.6,
) -> str:
    """Birleşik skorun nasıl hesaplandığını açıkla."""
    cv_part = cv_weight * cv_score
    gh_part = gh_weight * gh_score
    return (
        f"Fusion skoru = CV×{cv_weight:.0%} + GitHub×{gh_weight:.0%} = "
        f"{cv_score}×{cv_weight} + {gh_score}×{gh_weight} = "
        f"{cv_part:.1f} + {gh_part:.1f} = {fusion_score}"
    )


def build_full_explanation(
    cv_result: Dict[str, Any],
    gh_result: Dict[str, Any] | None,
    fusion: int,
    cv_weight: float = 0.4,
    gh_weight: float = 0.6,
) -> Dict[str, Any]:
    """Tüm açıklamaları tek yapıda topla."""
    cv_reasons = explain_cv_score(cv_result)
    result = {
        "cv_explanation": cv_reasons,
        "github_explanation": [],
        "fusion_explanation": "",
    }
    if gh_result:
        result["github_explanation"] = explain_github_score(gh_result)
        result["fusion_explanation"] = explain_fusion(
            cv_result["score"],
            gh_result["score"],
            fusion,
            cv_weight,
            gh_weight,
        )
    else:
        result["fusion_explanation"] = "GitHub verisi olmadığı için yalnızca CV skoru kullanıldı."
    return result
