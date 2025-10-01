import fitz  # PyMuPDF

def extract_text_fitz(pdf_path):
    # เปิดไฟล์ PDF ด้วย PyMuPDF
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # โหลดหน้า
        full_text += page.get_text()  # ดึงข้อความจากแต่ละหน้า
    return full_text

