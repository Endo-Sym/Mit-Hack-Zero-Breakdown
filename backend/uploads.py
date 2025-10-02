import fitz  # PyMuPDF

# ฟังก์ชันสำหรับการ extrach file เป็น text 
def extract_text_fitz(pdf_path):
    # เปิดไฟล์ PDF ด้วย PyMuPDF
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # โหลดหน้า
        full_text += page.get_text()  # ดึงข้อความจากแต่ละหน้า
    return full_text


# ฟังก์ชันสำหรับการโหลด embeddings จากไฟล์
def load_embeddings_from_file(file_path):
    with open(file_path, 'r') as f:
        embeddings = json.load(f)
    return embeddings

def generate_embeddings(texts):
    embeddings = []
    for text in texts:
        response = bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": text})
        )
        response_body = json.loads(response["body"].read())
        embeddings.append(response_body["embedding"])
    return embeddings

def save_embedding(texts):
    text_fitz = extract_text_fitz(pdf_path)

    # ตรวจสอบว่า `text_fitz` ไม่ว่างและมีข้อความที่ต้องการ
    if not text_fitz.strip():
        print("ไม่พบข้อความจากไฟล์ PDF")
    else:
        # แบ่งข้อความเป็นบรรทัดหรือพารากราฟ
        texts = text_fitz.split("\n")  # หรือคุณสามารถแบ่งตามพารากราฟ

        # กรองข้อความว่างออก
        texts = [text for text in texts if text.strip()]  # กรองข้อความว่างออก

        # สร้าง embeddings จากข้อความที่ดึงมา
        embeddings = generate_embeddings(texts)

        # บันทึก embeddings ลงไฟล์
        output_path = "/opt/dlami/nvme/embeddings.json"
        with open(output_path, 'w') as f:
            json.dump(embeddings, f)

        print(f"Embeddings saved to {output_path}")

