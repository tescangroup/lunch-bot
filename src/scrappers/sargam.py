"""Module for getting lunch menu from Sargam Indian restaurant"""

from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .utils import Menu, MenuItem, day_dict


def get_name_of_current_day() -> str:
    """
    Get the name of the current day in English.
    """
    return datetime.now().strftime("%A")


def get_sargam_menu(url: str = "https://sargamrestaurace.cz/Sargam1/DMenuItems") -> Menu:
    """
    Get the lunch menu for Sargam restaurant.

    Parameters
    ----------
    url : str
        URL of the restaurant website.

    Returns
    -------
    Menu
        Menu object containing menu items for the current day.
    """

    html_content = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html_content, "html.parser")

    # get name of the current day
    current_day_str = get_name_of_current_day()

    # find the element for current day
    day_header = soup.find(attrs={"id": current_day_str, "class": "category"})

    # get grandparent element to find the menu items
    day_menu = day_header.find_parent().find_parent()

    # find all dish elements in the day menu
    dishes = day_menu.find_all("div", {"class": "dish-name"})

    # for each dish get the next element with class dish-number which contains the price
    dish_prices = [dish.find_next(
        "div", {"class": "dish-number"}).get_text().strip() for dish in dishes]
    # for each dish get the next element with class dish-info which contains additional info
    dish_infos = [dish.find_next(
        "div", {"class": "dish-info"}).get_text().strip() for dish in dishes]

    dish_names = [dish.get_text().strip() for dish in dishes]

    menu_items = []
    for dish_name, dish_info, dish_price in zip(dish_names, dish_infos, dish_prices):
        menu_items.append(
            MenuItem(f"**{dish_name}** ({dish_info})", dish_price))

    menu = Menu(":flag-in: Sargam :pepe_indian:", menu_items,
                day_dict[datetime.now().strftime("%A").lower()],
                datetime.now().strftime("%d.%m."),
                )
    return menu


if __name__ == "__main__":
    print(get_sargam_menu().get_json_menu())
