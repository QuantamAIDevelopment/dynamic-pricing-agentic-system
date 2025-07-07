from langchain_groq import ChatGroq
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

groq_api_key = os.getenv("GROQ_API_KEY")


if not groq_api_key:
    logger.error("GROQ_API_KEY environment variable is not set.")
    raise ValueError("GROQ_API_KEY is required for Groq integration.")


llm = None
if groq_api_key:
    llm = ChatGroq(
        model="llama3-70b-8192",
        api_key=groq_api_key,
        base_url="https://api.groq.com",
        temperature=0.7
    )
    logger.info("Using Groq LLM with llama3-70b-8192 model and base_url=https://api.groq.com")
