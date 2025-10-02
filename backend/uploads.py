import fitz  # PyMuPDF
import json
import boto3
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Bedrock setup
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Directory to store embeddings - AWS Cloud Path
EMBEDDINGS_DIR = "/opt/dlami/nvme/embeddings"
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# ฟังก์ชันสำหรับการ extract file เป็น text
def extract_text_fitz(pdf_path):
    """Extract text from PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        full_text += page.get_text()
    return full_text


def generate_embeddings(texts):
    """Generate embeddings using AWS Bedrock Titan"""
    embeddings = []
    for text in texts:
        response = bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": text})
        )
        response_body = json.loads(response["body"].read())
        embeddings.append(response_body["embedding"])
    return embeddings


def save_embedding(pdf_path, custom_name=None):
    """
    Save embeddings from PDF to JSON file

    Args:
        pdf_path: Path to PDF file
        custom_name: Optional custom name for the embedding file

    Returns:
        dict: Information about saved embedding file
    """
    text_fitz = extract_text_fitz(pdf_path)

    # ตรวจสอบว่า text_fitz ไม่ว่างและมีข้อความที่ต้องการ
    if not text_fitz.strip():
        raise ValueError("ไม่พบข้อความจากไฟล์ PDF")

    # แบ่งข้อความเป็นบรรทัดหรือพารากราฟ
    texts = text_fitz.split("\n")

    # กรองข้อความว่างออก
    texts = [text for text in texts if text.strip()]

    # สร้าง embeddings จากข้อความที่ดึงมา
    embeddings = generate_embeddings(texts)

    # สร้างชื่อไฟล์
    if custom_name:
        filename = f"{custom_name}.json"
    else:
        # ใช้ชื่อไฟล์ PDF + timestamp
        pdf_name = Path(pdf_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{pdf_name}_{timestamp}.json"

    output_path = os.path.join(EMBEDDINGS_DIR, filename)

    # สร้างโครงสร้างข้อมูลที่จะบันทึก
    embedding_data = {
        "metadata": {
            "source_file": os.path.basename(pdf_path),
            "created_at": datetime.now().isoformat(),
            "num_texts": len(texts),
            "num_embeddings": len(embeddings),
            "custom_name": custom_name or pdf_name
        },
        "texts": texts,
        "embeddings": embeddings
    }

    # บันทึก embeddings ลงไฟล์
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(embedding_data, f, ensure_ascii=False, indent=2)

    return {
        "filename": filename,
        "path": output_path,
        "num_embeddings": len(embeddings),
        "size_mb": os.path.getsize(output_path) / (1024 * 1024)
    }


def load_embeddings_from_file(file_path):
    """Load embeddings from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def list_embedding_files():
    """List all embedding JSON files"""
    files = []
    for filename in os.listdir(EMBEDDINGS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(EMBEDDINGS_DIR, filename)
            stat = os.stat(filepath)

            # Load metadata
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
            except:
                metadata = {}

            files.append({
                "filename": filename,
                "path": filepath,
                "size_mb": stat.st_size / (1024 * 1024),
                "created_at": metadata.get('created_at', ''),
                "source_file": metadata.get('source_file', ''),
                "num_embeddings": metadata.get('num_embeddings', 0),
                "custom_name": metadata.get('custom_name', filename.replace('.json', ''))
            })

    # Sort by creation time (newest first)
    files.sort(key=lambda x: x['created_at'], reverse=True)
    return files


def rename_embedding_file(old_filename, new_name):
    """Rename an embedding file"""
    old_path = os.path.join(EMBEDDINGS_DIR, old_filename)

    if not os.path.exists(old_path):
        raise FileNotFoundError(f"File {old_filename} not found")

    # Create new filename
    new_filename = f"{new_name}.json"
    new_path = os.path.join(EMBEDDINGS_DIR, new_filename)

    if os.path.exists(new_path):
        raise FileExistsError(f"File {new_filename} already exists")

    # Load and update metadata
    with open(old_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data['metadata']['custom_name'] = new_name
    data['metadata']['renamed_at'] = datetime.now().isoformat()

    # Save with new name
    with open(new_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Remove old file
    os.remove(old_path)

    return {
        "old_filename": old_filename,
        "new_filename": new_filename,
        "new_path": new_path
    }


def delete_embedding_file(filename):
    """Delete an embedding file"""
    filepath = os.path.join(EMBEDDINGS_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filename} not found")

    os.remove(filepath)

    return {
        "filename": filename,
        "deleted": True
    }


def get_embedding_file_info(filename):
    """Get detailed information about an embedding file"""
    filepath = os.path.join(EMBEDDINGS_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filename} not found")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stat = os.stat(filepath)

    return {
        "filename": filename,
        "path": filepath,
        "size_mb": stat.st_size / (1024 * 1024),
        "metadata": data.get('metadata', {}),
        "num_texts": len(data.get('texts', [])),
        "num_embeddings": len(data.get('embeddings', []))
    }