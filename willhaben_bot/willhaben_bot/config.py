import os
from dotenv import load_dotenv

load_dotenv()

WILLHABEN_EMAIL = os.getenv("WILLHABEN_EMAIL")
WILLHABEN_PASSWORD = os.getenv("WILLHABEN_PASSWORD")
