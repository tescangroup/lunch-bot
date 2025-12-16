"""Module for getting lunch menu from "Na Hasicce" restaurant"""
from datetime import datetime

import io
import requests
import regex

from bs4 import BeautifulSoup
from PIL import Image
from pytesseract import pytesseract


from .utils import Menu, MenuItem, day_dict

def get_hasicka_menu(
    url: str = "https://nahasicce.cz/?lang=cs",
    check_date: bool = True
) -> Menu:
    # pylint: disable=R0911,R0912,R0914,R0915
    """
    Parameters
    ----------
    url : str
        URL of the restaurant website.
    check_date : bool
        flag if you want menu only for the current date (True) or any available (False).

    Returns
    -------
    Menu
        Menu object containing menu items for the current day.
    """

    ret_menu = Menu(
        "Na Hasičce",
        [MenuItem("Nenalezeno menu pro dnešní den","")],
        day_dict[datetime.now().strftime("%A").lower()],
        datetime.now().strftime("%d.%m."),
    )

    # get html content
    # needs cookie and user agent, otherwise returns just javascript bullcrap
    # pylint: disable=C0301
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0', 'Cookie':'AMCV_1548453B5D8483AE0A495FCB%40AdobeOrg=179643557%7CMCIDTS%7C19825%7CMCMID%7C92214235278812603797120205436681051174%7CMCOPTOUT-1712917980s%7CNONE%7CvVersion%7C5.5.0; rbzid=XeNXGFDRlnehOGsGuXWH+uQy/9XzM+lWsCGv51Q1eJW4rNY8MUJ9jG4FnFJbYEYj7IROndZiocu4z/smAjLW+4UriETWX6Gb1wJZA59YyKBy8ae6RPg3tOtsj+6CQ1wmoAeDcax2fJpXSod8rpvAQ6jCcawhn7IVTSnbXuZwl0PCtfvJ9M3/hzcV7+Okvt3xHiv8R7HPyGu7x17EDfy/96i9n6QUlFH9mTj/SSkdf0kVhP001B5ST/hFPDfjXvv9; rbzsessionid=e7ab98f3aca5de4515a1114d130aa99e; AMCVS_1548453B5D8483AE0A495FCB%40AdobeOrg=1; cookieAcceptanceLevelWSB=2; ADVTrackingWSB=1; s_cc=true'}
    html_content = requests.get(url, headers=headers, timeout=10).text

    # parse html content
    soup = BeautifulSoup(html_content, "html.parser")

    # get menu image element
    result = soup.find("a", class_="menu-image")
    if not result:
        return ret_menu # webpage in bad format

    # get manu image url
    img_url = result['href']
    if not img_url or len(img_url) <= 0:
        return ret_menu # webpage in bad format

    # get image content
    img_response = requests.get(img_url, timeout=10)
    if not img_response.ok:
        return ret_menu # webpage in bad format
    img_content = img_response.content

    # load the img content into Image
    img = Image.open(io.BytesIO(img_content))

    # Defining path to tesseract.exe
    #path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Providing the tesseract executable location to pytesseract library
    #pytesseract.tesseract_cmd = path_to_tesseract

    # Passing the image object to image_to_string() function
    # This function will extract the text from the image
    # passing the lang helps with identifiing language,
    # you need the language package installed in tesseract
    menu_text = pytesseract.image_to_string(img, lang='ces')

# example OCR text for testing and refference
#    menu_text = r"""Na Hasičce
#Reafaurace
#
#DENNÍ MENU
#pondělí 11.12.2023
#
#DENNÍ MENU KAŽDÝ DEN
#NA FACEBOOKU Restaurace Na Hasičce
#nebo na www.restauracenahasicce.eatbu.com
#
#POLÉVKA
#Čočková
#MENU č.1
#
#150g Steak z vepřové krkovice podávaný na pikantní
#zeleninovém lůžku s opékanými bramborami a naší tatarskou
#omáčkou
#169,-
#
#MENU č.2
#
#120g Smažená kuřecí kapsa plněná slaninou a nivou
#se šťouchanými bramborami
#149,-
#
#MENU č.3
#
#120g Boloňské špagety
#sypané sýrem a čerstvou bazalkou
#145,-
#
#Potravinové alergeny: 1)Obiloviny obsahující lepek, 2)Korýši, 3)Vejce, 4)Ryby,
# 5)Podzemnice olejná, 6)Sójové boby,
#7)Mléko, 8)Ořechy, 9)Celer, 10)Hořčice, 11)Sezamová semena,
# 12)S02 více jak 10mg/kg, 13)Vlčí bob, 14)Měkkýši
#Polévka je v ceně menu. Samostatná polévka 45,-
#Menu box 7,-/14,-"""

    #Manual parsing of data from the recognized text

    if check_date:
        # find date
        res = regex.search(r"([0-3]?[0-9])\.(1?[0-9])\.(20[2-9][0-9])", menu_text)
        if not res:
            return ret_menu #no date found
        datum = ""
        if len(res[1]) < 2:
            datum += "0"
        datum += res[1] + "."
        if len(res[2]) < 2:
            datum += "0"
        datum += res[2] + "." + res[3]

        #check date
        date = datetime.strptime(datum, '%d.%m.%Y')
        today = datetime.now()
        if date.date() != today.date():
            return ret_menu #not actual date

    # find polevka and alergeny (to limit the search, alergens are listed right after menus)
    # using fuzzy regex: {e<X} specifies alowed X error chars (to allow some error from OCR)
    pol = regex.search(r'(POLÉVKA){e<2}',menu_text,flags=regex.IGNORECASE)
    ale = regex.search(r'(Potravinové alergeny){e<4}',menu_text,flags=regex.IGNORECASE)
    if not pol or not ale:
        return ret_menu # menu not found
    start = pol.end()
    end = ale.start()
    if start >= end:
        return ret_menu # menu not found
    menupos = []
    menupol = [pol.end(), end]
    menupos.append(menupol)
    i = 0
    #search for menus between polevka and alergeny and mark string positions
    while True:
        menu = regex.search(
            r'(MENU č/.[0-9]){e<2}',
            menu_text,
            pos=start,
            endpos=end,
            flags=regex.IGNORECASE
        )
        if not menu:
            break
        menupos[i][1] = menu.start()
        menum = [menu.end(), end]
        menupos.append(menum)
        start = menu.end()
        i+=1

    # extract menu strings from the text based on the saved string positions
    menu_objs = []
    for menu in menupos:
        menustr = menu_text[menu[0]:menu[1]]
        # find price
        price = regex.search(r'([0-9][0-9][0-9])',menustr,flags=regex.IGNORECASE | regex.REVERSE)
        jidlo = menustr
        cena = ""
        if price:
            cena = price[0] + " Kč"
            jidlo = menustr[:price.start()]
        # beatify the string and put it into MenuItem together with price
        item = MenuItem(jidlo.replace('\n', " ").strip(), cena)
        menu_objs.append(item)

    # replace the menu items into the menu object
    ret_menu.items=menu_objs
    return ret_menu


if __name__ == "__main__":
    print(get_hasicka_menu().get_json_menu())
