"""Module for easier work with menus"""
from datetime import datetime
import json


def is_monday() -> bool:
    """
    Check if today is Monday.

    Returns
    -------
    bool
        True if today is Monday, False otherwise.
    """

    return datetime.now().weekday() == 0


class MenuItem:
    # pylint: disable=R0903
    """
    MenuItem class represents a single item on the menu.
    """

    def __init__(self, name: str, price: str = None):
        """
        Parameters
        ----------
        name : str
            Name of the menu item.
        price : str
            Price of the menu item in CZK.

        """
        self.name = name
        self.price = price

    def __repr__(self):
        """
        Returns
        -------
        str
            Name of the menu item and its price if available.
        """
        if self.price is None or self.price == "":
            return f"{self.name}"
        return f"{self.name} - {self.price}"


class Menu:
    """
    Menu class represents a menu for a single day.
    """

    def __init__(self, name: str, items: list[MenuItem], day: str, date: str):
        """
        Parameters
        ----------
        name : str
            Name of the restaurant.
        items : list
            List of MenuItem objects.
        day : str
            Name of the day in Czech.
        date : str
            Date in format DD.MM.
        """
        self.name = name
        self.items = items
        self.day = day
        if date.startswith("0"):
            self.date = date[1:]
        else:
            self.date = date

    def get_json_menu(self):
        """
        Returns
        -------
        str
            JSON representation of the menu.
        """
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=False,
            indent=4,
            ensure_ascii=False,
        )

    def __repr__(self):
        return f"{self.name} - {self.day} - {self.date} \n {self.items}"


day_dict = {
    "monday": "pondělí",
    "tuesday": "úterý",
    "wednesday": "středa",
    "thursday": "čtvrtek",
    "friday": "pátek",
    "saturday": None,
    "sunday": None,
}
