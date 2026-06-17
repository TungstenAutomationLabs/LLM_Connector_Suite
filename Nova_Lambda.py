import json
import boto3
import time
import base64
from botocore.exceptions import ClientError

MIME_TO_BEDROCK_FORMAT = {
    "application/pdf":                                                           "pdf",
    "application/msword":                                                        "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":  "docx",
    "application/vnd.ms-excel":                                                  "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":        "xlsx",
    "text/csv":                                                                  "csv",
    "text/html":                                                                 "html",
    "text/plain":                                                                "txt",
    "text/markdown":                                                             "md"
}

IMAGE_MIME_TO_FORMAT = {
    "image/jpeg": "jpeg",
    "image/jpg":  "jpeg",
    "image/png":  "png",
    "image/gif":  "gif",
    "image/webp": "webp"
}

def get_bedrock_format(mime_or_format):
    return MIME_TO_BEDROCK_FORMAT.get(mime_or_format, mime_or_format)

def get_image_format(mime_or_format):
    return IMAGE_MIME_TO_FORMAT.get(mime_or_format, mime_or_format)

def detect_format_from_base64(b64_string):
    if b64_string.startswith("JVBERi"):  return "pdf",  False  # PDF
    if b64_string.startswith("/9j/"):    return "jpeg", True   # JPEG
    if b64_string.startswith("iVBORw"): return "png",  True   # PNG
    if b64_string.startswith("R0lGOD"): return "gif",  True   # GIF
    if b64_string.startswith("UklGRi"): return "webp", True   # WebP
    return "pdf", False                                         # default fallback

# NEW: Build content block for any file — doc or image, auto-detected
def build_file_block(b64_string):
    fmt, is_image = detect_format_from_base64(b64_string)
    if is_image:
        return {
            "image": {
                "format": fmt,
                "source": {"bytes": base64.b64decode(b64_string)}
            }
        }
    else:
        return {
            "document": {
                "format": fmt,
                "name":   "document",
                "source": {"bytes": base64.b64decode(b64_string)}
            }
        }

def lambda_handler(event, context):   
    
    # Parse body
    if "body" in event and event["body"]:
        try:
            body = json.loads(event["body"])
        except:
            body = event
    else:
        body = event
   
    model_id    = body.get("modelId", "eu.amazon.nova-lite-v1:0")
    question    = body.get("question", "")
    options     = body.get("options", None)
    system_text = body.get("systemPrompt", "You are a helpful assistant.")
    max_tokens  = body.get("maxTokens", 500)
    temperature = body.get("temperature", 0)

    # Read document fields (only present when caller sends a document)
    doc_base64  = body.get("docBase64", None)
    doc_format  = body.get("docFormat", "pdf")
    doc_name    = body.get("docName", "uploaded-document")

    # Read image fields (only present when caller sends an image)
    image_base64 = body.get("imageBase64", None)
    image_format = body.get("imageFormat", "jpeg")

    if not question:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "question is empty"})
        }

    client = boto3.client(
        service_name="bedrock-runtime",
        region_name="eu-west-1"
    )

    if options:
    # MCQ mode
        options_text = "\n".join(options) if isinstance(options, list) else options
        full_question = f"{question}\n\nOptions:\n{options_text}"
    
    else:
    # Open QnA mode
        full_question = question

    # Combo: document block + image block + question text
    content = []

    # Add document block if docBase64 was provided
    if doc_base64:
    # Check if the file is an image or a document based on MIME type
        is_image = doc_format in IMAGE_MIME_TO_FORMAT or doc_format in ["jpeg", "png", "gif", "webp"]

        if is_image:
            # Single image upload → image block
            content.append({
                "image": {
                    "format": get_image_format(doc_format),
                    "source": {"bytes": base64.b64decode(doc_base64)}
                }
            })
        else:
            # Document upload (PDF, CSV etc.) → document block
            content.append({
                "document": {
                    "format": get_bedrock_format(doc_format),
                    "name":   "document",
                    "source": {"bytes": base64.b64decode(doc_base64)}
                }
            })

    # Add image block if imageBase64 was provided
    if image_base64:
        content.append({
            "image": {
                "format": get_image_format(image_format),
                "source": {
                    # Bedrock expects raw bytes, not base64 string — decode 
                    "bytes": base64.b64decode(image_base64)
                }
            }
        })
  
    content.append({"text": full_question})

    messages = [
        {
            "role": "user",
            "content": content
        }
    ]

    system = [{"text": system_text}]

    inference_config = {
        "maxTokens": max_tokens,
        "temperature": temperature
    }

    try:
        start_time = time.time()

        response = client.converse(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig=inference_config
        )

        end_time = time.time() 
        latency_s = round(end_time - start_time, 2)

        raw_answer    = response["output"]["message"]["content"][0]["text"]
        input_tokens  = response["usage"]["inputTokens"]
        output_tokens = response["usage"]["outputTokens"]
        total_tokens  = response["usage"]["totalTokens"]
        stop_reason   = response["stopReason"]

        # Split reasoning and answer into separate fields
        # Split reasoning and answer into separate fields
        reasoning = ""
        answer = raw_answer

        if "Answer:" in raw_answer and "Reasoning:" in raw_answer:
            # Answer first then Reasoning
            parts = raw_answer.split("Reasoning:")
            answer = parts[0].replace("Answer:", "").strip()
            reasoning = parts[1].strip()

        elif "Answer:" in raw_answer and "Reasoning:" not in raw_answer:
            answer = raw_answer.replace("Answer:", "").strip()
            reasoning = ""

        elif "Reasoning:" in raw_answer and "Answer:" not in raw_answer:
            reasoning = raw_answer.replace("Reasoning:", "").strip()
            answer = ""

        else:
            answer = raw_answer.strip()
            reasoning = ""
        if doc_base64 and image_base64:
            input_mode = "Combo"
        elif doc_base64 and is_image:
            input_mode = "Image"   # ← was wrongly showing "Doc" before
        elif doc_base64:
            input_mode = "Doc"
        elif image_base64:
            input_mode = "Image"
        else:
            input_mode = "MCQ" if options else "QnA"

        return {
            "statusCode": 200,
            "body": json.dumps({
                "modelId":      model_id,
                "question":     question,
                "options":      options,
                "mode":         input_mode,
                "answer":       answer,
                "reasoning":    reasoning,
                "inputTokens":  input_tokens,
                "outputTokens": output_tokens,
                "totalTokens":  total_tokens,
                "stopReason":   stop_reason,
                "latencyS":     latency_s
            })
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
