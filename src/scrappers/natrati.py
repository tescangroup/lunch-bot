"""Module for getting lunch menu from Bernard Brno restaurant"""
import re

import requests
from bs4 import BeautifulSoup

from .utils import is_monday, Menu, MenuItem


def get_natrati_menu(url: str = "https://www.restauracenatrati.cz") -> Menu:
    """
    Get the lunch menu for "NA TRATI" restaurant.

    Parameters
    ----------
    url : str
        URL of the restaurant website.

    Returns
    -------
    Menu
        Menu object containing menu items for the current day.
    """
    # pylint: disable=R0914,R0912

    if is_monday():
        return Menu("Na trati", [MenuItem("Restaurace je v pondělí zavřená", "")], "", "")

    html_content = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html_content, "html.parser")

    # Najdi wrapper s obědovým menu
    menu_root = soup.find("div", {"id": "obedovemenu"})
    if not menu_root:
        raise ValueError("Div with id='obedovemenu' not found")

    # Najdi aktivní den – tlačítko s .nav-link.active
    active_button = menu_root.select_one("ul.nav button.nav-link.active")
    if not active_button:
        raise ValueError("Active day button (.nav-link.active) not found")

    # Text dne (Úterý, Středa, ...)
    day = active_button.get_text(strip=True)

    # Získání ID tab-panu aktivního dne
    target = active_button.get(
        "data-bs-target") or active_button.get("aria-controls")
    if not target:
        raise ValueError(
            "Active day button does not contain data-bs-target or aria-controls")

    # data-bs-target="#day-20251203" -> "day-20251203"
    target_id = target.lstrip("#")

    # Pokusíme se z ID vytáhnout datum ve formátu YYYYMMDD
    date_match = re.search(r"(\d{8})", target_id)
    if date_match:
        yyyymmdd = date_match.group(1)
        # YYYY-MM-DD -> DD. MM. YYYY
        date = f"{yyyymmdd[6:8]}. {yyyymmdd[4:6]}. {yyyymmdd[0:4]}"
    else:
        # Fallback: použijeme jen text z lunch-menu-description, pokud existuje
        date_span = menu_root.find("span", class_="lunch-menu-description")
        if date_span:
            date = date_span.get_text(" ", strip=True)
        else:
            date = ""

    # Najdi tab-pane pro aktivní den
    tab_pane = menu_root.find("div", {"id": target_id})
    if not tab_pane:
        raise ValueError(f"Tab pane with id='{target_id}' not found")

    # Všechny tabulky – každá reprezentuje jednu položku menu (hlavní jídlo + polévka v řádku pod)
    tables = tab_pane.find_all("table")
    menu_objs = []

    for table in tables:
        name_td = table.find("td", class_="list-items-item-name")
        price_td = table.find("td", class_="list-items-item-price")

        if not name_td:
            # pokud u nějakého stolu není jméno, přeskočíme
            continue

        food_name = name_td.get_text(" ", strip=True)

        # Polévka / dodatečný popis v dalším řádku
        description = None
        desc_row = table.find("tr", class_="menu-items-more-information")
        if desc_row:
            desc_span = desc_row.find("span", class_="list-items-description")
            if desc_span:
                description = desc_span.get_text(" ", strip=True)

        if description:
            full_name = f"{food_name} ({description})"
        else:
            full_name = food_name

        price = price_td.get_text(" ", strip=True) if price_td else ""

        menu_objs.append(MenuItem(full_name, price))

    # Název restaurace můžeš klidně parametrizovat; tady ho nechám generický
    menu = Menu("Na trati", menu_objs, day.lower(), date)
    return menu


if __name__ == "__main__":
    print(get_natrati_menu().get_json_menu())
