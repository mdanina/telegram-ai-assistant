#!/usr/bin/env python3
"""
Telegram Bot: Yandex Mail Handler (IMAP/SMTP)

Provides email functionality via Yandex Mail:
- Check inbox (unread summary)
- Read specific email (with metadata for follow-up actions)
- Reply to email
- Mark email as read
- AI-summarize long emails (GPT-5)
- Send email

Uses IMAP for reading and SMTP for sending.
App password stored in .env (YANDEX_APP_PASSWORD).
"""

import os
import sys
import re
import ssl
import email
import imaplib
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import get_openai_client, MODEL_MAIN

logger = logging.getLogger(__name__)

YANDEX_EMAIL = os.getenv("YANDEX_EMAIL", "")
YANDEX_APP_PASSWORD = os.getenv("YANDEX_APP_PASSWORD", "")
IMAP_SERVER = "imap.yandex.ru"
IMAP_PORT = 993
SMTP_SERVER = "smtp.yandex.ru"
SMTP_PORT = 465


def _decode_header_value(raw):
    """Decodes an email header (Subject, From) into a readable string."""
    if not raw:
        return ""
    parts = decode_header(raw)
    decoded = []
    for data, charset in parts:
        if isinstance(data, bytes):
            decoded.append(data.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(str(data))
    return " ".join(decoded).strip()


def _extract_email_address(from_header: str) -> str:
    """Extracts just the email address from a From header."""
    match = re.search(r"<(.+?)>", from_header)
    return match.group(1) if match else from_header


def _extract_name(from_header: str) -> str:
    """Extracts the display name from a From header."""
    decoded = _decode_header_value(from_header)
    match = re.match(r"(.+?)\s*<", decoded)
    if match:
        name = match.group(1).strip().strip('"')
        return name if name else _extract_email_address(decoded)
    return decoded


def _get_text_body(msg) -> str:
    """Extracts the plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
        # Fallback: try HTML
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                html = payload.decode(charset, errors="replace")
                # Strip HTML tags for plain text
                text = re.sub(r"<[^>]+>", "", html)
                return text.strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def _connect_imap():
    """Opens an IMAP connection to Yandex Mail (with 30s timeout)."""
    if not YANDEX_EMAIL or not YANDEX_APP_PASSWORD:
        raise ValueError("YANDEX_EMAIL or YANDEX_APP_PASSWORD not set in .env")
    conn = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=30)
    conn.login(YANDEX_EMAIL, YANDEX_APP_PASSWORD)
    return conn


# ── Public API ────────────────────────────────────────────────────────


def check_inbox(count: int = 10, unread_only: bool = True) -> str:
    """Returns a formatted summary of recent emails.

    Args:
        count: Max emails to return.
        unread_only: If True, only show unread messages.

    Returns:
        Formatted string for Telegram.
    """
    conn = None
    try:
        conn = _connect_imap()
        conn.select("INBOX", readonly=True)

        if unread_only:
            status, data = conn.search(None, "UNSEEN")
        else:
            status, data = conn.search(None, "ALL")

        if status != "OK" or not data[0]:
            if unread_only:
                return "Нет непрочитанных писем."
            return "Входящие пусты."

        msg_ids = data[0].split()
        # Take the latest N
        msg_ids = msg_ids[-count:]
        msg_ids.reverse()  # newest first

        lines = []
        if unread_only:
            lines.append(f"Непрочитанных: {len(data[0].split())}")
            if len(data[0].split()) > count:
                lines.append(f"(показаны последние {count})")
        lines.append("")

        for i, msg_id in enumerate(msg_ids, 1):
            status, msg_data = conn.fetch(msg_id, "(BODY.PEEK[HEADER])")
            if status != "OK":
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            from_name = _extract_name(msg["From"])
            subject = _decode_header_value(msg["Subject"]) or "(без темы)"
            date_str = msg["Date"] or ""

            # Parse date for display
            date_display = ""
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_str)
                now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
                if dt.date() == now.date():
                    date_display = dt.strftime("%H:%M")
                elif dt.date() == (now - timedelta(days=1)).date():
                    date_display = "вчера " + dt.strftime("%H:%M")
                else:
                    date_display = dt.strftime("%d.%m")
            except Exception:
                pass

            time_part = f" ({date_display})" if date_display else ""
            lines.append(f"{i}. {from_name}{time_part}\n   {subject}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"IMAP check_inbox error: {e}")
        return f"Ошибка чтения почты: {e}"
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
            try:
                conn.logout()
            except Exception:
                pass


def read_email(index: int = 1) -> str:
    """Reads the Nth most recent unread email (formatted text only).

    Wrapper around read_email_full() for backward compatibility.
    """
    result = read_email_full(index)
    return result.get("text", "Ошибка чтения письма.")


def read_email_full(index: int = 1) -> dict:
    """Reads the Nth most recent unread email with full metadata.

    Args:
        index: 1-based index (1 = most recent unread).

    Returns:
        Dict with keys: text, from_email, from_name, subject, body, msg_uid, error
    """
    conn = None
    try:
        conn = _connect_imap()
        conn.select("INBOX", readonly=True)

        status, data = conn.search(None, "UNSEEN")
        if status != "OK" or not data[0]:
            return {"text": "Нет непрочитанных писем.", "error": "no_unread"}

        msg_ids = data[0].split()
        msg_ids.reverse()  # newest first

        if index < 1 or index > len(msg_ids):
            return {
                "text": f"Письмо #{index} не найдено. Всего непрочитанных: {len(msg_ids)}",
                "error": "out_of_range",
            }

        msg_id = msg_ids[index - 1]

        # Get UID for later mark-as-read
        uid_status, uid_data = conn.fetch(msg_id, "(UID)")
        msg_uid = None
        if uid_status == "OK" and uid_data[0]:
            uid_match = re.search(r"UID (\d+)", uid_data[0].decode() if isinstance(uid_data[0], bytes) else str(uid_data[0]))
            if uid_match:
                msg_uid = uid_match.group(1)

        # Fetch full message (PEEK = don't mark as read)
        status, msg_data = conn.fetch(msg_id, "(BODY.PEEK[])")
        if status != "OK":
            return {"text": "Ошибка чтения письма.", "error": "fetch_failed"}

        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        from_name = _extract_name(msg["From"])
        from_email_addr = _extract_email_address(_decode_header_value(msg["From"]))
        subject = _decode_header_value(msg["Subject"]) or "(без темы)"
        body = _get_text_body(msg)

        # Truncate body for Telegram display
        display_body = body
        if len(display_body) > 3000:
            display_body = display_body[:3000] + "\n\n... (обрезано)"

        text = (
            f"От: {from_name} <{from_email_addr}>\n"
            f"Тема: {subject}\n"
            f"{'─' * 30}\n"
            f"{display_body}"
        )

        return {
            "text": text,
            "from_email": from_email_addr,
            "from_name": from_name,
            "subject": subject,
            "body": body,         # full body (not truncated)
            "msg_uid": msg_uid,   # IMAP UID for mark-as-read
            "error": None,
        }

    except Exception as e:
        logger.error(f"IMAP read_email error: {e}")
        return {"text": f"Ошибка чтения письма: {e}", "error": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
            try:
                conn.logout()
            except Exception:
                pass


# ── Mark as read ──────────────────────────────────────────────────


def mark_as_read(msg_uid: str) -> str:
    """Marks an email as read by IMAP UID.

    Args:
        msg_uid: IMAP UID string.

    Returns:
        Success or error message.
    """
    if not msg_uid:
        return "Нет UID письма для отметки."
    try:
        conn = _connect_imap()
        conn.select("INBOX")  # NOT readonly — need to modify flags
        # Use UID STORE to set \Seen flag
        status, _ = conn.uid("STORE", msg_uid, "+FLAGS", "(\\Seen)")
        conn.close()
        conn.logout()
        if status == "OK":
            return "Письмо отмечено как прочитанное."
        return "Не удалось отметить письмо."
    except Exception as e:
        logger.error(f"IMAP mark_as_read error: {e}")
        return f"Ошибка: {e}"


# ── Reply to email ────────────────────────────────────────────────


def reply_to_email(to: str, subject: str, body: str, original_body: str = "") -> str:
    """Sends a reply email via SMTP.

    Automatically adds 'Re:' prefix if not present.
    Includes quoted original message.

    Args:
        to: Recipient email (original sender).
        subject: Original subject line.
        body: Reply text.
        original_body: Original message text to quote.

    Returns:
        Success or error message.
    """
    if not YANDEX_EMAIL or not YANDEX_APP_PASSWORD:
        return "Ошибка: YANDEX_EMAIL or YANDEX_APP_PASSWORD not set."

    # Add Re: prefix
    re_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"

    # Build reply body with quote
    full_body = body
    if original_body:
        # Truncate original for quoting
        quoted = original_body[:2000]
        if len(original_body) > 2000:
            quoted += "\n[...]"
        quoted_lines = "\n".join(f"> {line}" for line in quoted.split("\n"))
        full_body = f"{body}\n\n--- Исходное сообщение ---\n{quoted_lines}"

    return send_email(to, re_subject, full_body)


# ── AI Summary ────────────────────────────────────────────────────


def summarize_email(body: str, subject: str = "", from_name: str = "") -> str:
    """Uses GPT-5 to generate a concise Russian summary of the email.

    Args:
        body: Full email body text.
        subject: Email subject for context.
        from_name: Sender name for context.

    Returns:
        Russian summary string.
    """
    if not body or len(body.strip()) < 30:
        return "Письмо слишком короткое для саммари."

    try:
        client = get_openai_client()

        context_parts = []
        if from_name:
            context_parts.append(f"От: {from_name}")
        if subject:
            context_parts.append(f"Тема: {subject}")
        context_header = "\n".join(context_parts)

        # Truncate very long emails for API
        email_text = body[:6000]
        if len(body) > 6000:
            email_text += "\n\n[... текст обрезан ...]"

        response = client.chat.completions.create(
            model=MODEL_MAIN,
            max_completion_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — ассистент руководителя. Сделай краткое содержание письма на русском языке. "
                        "Выдели: основную суть, ключевые факты/цифры, требуемые действия (если есть). "
                        "Формат: 3-5 предложений, без воды."
                    ),
                },
                {
                    "role": "user",
                    "content": f"{context_header}\n\n{email_text}",
                },
            ],
        )
        summary = response.choices[0].message.content.strip()
        return f"📝 Саммари:\n\n{summary}"

    except Exception as e:
        logger.error(f"Email summarize error: {e}")
        return f"Ошибка генерации саммари: {e}"


def send_email(to: str, subject: str, body: str) -> str:
    """Sends an email via Yandex SMTP.

    Args:
        to: Recipient email address.
        subject: Email subject.
        body: Plain text body.

    Returns:
        Success or error message.
    """
    if not YANDEX_EMAIL or not YANDEX_APP_PASSWORD:
        return "Ошибка: YANDEX_EMAIL or YANDEX_APP_PASSWORD not set."

    try:
        msg = MIMEMultipart()
        msg["From"] = YANDEX_EMAIL
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(YANDEX_EMAIL, YANDEX_APP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to}: {subject}")
        return f"Письмо отправлено: {to}\nТема: {subject}"

    except Exception as e:
        logger.error(f"SMTP send error: {e}")
        return f"Ошибка отправки: {e}"
