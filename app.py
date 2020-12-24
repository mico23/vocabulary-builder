import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, jsonify, flash, redirect, render_template, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///vocabulary.db")

# TO-DO: consider to set up a reminder for user to review the words
# TO-DO: consider to add weather forecast performance
# TO-DO: consider to add "word-of-day"

# EFFECTS: render login page
@app.route("/")
@login_required
def index():
    words = db.execute("SELECT word FROM vocabulary WHERE user_id=:id", id=session["user_id"])
    words = [item["word"] for item in words]
    word_list = "<ul class='list-group list-group-flush'>"
    for word in words:
        word_list = word_list + "<li class='list-group-item'>" + word + "</li>"
    word_list = word_list + "</ul>"
    return render_template("index.html", today_date = datetime.date(datetime.now()),
                            result="please entre your word", word_list = word_list, word_count=len(words))

# EFFECTS: render the word search result
@app.route("/result", methods=["GET", "POST"])
@login_required
def result():
    # has to use JS to partially update the page.
    word = request.form["word_search"]

    if not word:
        return render_template("result.html", word="Please entre a word")
    else:
        try:
            result = lookup(word)
            return render_template("result.html", word=result["results"][0]['id'],
                                    meaning=result["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0],
                                    add_button="<input class='btn btn-outline-primary btn-sm' type='button' value='Add Word' onClick='addWord()'/>")
        except:
            return render_template("result.html", word="The word you entred does not exist. Please try again.")

# EFFECTS: add a word to the vobcabulary list
@app.route("/add_word", methods=["GET", "POST"])
@login_required
def add_word():
    add_word = request.form["add_word"]
    words = db.execute("SELECT word FROM vocabulary WHERE user_id=:id", id=session["user_id"])
    words = [item["word"] for item in words]

    if result not in words:
        db.execute("INSERT INTO vocabulary (word, user_id) VALUES (:word, :id)", word=add_word, id=session["user_id"])
        words = db.execute("SELECT word FROM vocabulary WHERE user_id=:id", id=session["user_id"])
        words = [item["word"] for item in words]
        word_list = "<ul class='list-group list-group-flush'>"
        for word in words:
            word_list = word_list + "<li class='list-group-item'>" + word + "</li>"
        word_list = word_list + "</ul>"

        return word_list

    else:
        words = db.execute("SELECT word FROM vocabulary WHERE user_id=:id", id=session["user_id"])
        words = [item["word"] for item in words]
        word_list = "<ul class='list-group list-group-flush'>"
        for word in words:
            word_list = word_list + "<li class='list-group-item'>" + word + "</li>"
        word_list = word_list + "</ul>"

        return word_list

# EFFECTS: render the quiz page
@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    words = db.execute("SELECT * FROM (SELECT * FROM 'vocabulary' WHERE user_id = :id ORDER BY (correct_times/test_taken) LIMIT 5) AS T ORDER BY last_update",
                        id=session["user_id"])
    words = [item["word"] for item in words]

    total_words = len(words)

    return render_template("quiz.html", total_words=total_words)

# EFFECTS: render the question section
@app.route("/question", methods=["GET", "POST"])
@login_required
def question():
    words = db.execute("SELECT * FROM (SELECT * FROM 'vocabulary' WHERE user_id = :id ORDER BY (correct_times/test_taken) LIMIT 5) AS T ORDER BY last_update",
                        id=session["user_id"])
    words = [item["word"] for item in words]

    total_words = len(words)

    try:
        result = lookup(words[0])
        word_meaning =result["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]
    except:
        word_meaning = "ERROR. The meaing of the word cannot be retrieved."
    return render_template("question.html", word_meaning=word_meaning, words=words, total_words=total_words)

# EFFECTS: check answer provided by the user in a quiz
@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    answer = request.form["answer"]
    words = request.form["wordList"].split(',')
    step = int(request.form["currentStep"])
    word = words[step]

    if answer == word:
        db.execute("UPDATE vocabulary SET correct_times = correct_times + 1, test_taken = test_taken + 1 WHERE user_id = :id AND word=:word",
                               id=session["user_id"], word=word)
    else:
        db.execute("UPDATE vocabulary SET correct_times = correct_times + 0, test_taken = test_taken + 1 WHERE user_id = :id AND word=:word",
                               id=session["user_id"], word=word)

    step += 1

    if step < len(words):
        word = words[step]
        print(word)

        try:
            result = lookup(word)
            word_meaning = result["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]
        except:
            word_meaning = "ERROR. The meaing of the word cannot be retrieved."
        return word_meaning
    else:
        word_meaning = "Quiz completed!"
        return render_template("finish.html")

# EFFECTS: render registration page and resigter a user
#          return errors if inputs are invalid
# TODO refactor some code here
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        usernames = db.execute("SELECT username FROM Users")
        usernames = [name['username'] for name in usernames]
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate Username
        if (username in usernames) or (not username):
            return apology("invalid username, please try another", 400)

        # Validate Password
        elif password != confirmation or not password or not confirmation:
            return apology("invalid password", 400)

        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            # Cannot pass an assigned variable as an argument - e.g. username
            # Need to assign the value to the "variable" as the arugment - e.g. username = request.form.get("username")
            db.execute("INSERT INTO users (username, hash) VALUES(:username, :password)",
                       username=request.form.get("username"), password=hashed_password)

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect the user to the index page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

# EFFCTS: process user login
#         return errors if the user provides invalid inputs
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# EFFECTS: logout user
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")