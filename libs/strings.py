"""
libs.strings

By default, uses `en-gb.json` file inside the `strings` top-level folder.

If language changes, set `libs.strings.default_locale` and run `libs.strings.refresh()`.

Caching is temporarily storing a piece of data that is being used multiple times, so it doesn't need to be
regenerated or retrieved many times

Babel in python is a translation library used for handling internalization with not only languages being handled but
dates etc
"""
import json

default_locale = "en-gb"
cached_strings = {}


def refresh():
    print("Refreshing...")
    global cached_strings
    with open(f"strings/{default_locale}.json") as f:
        cached_strings = json.load(f)


def gettext(name):
    return cached_strings[name]


# def set_default_locale(locale):
#     global default_locale
#     default_locale = locale


refresh()
