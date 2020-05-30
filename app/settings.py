
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path('.') / 'environment'
load_dotenv(dotenv_path=env_path,verbose=True)


BASE_URL=os.getenv("BASE_URL")
CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
OAUTH_REDIRECT_URL=os.getenv("OAUTH_REDIRECT_URL")
WEBHOOK_SECRET=os.getenv("WEBHOOK_SECRET")
SLACK_BOT_ACCESS_TOKEN=os.getenv("SLACK_BOT_ACCESS_TOKEN")
DATABASE=os.getenv("DATABASE")
DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL: ",DATABASE_URL)