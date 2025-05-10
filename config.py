import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Use gemini-1.5-flash which has better performance in the free tier
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
EVAL_MODEL_NAME = os.getenv("EVAL_MODEL_NAME", "gemini-1.5-flash")

# System Parameters
MAX_TOKENS = 2048  # Reduced to lower token usage
TEMPERATURE = 0.7
EVAL_TEMPERATURE = 0.5

# Rate Limiting Settings
MIN_DELAY_BETWEEN_REQUESTS = 3  # seconds between API calls
MAX_RETRIES = 3
RETRY_DELAY = 5  # initial seconds to wait before retry (will increase exponentially)

# Path configurations
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def rate_limit():
    """Simple function to enforce delay between API calls"""
    time.sleep(MIN_DELAY_BETWEEN_REQUESTS)
