"""Module for loading settings from .env file"""
import os

from dotenv import load_dotenv


load_dotenv()

LUNCH_CHANNEL_EMAIL_ADDRESS=os.getenv("LUNCH_CHANNEL_EMAIL_ADDRESS")
LUNCH_DAY_OF_WEEK=os.getenv("LUNCH_DAY_OF_WEEK", "mon-fri")
LUNCH_HOUR=os.getenv("LUNCH_HOUR")
LUNCH_MINUTES=os.getenv("LUNCH_MINUTES")
TZ=os.getenv("TZ", "Europe/Prague")
SMTP_HOST=os.getenv("SMTP_HOST", "smtp.mailtrap.io")
SMTP_PORT=int(os.getenv("SMTP_PORT", "587"))
SMTP_USER=os.getenv("SMTP_USER", "user")
SMTP_PASSWORD=os.getenv("SMTP_PASSWORD", "password")
SMTP_FROM=os.getenv("SMTP_FROM", "Lunch Bot <lunchbot@example.com>")
