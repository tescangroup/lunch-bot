"""Utility module for simplified email creation and sending.

This module provides helper functions for constructing email messages and
creating a preconfigured email-sending client based on application settings.
"""

from email.message import EmailMessage
from redmail import EmailSender

from src import settings


def get_default_sender() -> str:
    """Return the default configured sender email address.

    The value is taken from application settings (`settings.SMTP_FROM`).

    Returns:
        str: Default email address used as the "From" field.
    """
    return settings.SMTP_FROM


def get_default_message() -> EmailMessage:
    """Create and return a new EmailMessage with a predefined sender.

    The message returned contains only the "From" header populated using
    the default sender. The caller is expected to fill in the remaining
    fields such as subject, recipients, and body.

    Returns:
        EmailMessage: A new email message initialized with the default sender.
    """
    msg = EmailMessage()
    msg["From"] = get_default_sender()
    return msg


def get_mail_client() -> EmailSender:
    """Create and return a preconfigured Redmail EmailSender client.

    The client is initialized using SMTP parameters defined in application
    settings, such as host, port, username, and password.

    Returns:
        EmailSender: Configured instance ready to send emails.
    """
    return EmailSender(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
    )


if __name__ == "__main__":
    # Example usage for manual testing.
    client = get_mail_client()
    client.send(
        subject="Test mail",
        sender=get_default_sender(),
        receivers=["test@lukasmatuska.cz"],
        text="Hello world!",
        html="<h1>Hi, </h1><p>This is a testing email.</p>"
    )
