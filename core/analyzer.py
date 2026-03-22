"""Ana analiz pipeline: CV + GitHub verisini alıp skor üretir."""
import os
import re
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from .cv_score import analyze_cv
from .github_score import calculate_github_score
from .explainability import build_full_explanation

# Proje kökü (bu dosya core/ içinde)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def extract_github_username(text: str) -> Optional[str]:
    """CV metninden GitHub kullanıcı adını çıkar."""
    match = re.search(r"github\.com/([A-Za-z0-9-]{4,})", text)
    if match:
        username = re.split(r"[\s,.\)\]/]", match.group(1))[0]
        return username
    match2 = re.search(r"github[:\s]+([A-Za-z0-9-]{4,})", text, re.I)
    if match2:
        username = match2.group(1).lower()
        banned = {"data", "science", "python", "developer", "engineer", "java", "dotnet", "devops", "network"}
        if username not in banned:
            return username
    return None


def fetch_github_data(username: str, token: Optional[str] = None) -> dict:
    """GitHub API ile kullanıcı verisini çek."""
    github_script = PROJECT_ROOT / "github_scraper.py"
    if not github_script.exists():
        raise FileNotFoundError(f"github_scraper.py bulunamadı: {github_script}")

    # Token varsa geçici env ile çalıştır (github_scraper token'ı env'den alacak şekilde güncellenebilir)
    env = os.environ.copy()
    if token:
        env["GITHUB_TOKEN"] = token

    result = subprocess.run(
        [sys.executable, str(github_script), username],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"GitHub scraper hata: {result.stderr}")

    json_path = PROJECT_ROOT / f"github_{username}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"GitHub JSON oluşturulmadı: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def fusion_score(
    cv_score: int,
    gh_score: int,
    cv_weight: float = 0.4,
    gh_weight: float = 0.6,
) -> int:
    """Ağırlıklı birleşik skor."""
    return int(cv_weight * cv_score + gh_weight * gh_score)


def analyze_cv_github(
    cv_text: str,
    github_username: Optional[str] = None,
    github_json: Optional[dict] = None,
    cv_weight: float = 0.4,
    gh_weight: float = 0.6,
    use_rag: bool = False,
    llm_provider: str = "auto",
) -> dict:
    """
    CV metni + (opsiyonel) GitHub ile tam analiz.
    github_username veya github_json verilmeli (ikisi birden verilirse github_json öncelikli).
    """
    cv_result = analyze_cv(cv_text)
    cv_score = cv_result["score"]

    gh_result = None
    gh_error = None
    resolved_username = None
    gh_raw = None  # RAG için ham GitHub JSON
    if github_json:
        gh_raw = github_json
        gh_result = calculate_github_score(github_json)
        resolved_username = github_json.get("login")
    elif github_username:
        try:
            gh_raw = fetch_github_data(github_username)
            gh_result = calculate_github_score(gh_raw)
            resolved_username = github_username
        except Exception as e:
            gh_error = str(e)
    else:
        gh_username_from_cv = extract_github_username(cv_text)
        if gh_username_from_cv:
            try:
                gh_raw = fetch_github_data(gh_username_from_cv)
                gh_result = calculate_github_score(gh_raw)
                resolved_username = gh_username_from_cv
            except Exception as e:
                gh_error = str(e)
        else:
            gh_result = None

    gh_score = gh_result["score"] if gh_result else 0
    fusion = fusion_score(cv_score, gh_score, cv_weight, gh_weight) if gh_result else cv_score

    explanation = build_full_explanation(cv_result, gh_result, fusion, cv_weight, gh_weight)

    result = {
        "cv_score": cv_score,
        "github_score": gh_score if gh_result else None,
        "fusion_score": fusion,
        "cv_details": cv_result,
        "github_details": gh_result,
        "explanation": explanation,
        "github_username": resolved_username,
        "error": gh_error,
    }

    if use_rag:
        try:
            from .rag import rag_assessment
            rag_text, rag_err = rag_assessment(
                cv_text=cv_text,
                github_data=gh_raw,
                cv_score=cv_score,
                gh_score=gh_score if gh_result else None,
                fusion_score=fusion,
                matched_skills=cv_result.get("matched_skills"),
                provider=llm_provider,
            )
            result["rag_assessment"] = rag_text if rag_err is None else None
            result["rag_error"] = rag_err
        except Exception as e:
            result["rag_assessment"] = None
            result["rag_error"] = str(e)

    return result
