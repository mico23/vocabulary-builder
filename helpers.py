# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import requests
import json

import os
import re

import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        # looping a tuple

        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(word):
    """Look up quote for word."""

    # Contact API
    try:
        app_id = 'd94407af'
        app_key = '' #Oxford Dictionary API Key
        language = 'en'
        word_id = word
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/'  + language + '/'  + word_id.lower()
        response = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})
    except requests.RequestException:
        return None

    # Parse response
    # To revise the code
    try:
        # print("code {}\n".format(r.status_code))
        # print("text \n" + r.text)
        # what is .dumps for?
        # print("json \n" + json.dumps(r.json()["results"][0]["id"]))
        # return render_template("layout.html", word = json.dumps(r.json()["results"][0]["id"]))

        result = response.json()
        return result
        '''
        return {
            "word": None,
            "definition": None,
            "example": None
        }
        '''
    except (KeyError, TypeError, ValueError):
        return None
