# answer_engine.py
# Handles uploading PDFs, retrieving signed URLs, and answering questions via Mistral API.

import os
from typing import Dict
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables once at import
default_env = load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise RuntimeError("MISTRAL_API_KEY not set in environment")

# Initialize a single Mistral client
client = Mistral(api_key=api_key)

# Cache to avoid re-uploading the same document repeatedly
doc_url_cache: Dict[str, str] = {}


def answer_question(pdf_path: str, question: str) -> str:
    """
    Uploads a PDF for OCR (if not already uploaded),
    and asks a question via Mistral API using the signed document URL.
    Returns the answer text.
    """
    # Upload once per PDF and cache the signed URL
    if pdf_path not in doc_url_cache:
        try:
            with open(pdf_path, "rb") as f:
                uploaded = client.files.upload(
                    file={"file_name": os.path.basename(pdf_path), "content": f},
                    purpose="ocr"
                )
            signed = client.files.get_signed_url(file_id=uploaded.id)
            doc_url_cache[pdf_path] = signed.url
        except Exception as upload_err:
            raise RuntimeError(f"Failed to upload document '{pdf_path}': {upload_err}")

    doc_url = doc_url_cache[pdf_path]

    # Prepare the chat messages
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "document_url", "document_url": doc_url},
                {"type": "text", "text": question}
            ]
        }
    ]

    try:
        resp = client.chat.complete(model="mistral-small-latest", messages=messages)
        return resp.choices[0].message.content
    except Exception as chat_err:
        raise RuntimeError(f"Chat completion failed: {chat_err}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python answer_engine.py <path_to_pdf> '<question>'")
        sys.exit(1)

    pdf_path, question = sys.argv[1], sys.argv[2]
    try:
        answer = answer_question(pdf_path, question)
        print("Answer:", answer)
    except Exception as e:
        print(f"Error: {e}")

# Requirements:
# pip install mistralai python-dotenv
# Store MISTRAL_API_KEY in your .env
# Then run:
# python answer_engine.py knowledge.pdf "Your question here"