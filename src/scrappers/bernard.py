"""Module for getting lunch menu from Bernard Brno restaurant"""
import re

import requests
from bs4 import BeautifulSoup

from .utils import Menu, MenuItem


def get_bernard_menu(url: str = "https://www.bernardbar.cz/bar/brno") -> Menu:
    """
    Get the lunch menu for Bernard Pub & Bar.

    Parameters
    ----------
    url : str
        URL of the restaurant website.

    Returns
    -------
    Menu
        Menu object containing menu items for the current day.
    """
    # pylint: disable=R0914

    html_content = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html_content, "html.parser")
    active_day = soup.find("li", {"class": "active-tab"})
    day = active_day.find("strong").get_text().strip()
    date = active_day.find("span").get_text().strip()
    menu_list = soup.find(
        "div",
        {
            "id": re.compile(r"day-selection-tab-.*"),
            "class": re.compile(r".*active-tab.*"),
        },
    )
    menu_items = menu_list.find_all("ul", {"class": "food-list"})
    menu_objs = []
    for menu_item in menu_items:
        items = menu_item.find_all("div", {"class": "single-food"})
        for item in items:
            food_name = item.find("strong").get_text()
            food_price = item.find("span", {"class": "food-price"}).get_text()
            menu_obj = MenuItem(food_name, food_price)
            menu_objs.append(menu_obj)
    menu = Menu("Bernard", menu_objs, day.lower(), date)
    return menu


if __name__ == "__main__":
    print(get_bernard_menu("https://www.bernardbar.cz/bar/brno").get_json_menu())
