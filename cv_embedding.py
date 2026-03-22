from sentence_transformers import SentenceTransformer
import glob
import os

# cvler klasöründeki tüm txt dosyalarını listele
def get_txt_files(folder="cvler"):
    return glob.glob(os.path.join(folder, "*.txt"))

def get_text_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Türkçe ve İngilizce metinlerde çok iyi çalışan bir model!
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    txt_files = get_txt_files()

    for txt_file in txt_files:
        text = get_text_from_file(txt_file)
        embedding = model.encode(text)
        print(f"{txt_file} için embedding vektör boyutu: {embedding.shape}")
        print(embedding[:10])  # İlk 10 değeri göster (tüm vektör çok uzun!)
        print("="*40)

