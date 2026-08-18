import os
import logging

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_text(text: str) -> str:
    """Uses Gemini API to rewrite the text into a one-paragraph summary.
    Falls back to truncated text on failure."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Falling back to truncated text.")
        return _fallback_summarize(text)
    
    if not HAS_GENAI:
        logger.warning("google-genai package not installed. Falling back to truncated text.")
        return _fallback_summarize(text)
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"Rewrite the following abstract/post into a clear, original, single-paragraph summary for a personal ML/AI research digest:\n\n{text}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        if response.text:
            return response.text.strip()
        else:
            return _fallback_summarize(text)
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}. Falling back to truncated text.")
        return _fallback_summarize(text)

def _fallback_summarize(text: str, max_length: int = 500) -> str:
    cleaned = text.replace('\n', ' ').strip()
    if len(cleaned) <= max_length:
        return f"{cleaned}\n\n*(Unedited)*"
    return f"{cleaned[:max_length]}...\n\n*(Unedited)*"
