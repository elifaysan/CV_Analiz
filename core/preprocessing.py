"""CV ve metin ön işleme: temizleme, stopword, tokenization."""
import re
import unicodedata
from typing import List, Optional

# Türkçe + İngilizce stopword listesi (yazılım CV'leri için sadeleştirilmiş)
STOPWORDS_TR = {
    "ve", "veya", "için", "bir", "bu", "şu", "o", "da", "de", "mi", "mı", "mu", "mü",
    "ile", "olan", "olarak", "gibi", "kadar", "daha", "çok", "en", "hiç", "hem",
    "ancak", "ama", "fakat", "ne", "var", "yok", "ise", "ki", "bile", "dahi",
}

STOPWORDS_EN = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "can", "this", "that", "these",
    "those", "i", "you", "he", "she", "it", "we", "they",
}


def normalize_whitespace(text: str) -> str:
    """Fazla boşlukları temizle, satır sonlarını normalize et."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def to_lowercase(text: str) -> str:
    """Küçük harfe çevir (Türkçe karakterler korunur)."""
    return text.lower()


def remove_punctuation(text: str, keep_hyphen: bool = True) -> str:
    """Noktalama işaretlerini kaldır."""
    if keep_hyphen:
        # Tire ve alt çizgi hariç noktalama kaldır (c#, python gibi ifadeler korunur)
        punct = r"""[!"#$%&'()*+,./:;<=>?@[\]^`{|}~]"""
    else:
        punct = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    return re.sub(punct, " ", text)


def remove_stopwords(text: str, lang: str = "both") -> set:
    """Metni tokenlara ayır, stopword'leri çıkar. set (eşsiz kelimeler) döner."""
    stopwords = set()
    if lang in ("tr", "both"):
        stopwords |= STOPWORDS_TR
    if lang in ("en", "both"):
        stopwords |= STOPWORDS_EN
    words = re.findall(r"\b[\w#+]+\b", text.lower())
    return {w for w in words if w not in stopwords and len(w) > 1}


def clean_cv_text(
    text: str,
    lowercase: bool = True,
    normalize_ws: bool = True,
    remove_punct: bool = False,
    remove_stop: bool = False,
) -> str:
    """
    CV metnini ön işleme tabi tut.
    Embedding için: remove_punct=False, remove_stop=False (anlamsal bütünlük için).
    Anahtar kelime çıkarma için: remove_punct=True, remove_stop=True.
    """
    if not text:
        return ""
    if normalize_ws:
        text = normalize_whitespace(text)
    if lowercase:
        text = to_lowercase(text)
    if remove_punct:
        text = remove_punctuation(text)
    if remove_stop:
        words = remove_stopwords(text)
        text = " ".join(sorted(words))  # sıralı birleşim
    return text.strip()


def tokenize_simple(text: str) -> List[str]:
    """Basit tokenization: kelime sınırlarına göre böl."""
    text = normalize_whitespace(remove_punctuation(text))
    return text.lower().split()
