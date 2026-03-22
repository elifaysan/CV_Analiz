"""
RAG (Retrieval-Augmented Generation) pipeline.
Vektör veritabanından benzer CV'leri çeker, LLM ile değerlendirme üretir.
"""
from pathlib import Path
from typing import Optional

from .vector_store import search_similar, read_cv, github_json_to_text
from .llm import generate, SYSTEM_PROMPT_CV

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_similar_cv_texts(query_text: str, k: int = 3, max_chars_per_cv: int = 800) -> str:
    """Benzer CV'lerin metnini yükle (prompt için)."""
    results = search_similar(query_text, k=k)
    parts = []
    for path_str, dist in results:
        path = PROJECT_ROOT / path_str.replace("\\", "/")
        if not path.exists():
            continue
        text = read_cv(path)
        if len(text) > max_chars_per_cv:
            text = text[:max_chars_per_cv] + "..."
        parts.append(f"[Benzer CV - {path.name}]\n{text}")
    return "\n\n---\n\n".join(parts) if parts else "(Benzer CV bulunamadı)"


def rag_assessment(
    cv_text: str,
    github_data: Optional[dict] = None,
    cv_score: Optional[int] = None,
    gh_score: Optional[int] = None,
    fusion_score: Optional[int] = None,
    matched_skills: Optional[list] = None,
    k_similar: int = 3,
    provider: str = "auto",
) -> tuple[str, Optional[str]]:
    """
    RAG tabanlı uygunluk değerlendirmesi üret.
    Returns: (assessment_text, error)
    """
    similar_context = _load_similar_cv_texts(cv_text, k=k_similar)

    gh_summary = ""
    if github_data:
        gh_summary = github_json_to_text(github_data)

    scores_part = ""
    if cv_score is not None:
        scores_part = f"CV Skoru: {cv_score}"
    if gh_score is not None:
        scores_part += f", GitHub Skoru: {gh_score}"
    if fusion_score is not None:
        scores_part += f", Birleşik Skor: {fusion_score}"
    if scores_part:
        scores_part = "\nHesaplanan skorlar: " + scores_part
    if matched_skills:
        scores_part += f"\nTespit edilen beceriler: {', '.join(matched_skills)}"

    prompt = f"""Aşağıda bir yazılım adayının CV'si ve GitHub profil özeti verilmiş. Ayrıca veritabanından bulunan benzer adayların CV'leri var.

## ADAY CV'Sİ (özet)
{cv_text[:2000]}

## GITHUB PROFİL ÖZETİ
{gh_summary if gh_summary else "(GitHub verisi yok)"}
{scores_part}

## BENZER ADAYLARDAN ÖRNEKLER
{similar_context}

---

Bu aday hakkında Türkçe bir uygunluk değerlendirmesi yaz. Şunları içersin:
1. Genel izlenim (2-3 cümle)
2. Güçlü yönler
3. Geliştirilebilecek alanlar
4. Kısa öneri (1-2 cümle)

Kısa ve öz tut. Madde madde yaz."""

    return generate(prompt, provider=provider, max_tokens=1024, system_prompt=SYSTEM_PROMPT_CV)
