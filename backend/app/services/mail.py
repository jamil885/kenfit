"""Explicit SMTP delivery or a private local mailbox for development."""

import logging
import os
import smtplib
import ssl
import uuid
from email.message import EmailMessage
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def deliver(email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = email
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        if settings.mail_mode == "file":
            folder = Path(settings.mail_outbox).resolve()
            folder.mkdir(parents=True, exist_ok=True, mode=0o700)
            target = folder / (uuid.uuid4().hex + ".eml")
            with os.fdopen(
                os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
            ) as output:
                output.write(msg.as_bytes())
        elif settings.mail_mode == "smtp":
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password or "")
                smtp.send_message(msg)
    except Exception:
        # Never log email body, credentials or recovery tokens.
        logger.error("Account email delivery failed; check SMTP or local mailbox configuration")


def clear_local_mail(email: str):
    if settings.mail_mode != "file":
        return
    from email import policy
    from email.parser import BytesParser
    from email.utils import getaddresses

    for file in Path(settings.mail_outbox).glob("*.eml"):
        if file.is_symlink():
            continue
        try:
            msg = BytesParser(policy=policy.default).parsebytes(file.read_bytes(), headersonly=True)
            addresses = {address.lower() for _, address in getaddresses(msg.get_all("To", []))}
            if email.lower() in addresses:
                file.unlink()
        except (OSError, ValueError):
            logger.error("Local account-mail cleanup failed; check mailbox permissions")
