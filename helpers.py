from functools import wraps
from flask import render_template, redirect, session
import datetime
 
 
def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
 
 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
 
 
def currency(value):
    symbol_map = {
        "AUD": "A$",
        "CAD": "C$",
        "CHF": "CHF",
        "EUR": "€",
        "GBP": "£",
        "INR": "₹",
        "JPY": "¥",
        "KRW": "₩",
        "NZD": "NZ$",
        "SGD": "S$",
        "USD": "$"
    }
    currency_code = session.get("currency", "USD")
    symbol = symbol_map.get(currency_code, "$")
    return f"{symbol}{value:,.2f}"
 
 
def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None