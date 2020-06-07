
import os
from pathlib import Path
from dotenv import load_dotenv

print("env: ", os.getenv('ENV_FILE'))

ENV_PATH = Path('.') / os.getenv('ENV_FILE', 'environment')
load_dotenv(dotenv_path=ENV_PATH, verbose=True)


BASE_URL = os.getenv("BASE_URL")
CLIENT_ID = 'asdf'
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OAUTH_REDIRECT_URL = os.getenv("OAUTH_REDIRECT_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
SLACK_BOT_ACCESS_TOKEN = os.getenv("SLACK_BOT_ACCESS_TOKEN")
DATABASE = os.getenv("DATABASE")
DATABASE_URL = os.getenv("DATABASE_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN")
BAN_USERS = ['codecov', 'dependabot']
