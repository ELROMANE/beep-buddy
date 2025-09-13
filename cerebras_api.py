# the brain 

import requests
import os

API_KEY = os.getenv("API_KEY")
API_URL = "https://api.cerebras.ai/v2/chat/completions"


def ask_prompt (prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "Llama 4 Scout",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if (response.status_code != 200):
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
    return response.json()['choices'][0]['message']['content']


