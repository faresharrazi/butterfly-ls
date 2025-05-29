import sys
import os
from dotenv import load_dotenv 
from answer_engine import answer_question
from question_poller import poll_questions

def handle(qid, question, pdf_path):
    print(f"\n New question: {question}")
    print("butterfly thinking ...")
    try:
        answer = answer_question(pdf_path, question)
        print(f"🦋 Suggestion: {answer}")
    except Exception as e:
        print(f"❗ Error: {e}")

def main(pdf_path):
    load_dotenv()
    poll_questions(
        on_new_question=lambda qid, text: handle(qid, text, pdf_path)
    )

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python butterfly.py <path_to_pdf>")
        sys.exit(1)
    main(sys.argv[1])
