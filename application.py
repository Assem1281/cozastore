from cs50 import SQL
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify, send_file
from datetime import datetime

import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "thisissecret"

db = SQL("sqlite:///database.db")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "183344657631-0f22frnsat9r790oq95siqj21p61kgu0.apps.googleusercontent.com"
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email", "openid"
    ],
    redirect_uri="http://127.0.0.1:5000/callback")

@app.route("/")
def index():
    shirts = db.execute("SELECT * FROM shirts ORDER BY price")
    shirtsLen = len(shirts)
    # Initialize variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute(
            "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename"
        )
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        shirts = db.execute("SELECT * FROM shirts ORDER BY price ASC")
        shirtsLen = len(shirts)
        return render_template("index.html",
                               shoppingCart=shoppingCart,
                               shirts=shirts,
                               shopLen=shopLen,
                               shirtsLen=shirtsLen,
                               total=total,
                               totItems=totItems,
                               display=display,
                               session=session)
    return render_template("index.html",
                           shirts=shirts,
                           shoppingCart=shoppingCart,
                           shirtsLen=shirtsLen,
                           shopLen=shopLen,
                           total=total,
                           totItems=totItems,
                           display=display)


@app.route("/buy/")
def buy():  
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        # Select info of selected shirt from database
        goods = db.execute("SELECT * FROM shirts WHERE id = :id", id=id)
        # Extract values from selected shirt record
        price = goods[0]["price"]
        samplename = goods[0]["samplename"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        db.execute(
            "INSERT INTO cart (id, qty, samplename, image, price, subTotal) VALUES (:id, :qty, :samplename, :image, :price, :subTotal)",
            id=id,
            qty=qty,
            samplename=samplename,
            image=image,
            price=price,
            subTotal=subTotal)
        shoppingCart = db.execute(
            "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename"
        )
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Select all shirts for home page view
        shirts = db.execute("SELECT * FROM shirts ORDER BY samplename ASC")
        shirtsLen = len(shirts)
        # Go back to home page
        return render_template("index.html",
                               shoppingCart=shoppingCart,
                               shirts=shirts,
                               shopLen=shopLen,
                               shirtsLen=shirtsLen,
                               total=total,
                               totItems=totItems,
                               display=display,
                               session=session)


@app.route("/update/")
def update():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        db.execute("DELETE FROM cart WHERE id = :id", id=id)
        # Select info of selected shirt from database
        goods = db.execute("SELECT * FROM shirts WHERE id = :id", id=id)
        # Extract values from selected shirt record
        price = goods[0]["price"]
        samplename = goods[0]["samplename"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        db.execute(
            "INSERT INTO cart (id, qty, samplename, image, price, subTotal) VALUES (:id, :qty, :samplename, :image, :price, :subTotal)",
            id=id,
            qty=qty,
            samplename=samplename,
            image=image,
            price=price,
            subTotal=subTotal)
        shoppingCart = db.execute(
            "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename"
        )
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Go back to cart page
        return render_template("cart.html",
                               shoppingCart=shoppingCart,
                               shopLen=shopLen,
                               total=total,
                               totItems=totItems,
                               display=display,
                               session=session)


@app.route("/filter/")
def filter():
    if request.args.get('typeClothes'):
        query = request.args.get('typeClothes')
        shirts = db.execute(
            "SELECT * FROM shirts WHERE typeClothes = :query ORDER BY samplename ASC",
            query=query)
    if request.args.get('id'):
        query = int(request.args.get('id'))
        shirts = db.execute(
            "SELECT * FROM shirts WHERE id = :query ORDER BY samplename ASC",
            query=query)
    if request.args.get('kind'):
        query = request.args.get('kind')
        shirts = db.execute(
            "SELECT * FROM shirts WHERE kind = :query ORDER BY samplename ASC",
            query=query)
    shirtsLen = len(shirts)
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        # Rebuild shopping cart
        shoppingCart = db.execute(
            "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename"
        )
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Render filtered view
        return render_template("index.html",
                               shoppingCart=shoppingCart,
                               shirts=shirts,
                               shopLen=shopLen,
                               shirtsLen=shirtsLen,
                               total=total,
                               totItems=totItems,
                               display=display,
                               session=session)
    # Render filtered view
    return render_template("index.html",
                           shirts=shirts,
                           shoppingCart=shoppingCart,
                           shirtsLen=shirtsLen,
                           shopLen=shopLen,
                           total=total,
                           totItems=totItems,
                           display=display)


@app.route("/checkout/")
def checkout():
    order = db.execute("SELECT * from cart")
    # Update purchase history of current customer
    for item in order:
        db.execute(
            "INSERT INTO purchases (uid, id, samplename, image, quantity) VALUES(:uid, :id, :samplename, :image, :quantity)",
            uid=session["uid"],
            id=item["id"],
            samplename=item["samplename"],
            image=item["image"],
            quantity=item["qty"])
    # Clear shopping cart
    db.execute("DELETE from cart")
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Redirect to home page
    return redirect('/')


@app.route("/remove/", methods=["GET"])
def remove():
    # Get the id of shirt selected to be removed
    out = int(request.args.get("id"))
    # Remove shirt from shopping cart
    db.execute("DELETE from cart WHERE id=:id", id=out)
    # Initialize shopping cart variables
    totItems, total, display = 0, 0, 0
    # Rebuild shopping cart
    shoppingCart = db.execute(
        "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename"
    )
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Turn on "remove success" flag
    display = 1
    # Render shopping cart
    return render_template("cart.html",
                           shoppingCart=shoppingCart,
                           shopLen=shopLen,
                           total=total,
                           totItems=totItems,
                           display=display,
                           session=session)


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    # Render log in page
    return render_template("new.html")


@app.route("/logged/", methods=["POST"])
def logged():
    user = request.form["username"].lower()
    pwd = request.form["password"]
    # Make sure form input is not blank and re-render log in page if blank
    if user == "" or pwd == "":
        return render_template("login.html")
    # Find out if info in form matches a record in user database
    query = "SELECT * FROM users WHERE username = :user AND password = :pwd"
    rows = db.execute(query, user=user, pwd=pwd)

    # If username and password match a record in database, set session variables
    if len(rows) == 1:
        session['user'] = user
        session['time'] = datetime.now()
        session['uid'] = rows[0]["id"]
    # Redirect to Home Page
    if 'user' in session:
        return redirect("/")
    # If username is not in the database return the log in page
    return render_template("login.html", msg="Wrong username or password.")


@app.route("/history/")
def history():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all shirts ever bought by current user
    myShirts = db.execute("SELECT * FROM purchases WHERE uid=:uid",
                          uid=session["uid"])
    myShirtsLen = len(myShirts)
    # Render table with shopping history of current user
    return render_template("history.html",
                           shoppingCart=shoppingCart,
                           shopLen=shopLen,
                           total=total,
                           totItems=totItems,
                           display=display,
                           session=session,
                           myShirts=myShirts,
                           myShirtsLen=myShirtsLen)


@app.route("/logout/")
def logout():
    # clear shopping cart
    db.execute("DELETE from cart")
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register/", methods=["POST"])
def registration():
    # Get info from form
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    email = request.form["email"]
    # See if username already in the database
    rows = db.execute("SELECT * FROM users WHERE username = :username ",
                      username=username)
    # If username already exists, alert user
    if len(rows) > 0:
        return render_template("new.html", msg="Username already exists!")
    # If new user, upload info into the users database
    new = db.execute(
        "INSERT INTO users (username, password, email) VALUES (:username, :password, :email)",
        username=username,
        password=password,
        email=email)
    # Render login template
    return render_template("login.html")


@app.route("/cart/")
def cart():
    if 'user' in session:
        # Clear shopping cart variables
        totItems, total, display = 0, 0, 0
        # Grab info currently in database
        shoppingCart = db.execute(
            "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename"
        )
        # Get variable values
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    # Render shopping cart
    return render_template("cart.html",
                           shoppingCart=shoppingCart,
                           shopLen=shopLen,
                           total=total,
                           totItems=totItems,
                           display=display,
                           session=session)


@app.route("/download/")
def download_file():
    file = 'checklist .pdf'
    return send_file(file, as_attachment=True)

@app.route("/logingoogle")
def logingoogle():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(id_token=credentials._id_token,
                                           request=token_request,
                                           audience=GOOGLE_CLIENT_ID)

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/")
