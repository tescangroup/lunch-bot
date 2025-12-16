"""Module for working with active scrappers"""

import traceback
from typing import Callable

from src.scrappers.utils import Menu, MenuItem
from src.scrappers.leharo import get_leharo_menu
from src.scrappers.natrati import get_natrati_menu
from src.scrappers.ukohoutu import get_ukohoutu_menu
# pylint: disable=C0301
from src.services.formatters import get_czech_day_name, get_czech_date, get_czech_today_header, format_menu_to_teams_message
from src.services.mail import get_mail_client, get_default_sender
from src import settings


MENU_SCRAPPERS: list[Callable[[], Menu]] = [
    get_leharo_menu,
    get_natrati_menu,
    get_ukohoutu_menu,
]


def get_all_menus() -> list[Menu]:
    """Get menus from all scrappers."""
    menus = []
    for scraper in MENU_SCRAPPERS:
        # Handle exceptions
        try:
            # Initialize the menu object
            menu: Menu = scraper()
            menus.append(menu)

        # pylint: disable=W0718
        except Exception:
            # Print error message
            traceback.print_exc()

            menus.append(
                Menu(
                    name=scraper.__qualname__,
                    items=[MenuItem(
                        name="Chyba při získávání menu.",
                        price=""
                    )],
                    day=get_czech_day_name(),
                    date=get_czech_date(),
                )
            )

            # Jump to next menu
            continue
    return menus


def send_menus_to_teams(menus: list[Menu]) -> None:
    """Get menus from all scrappers and format them for MS Teams."""
    message_for_teams = ""
    for menu in menus:
        menu_message: str = format_menu_to_teams_message(menu)
        message_for_teams += f"{menu_message}\n\n"

    mail_client = get_mail_client()
    mail_client.send(
        subject=get_czech_today_header(),
        sender=get_default_sender(),
        receivers=[settings.LUNCH_CHANNEL_EMAIL_ADDRESS,],
        html=message_for_teams.strip(),
    )


if __name__ == "__main__":
    send_menus_to_teams(get_all_menus())
