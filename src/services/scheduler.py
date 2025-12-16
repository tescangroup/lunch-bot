#!/usr/bin/env python3
"""
Internal scheduler for running Lunch bot without system cron.
Runs the menu sending job by the configured schedule.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.services.lunch import get_all_menus, send_menus_to_teams
from src.settings import LUNCH_DAY_OF_WEEK, LUNCH_HOUR, LUNCH_MINUTES

def run_lunch_job():
    """Job: fetch menus and send them to MS Teams."""
    print("Running lunch job…")
    menus = get_all_menus()
    send_menus_to_teams(menus)
    print("Lunch job finished.")


def main():
    """Configure and start the internal scheduler."""
    scheduler = BlockingScheduler()

    # Cron job to run lunch job on specified days and times
    scheduler.add_job(
        run_lunch_job,
        CronTrigger(
            day_of_week=LUNCH_DAY_OF_WEEK,
            hour=LUNCH_HOUR,
            minute=LUNCH_MINUTES
        ),
        id="lunch_job",
        replace_existing=True,
    )

    print("Scheduler started. Waiting for jobs...")
    scheduler.start()


if __name__ == "__main__":
    main()
