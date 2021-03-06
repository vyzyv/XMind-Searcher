#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities used in lookup function."""

import base64
import os
import pathlib
import subprocess
from getpass import getpass

from termcolor import colored


def find_keyword(cursor, keyword: str, color: bool, keep: bool):
    """Find sought keyword in hierarchical database.

    Acts like a menu for finding keywords. Runs until no results can be found
    or user stopped the program using specified key (other than 'y').

    Parameters
    ----------
    cursor : MySQL connector object
           Cursor allowing execution queries to MySQL database
    keyword : str
           Saught for keyword

    """

    def _display_results(cursor):
        """Display branches for found keyword.

        Parameters
        ----------
        cursor : MySQL connector object
               Cursor allowing execution queries to MySQL database

        Returns
        -------
        str
             String containing path pointing to mind map

        """
        # [1:] Does not fetch the root of hierarchical database
        result = list(cursor.stored_results())[0].fetchall()[1:]

        if result:
            # Display indent based branches containing sought keyword
            for indent, branch in enumerate(result):
                print(" " * indent + "{}".format(branch[0]))
            return result[0][0]
        text = "No results found, exiting"
        print(colored(text, "red") if color else text)
        exit(0)

    def maybe_open_mind_map(result):
        text = "\nOpen mind map? \n[Y] yes [ANY] no "
        open_decision = input(colored(text, "blue") if color else text)
        if open_decision.lower() == "y":
            subprocess.call("XMind '{}' >/dev/null 2>&1 &".format(result), shell=True)

    def maybe_next_result():
        text = "\nShow next result? \n[Y] yes [ANY] no "
        next_branch_decision = input(colored(text, "green") if color else text)
        if next_branch_decision != "y":
            exit(0)

    def maybe_clear_screen():
        print()
        if not keep:
            os.system("cls" if os.name == "nt" else "clear")

    # Fetch the best result from database, than the second one, third one
    # afterwards etc.
    BEST_RESULT_ID = 0
    while True:
        cursor.callproc("find_node", [keyword, BEST_RESULT_ID])
        result = _display_results(cursor)
        maybe_open_mind_map(result)
        maybe_next_result()
        maybe_clear_screen()
        BEST_RESULT_ID += 1


def receive_data(
    path: str,
    error_message: str,
    not_found_message: str,
    first_prompt_message: str,
    second_prompt_message: str,
):
    """Return data from file in specified directory.

    Prints error messages if directory was not found or other errors occured

    Parameters
    ----------
    path: str
           Path pointing to secret
    error_message : str
           Error string to print in case of exception
    not_found_message : str
           Error string to print in case file is not present
    first_prompt_message : str
           Message displayed to user when prompting for non-sensitive data
           (first question)
    second_prompt_message : str
           Message displayed to user when prompting for sensitive data
           (second question)

    Returns
    -------
    list
         List containing decrypted/provided data, e.g. [username, password]

    """
    secret = pathlib.Path(os.path.expanduser(path))
    # If secret file exists read it
    if secret:
        try:
            with open(os.path.expanduser(path), "r") as file:
                return [
                    (base64.b64decode(data)).decode("utf-8")
                    for data in file.read().splitlines()
                ]
        # If something went wrong prompt the user to specify their secret
        except Exception:
            print(error_message)
            data1 = input(first_prompt_message)
            data2 = getpass(second_prompt_message)
            return [data1, data2]
    # If secret file not found prompt user to input their secret
    else:
        print(not_found_message)
        data1 = input(first_prompt_message)
        data2 = getpass(second_prompt_message)
        return [data1, data2]
