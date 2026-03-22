import pandas as pd
import os

# Dosya yolları
csv_path = "resume-dataset/UpdatedResumeDataSet.csv"
target_folder = "cvler"
os.makedirs(target_folder, exist_ok=True)

# Yazılım alanına ait kategoriler (istediklerini artırabilirsin)
keywords = ['software', 'developer', 'engineer', 'programmer', 'python', 'flutter']

df = pd.read_csv(csv_path)

for idx, (category, resume) in enumerate(zip(df['Category'], df['Resume'])):
    cat_lower = str(category).lower()
    if any(kw in cat_lower for kw in keywords):
        filename = f"{target_folder}/cv_{idx}_{category.replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(str(resume))
        print(f"Kayıt edildi: {filename}")

