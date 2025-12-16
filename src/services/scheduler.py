#!/usr/bin/env python3
"""
Internal scheduler for running Lunch bot without system cron.
Runs the menu sending job by the configured schedule.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from requests import JSONDecodeError, RequestException

from src.services.lunch import get_all_menus, send_menus_to_teams
from src.settings import LUNCH_DAY_OF_WEEK, LUNCH_HOUR, LUNCH_MINUTES
from src.services.app_logging import setup_logging


logger = setup_logging("scheduler")


def run_lunch_job():
    """Job: fetch menus and send them to MS Teams."""
    logger.info("Running lunch job...")
    try:
        menus = get_all_menus()
        send_menus_to_teams(menus)
        logger.info("Lunch job finished successfully.")
    except (RequestException, JSONDecodeError, RuntimeError, ValueError) as exc:
        logger.exception("Lunch job failed: %s", exc)
    # pylint: disable=W0718
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)


def main():
    """Configure and start the internal scheduler."""
    logger.info("Scheduler starting...")

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

    logger.info("Scheduler started. Waiting for jobs...")
    scheduler.start()


if __name__ == "__main__":
    main()
