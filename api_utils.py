import time
import json
from functools import wraps
import google.generativeai as genai
from config import GEMINI_API_KEY, MIN_DELAY_BETWEEN_REQUESTS, MAX_RETRIES, RETRY_DELAY

genai.configure(api_key=GEMINI_API_KEY)

def retry_with_backoff(max_retries=MAX_RETRIES, initial_delay=RETRY_DELAY):
    """
    Decorator that retries the wrapped function with exponential backoff 
    when exceptions occur
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    # Rate limit to prevent hitting quota
                    if attempt > 0:
                        print(f"Retry attempt {attempt}/{max_retries} after {delay}s delay...")
                    time.sleep(MIN_DELAY_BETWEEN_REQUESTS)
                    
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries:
                        # Rate limit error, wait longer
                        print(f"Rate limit hit: {str(e)}")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        if attempt == max_retries:
                            print(f"Max retries reached. Last error: {str(e)}")
                        raise e
        return wrapper
    return decorator

@retry_with_backoff()
def generate_content(model_name, prompt, system_instruction="", temperature=0.7):
    """
    Generate content using Gemini API with retry logic
    """
    model = genai.GenerativeModel(model_name, 
                                 generation_config={"temperature": temperature})
    
    complete_prompt = system_instruction + "\n\n" + prompt if system_instruction else prompt
    
    response = model.generate_content([
        {"role": "user", "parts": [complete_prompt]}
    ])
    
    return response.text

def parse_json_response(text):
    """
    Parse JSON from response text or return formatted error
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": text}
