"""Module for getting lunch menu from U Kohoutů restaurant"""

from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .utils import Menu, MenuItem


def _safe_text(element, default: str = "") -> str:
    return element.get_text(" ", strip=True) if element else default


def get_ukohoutu_menu(
    url: str = "https://ukohoutubrno.cz/denni-menu/"
) -> Menu:
    """
    Get the lunch menu for U Kohoutů restaurant.

    Parameters
    ----------
    url : str
        URL of the restaurant daily menu page.

    Returns
    -------
    Menu
        Menu object containing menu items for the current day.
    """
    # pylint: disable=R0914

    html_content = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html_content, "html.parser")

    # očekáváme strukturu s h1 "Denní menu" a uvnitř .listek bloky po dnech
    menulist = soup.find("div", class_="listek")
    if not menulist:
        raise ValueError(
            "Div with class 'listek' (daily menu container) not found")

    # dnešní datum ve formátu jako na webu: 'D. M. RRRR' (bez nul před jednocifernými čísly)
    today = datetime.today().date()
    today_str = f"{today.day}. {today.month}. {today.year}"

    # Každý den je v <div class="row mb-4">
    day_blocks = menulist.find_all("div", class_="row mb-4")
    if not day_blocks:
        raise ValueError("No day blocks with class 'row mb-4' found in menu")

    selected_block = None
    for block in day_blocks:
        date_div = block.find("div", class_="date")
        date_text = _safe_text(date_div)
        if date_text == today_str:
            selected_block = block
            break

    # fallback – pokud nenajdeme dnešek, vezmeme první blok (často je to aktuální pondělí)
    if not selected_block:
        selected_block = day_blocks[0]

    # název dne (Pondělí, Úterý, ...)
    day_div = selected_block.find("div", class_="day")
    day_name = _safe_text(day_div)

    # datum přesně tak, jak je na webu
    date_div = selected_block.find("div", class_="date")
    date = _safe_text(date_div)

    # polévka – použijeme ji jako součást popisu každého jídla v závorce
    soup_row = selected_block.find("div", class_="row-polevka")
    soup_div = soup_row.find("div", class_="polevka") if soup_row else None
    soup_text = _safe_text(soup_div)

    # jednotlivá jídla – každý blok <div class="row row-food">
    food_rows = selected_block.find_all("div", class_="row row-food")

    menu_items = []
    for row in food_rows:
        food_div = row.find("div", class_="food")
        price_div = row.find("div", class_="price")

        food_name = _safe_text(food_div)
        price = _safe_text(price_div)

        # jméno jídla očistíme od "A: ..." (alergeny), necháme jen text před "A:"
        if "A:" in food_name:
            food_name = food_name.split("A:", 1)[0].strip()

        # totéž u polévky – pro případ, že tam jsou alergeny
        clean_soup = soup_text
        if "A:" in clean_soup:
            clean_soup = clean_soup.split("A:", 1)[0].strip()

        # plný název – jídlo + polévka v závorce
        full_name = (
            f"{food_name} (polévka: {clean_soup})"
            if clean_soup
            else food_name
        )

        menu_items.append(MenuItem(full_name, price))

    return Menu("U Kohoutů", menu_items, day_name.lower(), date)


if __name__ == "__main__":
    print(get_ukohoutu_menu().get_json_menu())
