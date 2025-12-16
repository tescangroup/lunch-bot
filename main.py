#!/usr/bin/env python3

"""Entry point for the Lunch bot scheduler.

This script initializes and starts the internal APScheduler-based scheduler,
which periodically runs the Lunch bot tasks (such as collecting daily menus
from the configured scrapers and sending formatted messages to Microsoft Teams).
It replaces the need for a system-level cron job and keeps all scheduling logic
within the Python application itself.
"""


from src.services.scheduler import main as start_scheduler


if __name__ == "__main__":
    start_scheduler()
