"""Module for formatting messages"""

from datetime import datetime
from src.scrappers.utils import Menu, day_dict


def get_czech_day_name(date: datetime) -> str:
    """
    Return the Czech name of the weekday for the given date.

    Parameters:
        date (datetime): The date from which to extract the weekday name.

    Returns:
        str: The Czech weekday name with the first letter capitalized.
    """
    czech_day_name = day_dict[date.strftime("%A").lower()]
    return czech_day_name.capitalize()


def get_czech_date(date: datetime) -> str:
    """
    Return a Czech-formatted date string in the form 'D. M.' without leading zeros.

    Parameters:
        date (datetime): The date to be formatted.

    Returns:
        str: The formatted date string in Czech style.
    """
    return date.strftime("%d. %m.").replace(" 0", " ")


def get_czech_today_header() -> str:
    """
    Return a header string containing today's Czech weekday name and date.

    Returns:
        str: For example, 'Úterý 21. 1.'.
    """
    today = datetime.today()
    czech_day_name = get_czech_day_name(today)
    czech_date = get_czech_date(today)
    return f"{czech_day_name} {czech_date}"


def format_menu_to_teams_message(menu: Menu) -> str:
    """Convert scrapper output into a formatted MS Teams message."""

    lines = []
    lines.append(f"<h1>{menu.name}</h1>")

    for item in menu.items:
        # Description and allergen separation
        lines.append(f"{item.name} {item.price} <br>")
    lines.append("<hr>")

    return "".join(lines)
