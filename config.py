import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables read from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VIAM_API_KEY = os.getenv('VIAM_API_KEY')
VIAM_API_KEY_ID = os.getenv('VIAM_API_KEY_ID')
ROBOT_ADDR = os.getenv('ROBOT_ADDR')
