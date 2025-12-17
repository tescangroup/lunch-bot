"""Module for getting lunch menu from Leharo bistro"""

from datetime import datetime

import re
import io
import requests

from bs4 import BeautifulSoup
from PIL import Image
from pytesseract import pytesseract

from .utils import Menu, MenuItem, day_dict


def get_name_of_current_day() -> str:
    """
    Get the name of the current day in Czech.
    """
    return day_dict[datetime.now().strftime("%A").lower()]

def get_leharo_menu(url: str = "https://dejsileharo.cz/bistroleharo-poledni-menu/") -> Menu:
    # pylint: disable=R0914,R0915,R0801,W0718,R0912
    """
    Parameters
    ----------
    url : str
        URL of the bistro website.

    Returns
    -------
    Menu
        Menu object containing menu items for the current day.
    """

    current_day = get_name_of_current_day()
    date = datetime.now()
    current_date = f"{date.day}.{date.month}."

    ret_menu = Menu(
        "Leháro",
        [MenuItem("Menu pro dnešní den nebylo nalezeno.", "")],
        current_day,
        current_date,
    )

    # get html content
    # needs cookie and user agent, otherwise returns just javascript bullcrap
    # pylint: disable=C0301
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
               'Cookie': 'AMCV_1548453B5D8483AE0A495FCB%40AdobeOrg=179643557%7CMCIDTS%7C19825%7CMCMID%7C92214235'
                         '278812603797120205436681051174%7CMCOPTOUT-1712917980s%7CNONE%7CvVersion%7C5.5.0; rbzid'
                         '=XeNXGFDRlnehOGsGuXWH+uQy/9XzM+lWsCGv51Q1eJW4rNY8MUJ9jG4FnFJbYEYj7IROndZiocu4z/smAjLW+'
                         '4UriETWX6Gb1wJZA59YyKBy8ae6RPg3tOtsj+6CQ1wmoAeDcax2fJpXSod8rpvAQ6jCcawhn7IVTSnbXuZwl0P'
                         'CtfvJ9M3/hzcV7+Okvt3xHiv8R7HPyGu7x17EDfy/96i9n6QUlFH9mTj/SSkdf0kVhP001B5ST/hFPDfjXvv9;'
                         ' rbzsessionid=e7ab98f3aca5de4515a1114d130aa99e; AMCVS_1548453B5D8483AE0A495FCB%40Adobe'
                         'Org=1; cookieAcceptanceLevelWSB=2; ADVTrackingWSB=1; s_cc=true'
               }
    html_content = requests.get(url, headers=headers, timeout=10).text

    # parse html content
    soup = BeautifulSoup(html_content, "html.parser")

    # get menu image element
    main = soup.find("main", class_="site-main")
    result = main.find("img")
    if not result:
        return ret_menu  # webpage in bad format

    # get manu image url
    img_url = result['src']
    if not img_url or len(img_url) <= 0:
        return ret_menu  # webpage in bad format

    # get image content
    img_response = requests.get(img_url, timeout=10)
    if not img_response.ok:
        return ret_menu  # webpage in bad format
    img_content = img_response.content

    # load the img content into Image
    img = Image.open(io.BytesIO(img_content))

    menu_text = pytesseract.image_to_string(img, lang='ces', config="--psm 4")
    menu_lines = menu_text.splitlines()

    # remove empty elements
    menu_lines = [x for x in menu_lines if x != '']

    try:
        # find current date span and check current date belongs to it

        # find the menu for the current day using regex
        start_line = -1
        tip_line = -1
        current_day_regex = re.compile(f".*{current_day}.*".upper())
        tip_regex = re.compile(".*tip týdne.*".upper())

        for lnum, line in enumerate(menu_lines):
            day_header = current_day_regex.match(line)
            tip_header = tip_regex.match(line)
            if day_header:
                start_line = lnum
            if tip_header:
                tip_line = lnum

        if start_line < 0:
            return ret_menu

        soup_of_the_day = ""
        # get the soup of the day and the rest of the menu items
        soup_regex = re.compile(r"^\s*(\S.*\S)\s*$")
        menu_regex = re.compile(r"^\s*(\S.*\S)\s+(\d+)\s*,*-*\s*$")
        menu_objs = []
        soup_was = False
        for lnum, line in enumerate(menu_lines[start_line+1:]):
            menu_match = menu_regex.match(line)
            soup_match = soup_regex.match(line)
            if not menu_match and (soup_was or not soup_match):
                break
            if soup_match and not soup_was:
                soup_of_the_day = soup_match.group(0).strip()
                menu_objs.append(MenuItem(soup_of_the_day, ""))
                soup_was = True
            if menu_match:
                menu_description = menu_match.group(1).strip()
                menu_price = menu_match.group(2).strip() + " Kč"
                menu_obj = MenuItem(menu_description, menu_price)
                menu_objs.append(menu_obj)

        tip_first_line = ""
        for lnum, line in enumerate(menu_lines[tip_line+1:]):
            menu_match = menu_regex.match(line)
            if menu_match:
                menu_description = menu_match.group(1).strip()
                menu_price = menu_match.group(2).strip() + " Kč"
                menu_obj = MenuItem(tip_first_line + " (" + menu_description + ")", menu_price)
                menu_objs.append(menu_obj)
                break
            tip_match = soup_regex.match(line)
            if tip_match:
                tip_first_line = tip_match.group(0).strip()


        menu = Menu("Leháro", menu_objs, current_day, current_date)
    # if the menu for the current day is not found, return a menu not found message
    except Exception as e:
        print(e)
        menu = Menu(
            "Leháro",
            [MenuItem("Menu pro dnešní den nebylo nalezeno.", "")],
            current_day,
            current_date,

        )
    return menu


if __name__ == "__main__":
    print(get_leharo_menu().get_json_menu())
