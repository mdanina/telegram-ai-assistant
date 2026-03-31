#!/usr/bin/env python3
"""
AIOS Common: Shared utilities for all execution modules.

Centralizes:
  - LLM model constants (env-var backed, single place to change)
  - OpenAI client singleton (one connection for the whole bot process)
  - GPT call with automatic retry on transient errors
"""

import os
import re
import time
import logging

from openai import (
    OpenAI,
    APIError,
    RateLimitError,
    AuthenticationError,
    BadRequestError,
    APITimeoutError,
    APIConnectionError,
)

logger = logging.getLogger(__name__)

# ── Model constants ──────────────────────────────────────────────────────
# Override via .env if OpenAI releases new models.
MODEL_MAIN = os.getenv("AIOS_MODEL_MAIN", "gpt-5.4")       # Chat, tasks, queries
MODEL_FAST = os.getenv("AIOS_MODEL_FAST", "gpt-4o-mini")    # Memory extraction, cheap ops
MODEL_ANALYSIS = os.getenv("AIOS_MODEL_ANALYSIS", "gpt-4o") # Vision, background analysis

# ── OpenAI client singleton ─────────────────────────────────────────────
_openai_client = None


def get_openai_client() -> OpenAI:
    """Returns a shared OpenAI client instance (created once per process)."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("OpenAI client initialized (singleton)")
    return _openai_client


# ── Groq fallback client ──────────────────────────────────────────────
_groq_client = None
GROQ_MODEL = os.getenv("AIOS_GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_groq_client():
    """Returns Groq client (OpenAI-compatible). None if no key."""
    global _groq_client
    if _groq_client is None:
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            return None
        _groq_client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
        )
        logger.info("Groq fallback client initialized")
    return _groq_client


# ── API key masking ──────────────────────────────────────────────────────
_KEY_RE = re.compile(r"(sk-[a-zA-Z0-9]{2})[a-zA-Z0-9_-]{20,}([a-zA-Z0-9]{4})")


def _mask_keys(text: str) -> str:
    """Replace API keys in error messages with masked versions."""
    return _KEY_RE.sub(r"\1****\2", text)


# ── Error classification ────────────────────────────────────────────────

# Errors where retry makes sense (server-side / transient)
_RETRYABLE = (RateLimitError, APITimeoutError, APIConnectionError)

# Errors where retry is pointless (client-side / permanent)
_PERMANENT = (AuthenticationError, BadRequestError)


def call_gpt(messages, tools=None, model=None, max_tokens=2048, retries=3):
    """Calls GPT with automatic retry on transient errors.

    Retry strategy:
      - RateLimitError (429): exponential backoff with longer base (3s)
      - APITimeoutError, APIConnectionError: standard backoff (2s)
      - AuthenticationError, BadRequestError: fail immediately (no retry)
      - Unknown APIError: retry if status is 5xx, fail otherwise

    API keys are masked in all log messages.

    Args:
        messages: Chat messages list.
        tools: Optional function-calling tools.
        model: Model name (defaults to MODEL_MAIN).
        max_tokens: Max completion tokens.
        retries: Number of retry attempts.

    Returns:
        The response message object.

    Raises:
        The last exception if all retries fail.
    """
    client = get_openai_client()
    model = model or MODEL_MAIN

    last_error = None
    for attempt in range(retries):
        try:
            kwargs = {
                "model": model,
                "max_completion_tokens": max_tokens,
                "messages": messages,
                "timeout": 30,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message

        except _PERMANENT as e:
            # Auth / bad request — no point retrying
            logger.error("GPT permanent error (%s): %s", type(e).__name__, _mask_keys(str(e)))
            raise

        except RateLimitError as e:
            last_error = e
            # Longer backoff for rate limits
            wait = 3 * (2 ** attempt)  # 3, 6, 12 seconds
            logger.warning(
                "GPT rate-limited (attempt %d/%d), retrying in %ds...",
                attempt + 1, retries, wait,
            )
            time.sleep(wait)
            continue

        except _RETRYABLE as e:
            last_error = e
            wait = 2 ** attempt  # 1, 2, 4 seconds
            logger.warning(
                "GPT transient error (attempt %d/%d, %s): %s — retrying in %ds...",
                attempt + 1, retries, type(e).__name__,
                _mask_keys(str(e)[:120]), wait,
            )
            time.sleep(wait)
            continue

        except APIError as e:
            last_error = e
            # 5xx = server error, retry; 4xx = client error, fail
            if hasattr(e, "status_code") and e.status_code and e.status_code < 500:
                logger.error("GPT API error %d: %s", e.status_code, _mask_keys(str(e)))
                raise
            wait = 2 ** attempt
            logger.warning(
                "GPT server error (attempt %d/%d, status=%s): %s — retrying in %ds...",
                attempt + 1, retries, getattr(e, "status_code", "?"),
                _mask_keys(str(e)[:120]), wait,
            )
            time.sleep(wait)
            continue

        except Exception as e:
            # Completely unexpected — log masked and raise
            logger.error("GPT unexpected error: %s", _mask_keys(str(e)))
            raise

    # ── Fallback to Groq if OpenAI exhausted all retries ──
    groq = _get_groq_client()
    if groq:
        logger.warning("OpenAI failed after %d retries. Falling back to Groq (%s)...", retries, GROQ_MODEL)
        try:
            kwargs = {
                "model": GROQ_MODEL,
                "max_tokens": max_tokens,
                "messages": messages,
                "timeout": 30,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            response = groq.chat.completions.create(**kwargs)
            logger.info("Groq fallback succeeded.")
            return response.choices[0].message
        except Exception as groq_err:
            logger.error("Groq fallback also failed: %s", _mask_keys(str(groq_err)))

    if last_error:
        raise last_error
    raise RuntimeError("LLM call failed: no recorded error from OpenAI or Groq")
