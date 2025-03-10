import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PayPal Settings - Always using sandbox mode as required
PAYPAL_CONFIG = {
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET"),
    "mode": "sandbox",  # Always use sandbox per requirements
    "base_url": "https://api-m.sandbox.paypal.com"
}

# LLM Settings
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),  # Using gpt-4o-mini model
}

# Logging Settings
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "DEBUG"),  # Default to DEBUG level
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# System Prompts
PROMPTS = {
    "paypal_sandbox": {
        "role": "system",
        "content": "You are a PayPal assistant that only uses PayPal REST API in sandbox mode. "
                   "Only offer services available through PayPal's REST API and always operate in sandbox mode. "
                   "Never attempt to make real transactions."
    }
}
