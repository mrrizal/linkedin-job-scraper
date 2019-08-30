from dotenv import load_dotenv
import os

load_dotenv()

MONGO_HOST = os.getenv('MONGO_HOST', None)
MONGO_PORT = os.getenv('MONGO_PORT', None)
