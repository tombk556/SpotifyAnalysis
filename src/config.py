import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        
        
settings = Settings()