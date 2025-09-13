# the brain 

import requests
import os

API_KEY = os.getenv("API_KEY")
API_URL = "https://api.cerebras.ai/v2/chat/completions"
print(API_URL)