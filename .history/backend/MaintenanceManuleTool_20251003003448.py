from retrivals import load_embeddings_from_file, search_query_in_embeddings         
from fastapi import FastAPI, HTTPException, UploadFile, File
import boto3

# AWS Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'
)
class MaintenanceManuleTool:

    @staticmethod
    def get_tool_spec():
        return {
            "toolSpec": {
                "name": "Maintenance_Manule_Tool",
                "description": "Provides maintenance advice and breakdown predictions based on machine sensor data. Helps diagnose machine issues, provide repair steps, and suggest necessary tools and safety precautions.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query_text": {
                                "type": "string",
                                "description": "User's question regarding maintenance or breakdown advice."
                            }
                        },
                        "required": ["query_text"]  # Ensure the user provides a question
                    }
                }
            }
        }
    
    @staticmethod
    def maintenance_manules(input_data):
        try: 
            # Load embeddings from file
            embeddings_file_path  = "/embeddings.json"
            embeddings = load_embeddings_from_file(embeddings_file_path)
            
            # Open and read the manual file
            with open("manuls.txt", "r", encoding="utf-8") as file:
                text_fitz = file.read()  # อ่านเนื้อหาทั้งหมดในไฟล์

            # Split the text by new lines (or paragraphs)
            texts_strip = text_fitz.split("\n")

            # Filter out empty lines
            texts = [text for text in texts_strip if text.strip()]

            # Get query text from input data (message from the user)
            query_text = input_data.get('query_text', "")  # Assuming input_data contains 'query_text'

            if not query_text:
                raise HTTPException(status_code=400, detail="query_text is required")

            # Search the query text in the embeddings and retrieve results
            results = search_query_in_embeddings(query_text, embeddings, texts)

            # Construct the prompt for the model
            prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านการซ่อมบำรุงเครื่องจักรโรงงานน้ำตาล โดยเฉพาะระบบ Feed Mill

คำถาม: {query_text}
โดยใช้เนื้อหาจาก: {results}

กรุณาตอบคำถามเกี่ยวกับการซ่อมบำรุงอย่างละเอียด รวมถึง:
1. ขั้นตอนการซ่อม
2. อุปกรณ์ที่ต้องใช้
3. ข้อควรระวัง
4. เวลาที่ใช้โดยประมาณ"""

            # Send the request to the model via Bedrock API
            response_body = bedrock_runtime.converse(
                modelId="qwen.qwen3-32b-v1:0",
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 1024
                }
            )
            # Get the manual content from the response
            manual_content = response_body['output']['message']['content'][0]['text']

            return {
                "manual_content": manual_content,
                "query": query_text,
                "results_from_embeddings": results
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

