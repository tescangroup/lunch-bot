"""Module for loading settings from .env file"""
import os

from dotenv import load_dotenv


load_dotenv()

SMTP_HOST=os.getenv("SMTP_HOST", "smtp.mailtrap.io")
SMTP_PORT=int(os.getenv("SMTP_PORT", "587"))
SMTP_USER=os.getenv("SMTP_USER", "user")
SMTP_PASSWORD=os.getenv("SMTP_PASSWORD", "password")
SMTP_FROM=os.getenv("SMTP_FROM", "Lunch Bot <lunchbot@example.com>")
