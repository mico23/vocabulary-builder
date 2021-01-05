import requests
from flask import redirect, render_template, session
from functools import wraps


# EFFECTS: render error page
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


# EFFECTS: Decorate routes to require login
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


# EFFECTS: search a word via Oxford Dictionary API
def lookup(word):
    # Contact API
    try:
        app_id = 'd94407af'
        # Oxford Dictionary API Key
        app_key = ''
        language = 'en'
        word_id = word
        url = 'https://od-api.oxforddictionaries.com/api/v2/entries/' + language + '/' + word_id.lower()
        response = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
    except requests.RequestException:
        return None

    # Parse response
    try:
        result = response.json()
        return result

    except (KeyError, TypeError, ValueError):
        return None


# EFFECTS: format and return the list of words
def form_word_list(words):
    word_list = "<ul class='list-group list-group-flush'>"
    for word in words:
        word_list = word_list + "<li class='list-group-item'>" + word + "</li>"
    word_list = word_list + "</ul>"
    return word_list
