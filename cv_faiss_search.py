from sentence_transformers import SentenceTransformer
import faiss
import glob
import os
import numpy as np

# Tüm txt dosyalarını listele
def get_txt_files(folder="cvler"):
    return glob.glob(os.path.join(folder, "*.txt"))

def get_text_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    txt_files = get_txt_files()
    texts = []
    embeddings = []
    file_map = []

    for txt_file in txt_files:
        text = get_text_from_file(txt_file)
        emb = model.encode(text)
        texts.append(text)
        embeddings.append(emb)
        file_map.append(txt_file)

    # FAISS için numpy array yapısına dönüştür
    vectors = np.array(embeddings).astype("float32")
    faiss_index = faiss.IndexFlatL2(vectors.shape[1])
    faiss_index.add(vectors)

    print(f"{len(file_map)} CV indekslendi.")

    # Kullanıcıdan örnek bir txt dosyası seçmesini iste
    print("--- Benzerlik sorgusu yapmak için bir CV dosyası seçin (örn: cvler/Elif-AYSAN_CV.txt) ---")
    query_file = input("Sorgulamak istediğiniz CV dosyasını yazın: ").strip()
    query_text = get_text_from_file(query_file)
    query_emb = model.encode(query_text).reshape(1, -1)
    D, I = faiss_index.search(query_emb, k=3)  # En yakın 3 sonuç
    print("\nEn benzer 3 CV:")
    for rank, idx in enumerate(I[0]):
        print(f"{rank+1}) Dosya: {file_map[idx]}, Mesafe: {D[0][rank]:.4f}")

