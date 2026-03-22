"""Flask backend API: CV + GitHub uygunluk analizi."""
import os
import sys
from pathlib import Path

# Proje kökünü path'e ekle
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from flask import Flask, request, jsonify
import pdfplumber

from core.analyzer import analyze_cv_github

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB


def pdf_to_text(pdf_path: str) -> str:
    """PDF dosyasını metne çevir."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    CV (PDF veya TXT) + GitHub username ile analiz.
    Body: form-data
      - cv_file: PDF veya TXT dosyası (gerekli)
      - github_username: opsiyonel, verilmezse CV'den çıkarılmaya çalışılır
      - cv_weight: opsiyonel, varsayılan 0.4
      - gh_weight: opsiyonel, varsayılan 0.6
    """
    if "cv_file" not in request.files and "cv_text" not in request.form:
        return jsonify({"error": "cv_file veya cv_text gerekli"}), 400

    cv_text = None
    if "cv_text" in request.form:
        cv_text = request.form["cv_text"].strip()
    else:
        f = request.files["cv_file"]
        if f.filename == "":
            return jsonify({"error": "Dosya seçilmedi"}), 400
        suffix = Path(f.filename).suffix.lower()
        if suffix == ".pdf":
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                f.save(tmp.name)
                try:
                    cv_text = pdf_to_text(tmp.name)
                finally:
                    os.unlink(tmp.name)
        elif suffix == ".txt":
            cv_text = f.read().decode("utf-8", errors="replace").strip()
        else:
            return jsonify({"error": "Sadece PDF veya TXT destekleniyor"}), 400

    if not cv_text:
        return jsonify({"error": "CV metni boş veya okunamadı"}), 400

    github_username = request.form.get("github_username", "").strip() or None
    try:
        cv_weight = float(request.form.get("cv_weight", 0.4))
        gh_weight = float(request.form.get("gh_weight", 0.6))
    except (TypeError, ValueError):
        cv_weight, gh_weight = 0.4, 0.6

    if abs(cv_weight + gh_weight - 1.0) > 0.01:
        cv_weight, gh_weight = 0.4, 0.6

    result = analyze_cv_github(
        cv_text=cv_text,
        github_username=github_username,
        cv_weight=cv_weight,
        gh_weight=gh_weight,
    )
    return jsonify(result)


@app.route("/analyze/json", methods=["POST"])
def analyze_json():
    """
    JSON body ile analiz: cv_text + github_username.
    """
    data = request.get_json() or {}
    cv_text = data.get("cv_text", "").strip()
    if not cv_text:
        return jsonify({"error": "cv_text gerekli"}), 400

    github_username = data.get("github_username") or None
    cv_weight = float(data.get("cv_weight", 0.4))
    gh_weight = float(data.get("gh_weight", 0.6))
    if abs(cv_weight + gh_weight - 1.0) > 0.01:
        cv_weight, gh_weight = 0.4, 0.6

    result = analyze_cv_github(
        cv_text=cv_text,
        github_username=github_username,
        cv_weight=cv_weight,
        gh_weight=gh_weight,
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
