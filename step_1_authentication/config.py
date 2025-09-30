# config.py
import os

API_URL = "https://stageapi.glovoapp.com/oauth/token"
API_KEY = os.getenv("API_KEY", "your_api_key_here")
API_SECRET = os.getenv("API_SECRET", "your_api_secret_here")
Access_Token = []