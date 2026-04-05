import os
import sys

from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = ["MODEL", "BASE_URL", "API_KEY"]
_missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
if _missing:
    print(f"Missing required environment variables: {', '.join(_missing)}")
    sys.exit(1)

MODEL = os.getenv("MODEL")
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
