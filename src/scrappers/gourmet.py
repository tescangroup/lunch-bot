"""Module for getting lunch menu from Gourmet restaurant"""
from datetime import datetime

import re
import requests
from bs4 import BeautifulSoup

from .utils import Menu, MenuItem, day_dict


def get_gourmet_menu(
    url: str = "http://ponavka.gourmetrestaurant.cz/",
) -> Menu:
    """
    Get the lunch menu for Gourmet Brno.
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

    # get html content
    html_content = requests.get(url, timeout=10).text

    # parse html content
    soup = BeautifulSoup(html_content, "html.parser")

    # get menu for the current day
    menu_field = soup.find("div", {"class": "event-info text-center"})
    menu_date = soup.find("h1", {"class": "event-title-w text-center"}).get_text()
    d, m, y = menu_date.split(".")
    menu_date = datetime(int(y), int(m), int(d))
    day_name = day_dict[menu_date.strftime("%A").lower()]
    menu_date = menu_date.strftime("%d.%m.")
    menu_table = menu_field.find("table")
    menu_items = menu_table.find_all("tr")

    # create menu object and store menu items
    menu_objs = []
    for item in menu_items:
        item_field = item.find_all("td")
        food_name = item_field[1].get_text()
        food_price = item_field[2].get_text()
        menu_obj = MenuItem(food_name, food_price)
        menu_objs.append(menu_obj)

    # pizza items - find element w/ content "PIZZA", next sibling should be the field with pizzas
    pizza_heading = soup.find(string="PIZZA")
    pizza_siblings = pizza_heading.parent.find_next_siblings() if pizza_heading else []
    pizza_field = pizza_siblings[0].stripped_strings if pizza_siblings else []
    food_name = ""
    food_price = ""
    # use the stripped strings as the field is poorly formatted
    for value in list(pizza_field):
        # split value to obtain description and price
        pattern = r'^\s*(Pizza\s*\d+\s*[\*\d,]*)?\s*((?!\d+\s*Kč).*)?\s*(\d+\s*Kč)?\s*$'
        m = re.match(pattern, value, flags=re.MULTILINE)
        if not m:  # match is None
            continue
        for c, g in enumerate(m.groups()):
            if c == 0 and g:
                food_name = g
            if c == 1 and g:
                food_name = (food_name + ": " + g).strip() if g else food_name
            if c == 2 and g:
                food_price = g.strip()
                if food_name and food_price:
                    menu_obj = MenuItem(food_name, food_price)
                    menu_objs.append(menu_obj)

    menu = Menu("Gourmet Ponávka", menu_objs, day_name, menu_date)
    return menu


if __name__ == "__main__":
    print(get_gourmet_menu("http://ponavka.gourmetrestaurant.cz/").get_json_menu())
