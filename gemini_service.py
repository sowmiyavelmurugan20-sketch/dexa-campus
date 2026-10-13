"""
DEXA Gemini AI Service - Official Google Gen AI Python SDK Integration
Handles secure client initialization, multi-turn conversational chat, and analytics grounding.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from analytics_context import build_gemini_system_prompt, lookup_student_context

logger = logging.getLogger("dexa.gemini")

# Official Google GenAI SDK
GOOGLE_GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    pass

# Legacy SDK Fallback (only if official google-genai is missing)
LEGACY_GENAI_AVAILABLE = False
if not GOOGLE_GENAI_AVAILABLE:
    try:
        import google.generativeai as legacy_genai
        LEGACY_GENAI_AVAILABLE = True
    except ImportError:
        pass


DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest"
]


def get_api_key() -> Optional[str]:
    """Retrieve GEMINI_API_KEY from environment variables securely."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        key = os.environ.get("GOOGLE_API_KEY", "").strip()
    return key if key else None


def is_gemini_configured() -> bool:
    """Check if a non-empty GEMINI_API_KEY is available."""
    return get_api_key() is not None


def get_ai_service_status() -> Dict[str, Any]:
    """Return health & configuration status of the Gemini service."""
    configured = is_gemini_configured()
    sdk_name = "google-genai (v2.x)" if GOOGLE_GENAI_AVAILABLE else ("google-generativeai" if LEGACY_GENAI_AVAILABLE else "None")
    return {
        "configured": configured,
        "sdk": sdk_name,
        "preferred_model": DEFAULT_MODEL,
        "fallback_models": FALLBACK_MODELS,
        "fallback_model": FALLBACK_MODELS[0] if FALLBACK_MODELS else "None",
        "api_key_set": configured,
        "status_message": (
            f"Active ({DEFAULT_MODEL} via {sdk_name})"
            if configured
            else "GEMINI_API_KEY not set. Real-time GenAI requests pending environment key."
        )
    }


def format_missing_key_guidance() -> str:
    """Return clear, actionable instructions for setting GEMINI_API_KEY on Windows."""
    return (
        "⚠️ **Gemini API Key Required**\n\n"
        "To enable real-time, dynamic GenAI conversations with **DEXA Copilot**, configure your `GEMINI_API_KEY`:\n\n"
        "**Windows PowerShell:**\n"
        "```powershell\n"
        "$env:GEMINI_API_KEY=\"your_gemini_api_key_here\"\n"
        "```\n\n"
        "**Windows Command Prompt (CMD):**\n"
        "```cmd\n"
        "set GEMINI_API_KEY=your_gemini_api_key_here\n"
        "```\n\n"
        "**Or create a `.env` file in the project root:**\n"
        "```ini\n"
        "GEMINI_API_KEY=your_gemini_api_key_here\n"
        "```\n\n"
        "💡 *You can obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).*"
    )


def extract_student_id_from_text(text: str) -> Optional[str]:
    """Check for student ID patterns like STU0001 or 24CS001 in user queries."""
    m = re.search(r'\b(STU\d{4}|2[2-4]CS\d{3})\b', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return None


def chat_with_gemini(
    message: str,
    history: List[Dict[str, str]],
    df_students: pd.DataFrame,
    df_staff: pd.DataFrame,
    user_role: str = "HOD / Admin",
    user_id: str = "admin",
    mode: str = "vibe"
) -> Dict[str, Any]:
    """
    Send user query and conversation history to Gemini using the official Google GenAI SDK.
    Integrates verified DEXA institutional analytics context.
    """
    api_key = get_api_key()
    if not api_key:
        return {
            "role": "assistant",
            "content": format_missing_key_guidance(),
            "configured": False,
            "model_used": None,
            "error": "MISSING_GEMINI_API_KEY"
        }

    # 1. Detect if a specific student is referenced
    student_id = extract_student_id_from_text(message)
    specific_student = None
    if student_id:
        specific_student = lookup_student_context(student_id, df_students)

    # 2. Build grounded institutional system prompt
    system_instruction = build_gemini_system_prompt(
        df_students=df_students,
        df_staff=df_staff,
        user_role=user_role,
        user_id=user_id,
        specific_student=specific_student
    )

    # 3. Call Gemini using official google.genai SDK
    if GOOGLE_GENAI_AVAILABLE:
        try:
            client = genai.Client(api_key=api_key)

            # Build multi-turn content items
            contents = []
            # Append prior session turns (limited to last 8 turns for token efficiency)
            recent_history = history[-8:] if len(history) > 8 else history
            for turn in recent_history:
                role = "user" if turn.get("role") == "user" else "model"
                content_text = turn.get("content", "").strip()
                if content_text:
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=content_text)]
                        )
                    )

            # Add current user message
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=message.strip())]
                )
            )

            # Try primary model and cascade through fallback candidates
            models_to_try = [DEFAULT_MODEL]
            for fb in FALLBACK_MODELS:
                if fb not in models_to_try:
                    models_to_try.append(fb)

            response = None
            last_err = None
            selected_model = DEFAULT_MODEL

            for model_name in models_to_try:
                try:
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                        max_output_tokens=1024
                    )
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config
                    )
                    selected_model = model_name
                    break
                except Exception as m_err:
                    last_err = m_err
                    logger.warning(f"Gemini model '{model_name}' failed: {m_err}. Trying next candidate...")
                    continue

            if response is None:
                raise last_err or RuntimeError("All candidate Gemini models failed to generate content.")

            reply_text = response.text or "I processed your request, but the model generated an empty response."
            return {
                "role": "assistant",
                "content": reply_text,
                "configured": True,
                "model_used": selected_model,
                "error": None
            }

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Gemini API Execution Error: {err_msg}")

            # Helpful user-facing error diagnosis without exposing keys
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg or "quota" in err_msg.lower():
                user_friendly = (
                    "⏳ **Gemini Rate Limit Reached (HTTP 429)**\n\n"
                    "The current API key has temporarily exceeded its per-minute quota or rate limit. "
                    "Please wait a few moments and try your question again."
                )
            elif "API_KEY_INVALID" in err_msg or "API key not valid" in err_msg or "401" in err_msg or "403" in err_msg:
                user_friendly = (
                    "🔒 **Invalid Gemini API Key**\n\n"
                    "The provided `GEMINI_API_KEY` was rejected by Google AI services. "
                    "Please verify your key in Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)."
                )
            elif "NOT_FOUND" in err_msg or "404" in err_msg or "no longer available" in err_msg:
                user_friendly = (
                    "🔍 **Gemini Model Unavailable (HTTP 404)**\n\n"
                    "The requested Gemini model version is not available on this API tier or has been retired. "
                    f"Details: {err_msg}"
                )
            elif "DEADLINE_EXCEEDED" in err_msg or "timeout" in err_msg.lower():
                user_friendly = (
                    "⏱️ **Gemini Request Timeout**\n\n"
                    "The request to Google Gemini timed out. Please check your network connection and click Retry."
                )
            else:
                user_friendly = f"⚠️ **Gemini Service Notice**: {err_msg}"

            return {
                "role": "assistant",
                "content": user_friendly,
                "configured": True,
                "model_used": None,
                "error": err_msg
            }

    # 4. Fallback to legacy google.generativeai if google-genai is missing
    elif LEGACY_GENAI_AVAILABLE:
        try:
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            chat = model.start_chat(history=[])
            resp = chat.send_message(message)
            return {
                "role": "assistant",
                "content": resp.text,
                "configured": True,
                "model_used": "gemini-1.5-flash (legacy SDK)",
                "error": None
            }
        except Exception as leg_err:
            return {
                "role": "assistant",
                "content": f"⚠️ **Gemini API Error (Legacy SDK)**: {str(leg_err)}",
                "configured": True,
                "model_used": None,
                "error": str(leg_err)
            }

    return {
        "role": "assistant",
        "content": "⚠️ Google Gen AI SDK is not installed in the environment. Please run: `pip install google-genai`",
        "configured": False,
        "model_used": None,
        "error": "SDK_NOT_INSTALLED"
    }
