"""
Streamlit arayüzü: CV + GitHub uygunluk analizi.
Kullanım: streamlit run streamlit_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pdfplumber
from core.analyzer import analyze_cv_github


def pdf_to_text(uploaded_file) -> str:
    """Yüklenen PDF'den metin çıkar."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp.flush()
        try:
            with pdfplumber.open(tmp.name) as pdf:
                text = ""
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
                return text.strip()
        finally:
            os.unlink(tmp.name)


st.set_page_config(
    page_title="CV + GitHub Uygunluk Skoru",
    page_icon="📋",
    layout="centered",
)

st.title("📋 CV + GitHub Uygunluk Analizi")
st.caption("CV ve GitHub profilinizi analiz ederek bir uygunluk skoru üretir.")

with st.form("analiz_form"):
    cv_input = st.radio(
        "CV girişi",
        ["Dosya yükle (PDF/TXT)", "Metin yapıştır"],
        horizontal=True,
    )
    cv_text = ""
    if cv_input == "Dosya yükle (PDF/TXT)":
        cv_file = st.file_uploader(
            "CV dosyası",
            type=["pdf", "txt"],
            help="PDF veya metin dosyası yükleyin",
        )
        if cv_file:
            suffix = cv_file.name.lower().split(".")[-1]
            if suffix == "pdf":
                cv_text = pdf_to_text(cv_file)
            else:
                cv_text = cv_file.read().decode("utf-8", errors="replace").strip()
    else:
        cv_text = st.text_area(
            "CV metni",
            placeholder="CV içeriğinizi buraya yapıştırın...",
            height=200,
        )

    github_username = st.text_input(
        "GitHub kullanıcı adı (opsiyonel)",
        placeholder="örn: torvalds",
        help="Boş bırakırsanız CV'deki github.com/... linkinden alınır",
    ).strip() or None

    col1, col2 = st.columns(2)
    with col1:
        cv_weight = st.slider("CV ağırlığı (%)", 0, 100, 40) / 100
    with col2:
        gh_weight = st.slider("GitHub ağırlığı (%)", 0, 100, 60) / 100
    if abs(cv_weight + gh_weight - 1.0) > 0.01:
        st.warning("Ağırlıklar toplamı %100 olmalı. Varsayılana dönülüyor.")
        cv_weight, gh_weight = 0.4, 0.6

    submitted = st.form_submit_button("Analiz et")

if submitted:
    if not cv_text:
        st.error("CV metni girin veya dosya yükleyin.")
    else:
        with st.spinner("Analiz yapılıyor..."):
            try:
                result = analyze_cv_github(
                    cv_text=cv_text,
                    github_username=github_username,
                    cv_weight=cv_weight,
                    gh_weight=gh_weight,
                )
            except Exception as e:
                st.exception(e)
                st.stop()

        if result.get("error"):
            st.warning(f"GitHub verisi alınamadı: {result['error']} — Sadece CV skoru gösteriliyor.")

        # Skorlar
        st.subheader("📊 Skorlar")
        cols = st.columns(3)
        cols[0].metric("CV Skoru", result["cv_score"])
        cols[1].metric("GitHub Skoru", result["github_score"] or "—")
        cols[2].metric("Fusion Skoru", result["fusion_score"])

        # Gauge benzeri görsel (basit progress bar)
        fusion = result["fusion_score"]
        max_reasonable = 200
        pct = min(100, 100 * fusion / max_reasonable)
        st.progress(pct / 100, text=f"Uygunluk: {fusion} puan (max ~{max_reasonable})")

        # Açıklamalar
        st.subheader("📝 Açıklama")
        exp = result.get("explanation", {})
        for key, items in [
            ("CV", exp.get("cv_explanation", [])),
            ("GitHub", exp.get("github_explanation", [])),
        ]:
            if items:
                with st.expander(f"{key} skoru nasıl hesaplandı?"):
                    for line in items:
                        st.write(f"• {line}")
        if exp.get("fusion_explanation"):
            with st.expander("Fusion skoru nasıl hesaplandı?"):
                st.write(exp["fusion_explanation"])

        # Detaylar
        with st.expander("Detaylı veriler"):
            st.json({
                "cv_score": result["cv_score"],
                "github_score": result["github_score"],
                "fusion_score": result["fusion_score"],
                "matched_skills": result.get("cv_details", {}).get("matched_skills", []),
                "github_username": result.get("github_username"),
            })
