"""Module for getting lunch menu from Pepe restaurant"""
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .utils import Menu, MenuItem, day_dict


def get_current_date_string():
    """
    Get current date in expected format, i.e.:
    "DAY_OF_THE_WEEK – dd. mm. yyyy"

    Returns
    -------
    str
        Formatted current date.
    """
    current_day = day_dict[datetime.now().strftime("%A").lower()]
    current_date = datetime.now().strftime("%d. %m. %Y")
    return f"{current_day[0].upper()+current_day[1:]} – {current_date}"


def get_pepe_menu(url: str = "https://www.peperestaurace.cz/obedove-menu/") -> Menu:
    """
    Get the lunch menu for Pepe.
    Parameters
    ----------
    url : str
        URL of the restaurant website.

    Returns
    -------
    Menu
        Menu object containing menu items for the current day.
    """
    # get html content
    html_content = requests.get(url, timeout=10).text

    # parse html content
    soup = BeautifulSoup(html_content, "html.parser")

    # get menu for the current day
    menu_fields = soup.find_all("table", style="")

    menu_objs = []
    # create menu object and store menu items
    for menu_field in menu_fields:
        # each table with menu has date in h2 header as previous sibling
        day_menu_header = menu_field.find_previous_sibling("h2")
        # check for current day & date
        if day_menu_header and day_menu_header.contents[0] == get_current_date_string():
            menu_items = menu_field.find_all("tr")
            for item in menu_items:
                item_field = item.find_all("td")
                food_name = item_field[0].get_text() + " " + item_field[1].get_text()
                food_price = item_field[2].get_text()
                menu_obj = MenuItem(food_name, food_price)
                menu_objs.append(menu_obj)

    menu = Menu(
        "Pepe",
        menu_objs,
        day_dict[datetime.now().strftime("%A").lower()],
        datetime.now().strftime("%d.%m."),
    )
    return menu


if __name__ == "__main__":
    print(get_pepe_menu().get_json_menu())
