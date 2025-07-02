from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API keys from environment
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
use_groq = os.getenv("USE_GROQ", "false").lower() == "true"

# Validate API keys
if not openrouter_api_key and not groq_api_key:
    logger.error("Neither OPENROUTER_API_KEY nor GROQ_API_KEY environment variables are set")
    raise ValueError("Please set either OPENROUTER_API_KEY or GROQ_API_KEY environment variable")
elif not openrouter_api_key:
    logger.warning("OPENROUTER_API_KEY not set, defaulting to Groq if enabled")
elif not groq_api_key and use_groq:
    logger.error("GROQ_API_KEY is required when USE_GROQ is enabled")
    raise ValueError("Please set the GROQ_API_KEY environment variable when using Groq")

# LLM Configuration
if use_groq and groq_api_key:
    llm = ChatGroq(
        api_key=groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.7,
    )
    logger.info("Using Groq LLM")
else:
    llm = ChatOpenAI(
        api_key=openrouter_api_key,
        model="openrouter/anthropic/claude-3.5-sonnet",
        base_url="https://openrouter.ai/api/v1",
        extra_headers={
            "HTTP-Referer": os.getenv("YOUR_SITE_URL", "http://localhost"),
            "X-Title": os.getenv("YOUR_SITE_NAME", "Dynamic Pricing Agent"),
        },
        temperature=0.7,
    )
    logger.info("Using OpenRouter LLM with Claude 3.5 Sonnet")