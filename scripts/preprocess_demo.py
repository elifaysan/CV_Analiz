"""Ön işleme demo: CV temizleme öncesi/sonrası çıktı."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.preprocessing import clean_cv_text, remove_stopwords

def main():
    path = Path(__file__).parent.parent / "cvler" / "Elif-AYSAN_CV.txt"
    raw = path.read_text(encoding="utf-8")
    sample = raw[:800]

    out = []
    out.append("=" * 60)
    out.append("1. HAM METIN (ilk 800 karakter)")
    out.append("=" * 60)
    out.append(sample)
    out.append("")

    out.append("=" * 60)
    out.append("2. TEMIZLENMIS (normalize + lowercase)")
    out.append("=" * 60)
    cleaned = clean_cv_text(sample, remove_punct=False, remove_stop=False)
    out.append(cleaned[:800])
    out.append("")

    out.append("=" * 60)
    out.append("3. STOPWORD CIKARILMIS - Anahtar kelimeler")
    out.append("=" * 60)
    words = remove_stopwords(sample)
    out.append("Benzersiz kelimeler: " + ", ".join(sorted(words)[:50]))
    out.append(f"Toplam: {len(words)} kelime")
    out.append("")

    out.append("=" * 60)
    out.append("4. TAM TEMIZLIK (punct + stopword)")
    out.append("=" * 60)
    full_clean = clean_cv_text(sample, remove_punct=True, remove_stop=True)
    out.append(full_clean[:600])

    result = "\n".join(out)
    out_path = Path(__file__).parent.parent / "data" / "preprocess_demo_output.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding="utf-8")
    print("Cikti kaydedildi:", out_path)
    return out_path


if __name__ == "__main__":
    main()
