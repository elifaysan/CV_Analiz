import glob
import os
import pdfplumber

def pdf_to_txt(pdf_path, txt_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                all_text += page_text + "\n"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(all_text)

if __name__ == "__main__":
    pdf_files = glob.glob("cvler/*.pdf")
    for pdf_file in pdf_files:
        txt_file = pdf_file[:-4] + ".txt"
        if not os.path.exists(txt_file):
            print(f"Dönüştürülüyor: {pdf_file} -> {txt_file}")
            pdf_to_txt(pdf_file, txt_file)
        else:
            print(f"Zaten var: {txt_file}")

