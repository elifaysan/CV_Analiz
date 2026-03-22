"""
Vektör veritabanı: CV embedding'leri, FAISS index, kalıcı kayıt.
Faz 1: Veri toplama ve ön işleme sonrası embedding + index oluşturma.
"""
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .preprocessing import clean_cv_text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CV_FOLDER = PROJECT_ROOT / "cvler"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Windows'ta FAISS Unicode path (Masaüstü vb.) ile hata veriyor; TEMP kullan
def _data_dir() -> Path:
    p = str(PROJECT_ROOT)
    if sys.platform == "win32" and any(ord(c) > 127 for c in p):
        return Path(os.environ.get("TEMP", ".")) / "cv_analiz_data"
    return PROJECT_ROOT / "data"

DATA_DIR = _data_dir()
INDEX_PATH = DATA_DIR / "cv_faiss.index"
MAP_PATH = DATA_DIR / "cv_faiss_map.json"


def get_cv_files(folder: Optional[Path] = None) -> List[Path]:
    """cvler/ içindeki tüm .txt dosyalarını listele."""
    folder = folder or CV_FOLDER
    if not folder.exists():
        return []
    return sorted(folder.glob("*.txt"))


def read_cv(path: Path) -> str:
    """CV dosyasını oku."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def github_json_to_text(gh_data: dict) -> str:
    """GitHub JSON'dan embeddable profil metni oluştur."""
    parts = [f"GitHub: {gh_data.get('login', '')}"]
    if gh_data.get("bio"):
        parts.append(f"Bio: {gh_data['bio']}")
    langs = gh_data.get("languages", [])
    if langs:
        parts.append(f"Diller: {', '.join(langs)}")
    parts.append(f"Public repo: {gh_data.get('public_repos', 0)}")
    parts.append(f"Takipçi: {gh_data.get('followers', 0)}")
    for repo in gh_data.get("repos", [])[:15]:
        name = repo.get("name", "")
        desc = repo.get("description") or ""
        lang = repo.get("language") or ""
        stars = repo.get("stars", 0)
        line = f"- {name}: {desc} [{lang}] yıldız:{stars}"
        parts.append(line.strip())
    return "\n".join(parts)


def get_github_json_files(folder: Optional[Path] = None) -> List[Path]:
    """Proje kökündeki github_*.json dosyalarını listele."""
    folder = folder or PROJECT_ROOT
    return sorted(folder.glob("github_*.json"))


def build_cv_index(
    cv_folder: Optional[Path] = None,
    use_preprocessing: bool = True,
    model_name: str = MODEL_NAME,
    index_path: Optional[Path] = None,
    map_path: Optional[Path] = None,
) -> Tuple[faiss.Index, List[str]]:
    """
    Tüm CV'leri oku, ön işle, embed et, FAISS index oluştur.
    Index ve mapping'i diske kaydeder.
    """
    cv_folder = cv_folder or CV_FOLDER
    index_path = index_path or INDEX_PATH
    map_path = map_path or MAP_PATH

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    files = get_cv_files(cv_folder)
    if not files:
        raise FileNotFoundError(f"CV dosyası bulunamadı: {cv_folder}")

    model = SentenceTransformer(model_name)
    texts = []
    file_paths = []

    for path in files:
        raw = read_cv(path)
        if use_preprocessing:
            text = clean_cv_text(
                raw,
                lowercase=False,
                normalize_ws=True,
                remove_punct=False,
                remove_stop=False,
            )
        else:
            text = raw.strip()
        if len(text) < 10:
            continue
        texts.append(text)
        file_paths.append(str(path.relative_to(PROJECT_ROOT)))

    embeddings = model.encode(texts, show_progress_bar=len(texts) > 20)
    vectors = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    idx_path = Path(index_path)
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(idx_path))
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(
            {"files": file_paths, "model": model_name, "dim": vectors.shape[1]},
            f,
            ensure_ascii=False,
            indent=2,
        )

    return index, file_paths


def load_cv_index(
    index_path: Optional[Path] = None,
    map_path: Optional[Path] = None,
) -> Tuple[faiss.Index, List[str]]:
    """Kaydedilmiş FAISS index ve mapping'i yükle."""
    index_path = index_path or INDEX_PATH
    map_path = map_path or MAP_PATH

    if not index_path.exists():
        raise FileNotFoundError(
            f"Index bulunamadı: {index_path}. Önce build_cv_index() çalıştırın."
        )

    index = faiss.read_index(str(index_path))
    with open(map_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta["files"]


def build_github_index(
    model_name: str = MODEL_NAME,
    index_path: Optional[Path] = None,
    map_path: Optional[Path] = None,
) -> Tuple[faiss.Index, List[str]]:
    """
    Mevcut github_*.json dosyalarını oku, profil metnine çevir, embed et.
    Ayrı bir index olarak data/github_faiss.index'e kaydeder.
    """
    index_path = index_path or (DATA_DIR / "github_faiss.index")
    map_path = map_path or (DATA_DIR / "github_faiss_map.json")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    gh_files = get_github_json_files()
    if not gh_files:
        raise FileNotFoundError(f"GitHub JSON bulunamadı: {PROJECT_ROOT}/github_*.json")

    model = SentenceTransformer(model_name)
    texts = []
    file_paths = []

    for path in gh_files:
        with open(path, "r", encoding="utf-8") as f:
            gh_data = json.load(f)
        text = github_json_to_text(gh_data)
        if len(text) < 20:
            continue
        texts.append(text)
        file_paths.append(str(path.relative_to(PROJECT_ROOT)))

    embeddings = model.encode(texts, show_progress_bar=False)
    vectors = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    Path(index_path).parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(
            {"files": file_paths, "model": model_name, "dim": vectors.shape[1]},
            f,
            ensure_ascii=False,
            indent=2,
        )
    return index, file_paths


def search_similar(
    query_text: str,
    k: int = 5,
    index_path: Optional[Path] = None,
    map_path: Optional[Path] = None,
    model_name: str = MODEL_NAME,
    use_preprocessing: bool = True,
) -> List[Tuple[str, float]]:
    """
    Sorgu metnine en benzer k CV'yi bul.
    [(file_path, L2_distance), ...] döner (mesafe küçüldükçe benzerlik artar).
    """
    index, file_paths = load_cv_index(index_path or INDEX_PATH, map_path or MAP_PATH)
    model = SentenceTransformer(model_name)

    if use_preprocessing:
        query_text = clean_cv_text(
            query_text,
            lowercase=False,
            normalize_ws=True,
            remove_punct=False,
            remove_stop=False,
        )

    emb = model.encode([query_text]).astype("float32")
    D, I = index.search(emb, min(k, index.ntotal))

    results = []
    for i, idx in enumerate(I[0]):
        if idx >= 0 and idx < len(file_paths):
            results.append((file_paths[idx], float(D[0][i])))
    return results


if __name__ == "__main__":
    """Index oluştur: python -m core.vector_store"""
    print("CV embedding + FAISS index oluşturuluyor...")
    index, files = build_cv_index()
    print(f"CV: {len(files)} dosya indekslendi -> {INDEX_PATH}")

    gh_files = get_github_json_files()
    if gh_files:
        print("GitHub profil index oluşturuluyor...")
        build_github_index()
        print(f"GitHub: {len(gh_files)} profil indekslendi -> {DATA_DIR / 'github_faiss.index'}")
    else:
        print("GitHub JSON bulunamadı, atlanıyor.")

    print("Faz 1 index oluşturma tamamlandı.")
