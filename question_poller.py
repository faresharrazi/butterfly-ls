# question_poller.py

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN   = os.getenv('LIVESTORM_API_TOKEN')
SESSION_ID  = os.getenv('LIVESTORM_SESSION_ID')
URL = (
    f"https://api.livestorm.co/v1/sessions/{SESSION_ID}"
    "/questions?include=asker&include=responder"
)
HEADERS = {
    "accept": "application/vnd.api+json",
    "Authorization": API_TOKEN
}

def poll_questions(on_new_question, interval=6):
    """
    Polls the Livestorm questions endpoint every `interval` seconds.
    Calls on_new_question(question_id, question_text) for each fresh question.
    """
    seen = set()
    while True:
        resp = requests.get(URL, headers=HEADERS)
        resp.raise_for_status()
        for item in resp.json().get('data', []):
            qid  = item['id']
            text = item['attributes']['question']
            if qid not in seen:
                seen.add(qid)
                on_new_question(qid, text)
        time.sleep(interval)
