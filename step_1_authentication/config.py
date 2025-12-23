# config.py
import os

from dotenv import load_dotenv

load_dotenv()

API_URL = "https://stageapi.glovoapp.com/oauth/token"
API_KEY = os.getenv("API_KEY", "default_your_api_key_here")
API_SECRET = os.getenv("API_SECRET", "default_your_api_secret_here")
Access_Token = []