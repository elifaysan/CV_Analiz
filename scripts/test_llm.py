"""LLM bağlantı testi: hangi provider çalışıyor?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.llm import generate

def main():
    prompt = "Merhaba, sadece 'Test OK' yaz."
    print("LLM test ediliyor (provider=auto)...")
    text, err = generate(prompt, provider="auto", max_tokens=50)
    if err:
        print("HATA:", err)
        print("\nÇözüm:")
        print("  1. Ollama: ollama run mistral (ChatGPT benzeri, yerel, ücretsiz)")
        print("  2. OpenAI: .env'e OPENAI_API_KEY=sk-... ekle")
        print("  3. Groq: .env'e GROQ_API_KEY=gsk_... ekle")
        return 1
    print("Yanıt:", text[:200])
    print("OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
