"""
LLM entegrasyonu: OpenAI, Groq ve Ollama (yerel) destekli.
API key: .env dosyasından veya OPENAI_API_KEY / GROQ_API_KEY ortam değişkeninden.
Ollama: Yerel, ücretsiz, API key gerekmez (ollama run llama3 vb. ile başlat).
"""
import os
from pathlib import Path
from typing import Optional

# .env yükle (proje kökünden)
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass


def _get_openai_client():
    """OpenAI client - lazy import."""
    try:
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY")
        if not key or key.strip() == "":
            return None, "OPENAI_API_KEY tanımlı değil (.env veya ortam değişkeni)"
        return OpenAI(api_key=key.strip()), None
    except ImportError:
        return None, "openai paketi yüklü değil (pip install openai)"


def _get_groq_client():
    """Groq client - OpenAI uyumlu API (https://api.groq.com/openai/v1)."""
    try:
        from openai import OpenAI
        key = os.environ.get("GROQ_API_KEY")
        if not key or key.strip() == "":
            return None, "GROQ_API_KEY tanımlı değil (.env veya ortam değişkeni)"
        return OpenAI(api_key=key.strip(), base_url="https://api.groq.com/openai/v1"), None
    except ImportError:
        return None, "openai paketi yüklü değil (pip install openai)"


def _ollama_generate(
    prompt: str,
    model: str,
    base_url: str,
    max_tokens: int,
    system_prompt: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """Ollama /api/chat ile üretim (yerel)."""
    try:
        import httpx
        url = f"{base_url.rstrip('/')}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = httpx.post(
            url,
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"num_predict": max_tokens},
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("message", {})
        return (msg.get("content", "") or "").strip(), None
    except Exception as e:
        return "", f"Ollama hatası: {e}"


def generate(
    prompt: str,
    provider: str = "auto",
    model: Optional[str] = None,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """
    LLM'den metin üret.
    Returns: (response_text, error_message)
    provider: "openai" | "groq" | "ollama" | "auto"
    auto sırası: ollama → openai → groq (ücretsiz önce)
    """
    if provider == "auto":
        # Önce ücretsiz/yerel: ollama, sonra groq (ücretsiz tier), sonra openai
        order = ("ollama", "groq", "openai")
        for p in order:
            text, err = generate(prompt, provider=p, model=model, max_tokens=max_tokens, system_prompt=system_prompt)
            if err is None and (text or "").strip():
                return text, None
        return "", "Hiçbir LLM kullanılamadı. Ollama çalışıyor mu? veya OPENAI_API_KEY / GROQ_API_KEY tanımlı mı?"

    if provider == "ollama":
        base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        # mistral: ChatGPT benzeri | phi3:mini daha küçük alternatif
        model = model or os.environ.get("OLLAMA_MODEL", "mistral")
        return _ollama_generate(prompt, model, base, max_tokens, system_prompt)

    if provider == "openai":
        client, err = _get_openai_client()
        if err:
            return "", err
        model = model or "gpt-4o-mini"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            r = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens)
            return (r.choices[0].message.content or "").strip(), None
        except Exception as e:
            return "", str(e)

    if provider == "groq":
        client, err = _get_groq_client()
        if err:
            return "", err
        model = model or "llama-3.1-8b-instant"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            r = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            return (r.choices[0].message.content or "").strip(), None
        except Exception as e:
            return "", str(e)

    return "", f"Bilinmeyen provider: {provider}"


# CV değerlendirmesi için sistem promptu
SYSTEM_PROMPT_CV = """Sen bir insan kaynakları ve yazılım alanında uzman asistanısın. Görevin: CV ve GitHub profillerini inceleyip aday hakkında objektif, yapıcı bir Türkçe değerlendirme yazmak. Teknik becerileri, eğitimi, projeleri ve GitHub aktivitesini dikkate al. Tarafsız ve destekleyici ol."""
