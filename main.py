#!/usr/local/bin/python3

"""Module for running Lunch bot"""

from src.services.lunch import get_all_menus, send_menus_to_teams


if __name__ == "__main__":
    send_menus_to_teams(get_all_menus())
