import json
import numpy as np
import fitz  # PyMuPDF
import boto3
import json
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# สร้าง client สำหรับ AWS Bedrock
bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-west-2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# ฟังก์ชันสำหรับการโหลด embeddings จากไฟล์
def load_embeddings_from_file(file_path):
    with open(file_path, 'r') as f:
        embeddings = json.load(f)
    return embeddings

def generate_query_embedding(query_text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": query_text})
    )
    response_body = json.loads(response["body"].read())
    return response_body["embedding"]

# ฟังก์ชันสำหรับการค้นหาคำถามใน embeddings
def search_query_in_embeddings(query_text, embeddings, texts):
    # สร้าง embedding สำหรับคำถาม
    query_embedding = generate_query_embedding(query_text)

    # คำนวณ cosine similarity ระหว่าง query embedding กับ embeddings ที่โหลดจากไฟล์
    similarities = cosine_similarity([query_embedding], embeddings)

    # คำนวณผลลัพธ์ที่ใกล้เคียงที่สุด
    top_k = 4  # จำนวนผลลัพธ์ที่ต้องการ
    top_k_indices = similarities[0].argsort()[-top_k:][::-1]  # ดัชนีของผลลัพธ์ที่ใกล้เคียงที่สุด

    results = []
    for idx in top_k_indices:
        results.append({
            "text": texts[idx],  # ข้อความที่ตรงกับ embedding
            "similarity": similarities[0][idx]  # ความคล้ายคลึง
        })

    return results


# # โหลด embeddings จากไฟล์
# embeddings_file_path = "/opt/dlami/nvme/workspace/embeddings.json"
# embeddings = load_embeddings_from_file(embeddings_file_path)

# # ตัวอย่างคำถามที่ต้องการค้นหา
# query_text = "ขอวิธีแบริ่ง"

# # ค้นหาคำถามใน embeddings
# results = search_query_in_embeddings(query_text, embeddings, texts)

# # แสดงผลลัพธ์
# print("ผลการค้นหาจาก embeddings:")
# for result in results:
#     print(f"Text: {result['text']}, Similarity: {result['similarity']}")