import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, currency, parse_date
from datetime import datetime

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cs50-fintrack-dev-key-change-in-prod")

app.jinja_env.filters["currency"] = currency

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show user's financial summary and recent transactions"""
    user_id = session["user_id"]
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    currency_symbol = db.execute("SELECT currency FROM users WHERE id = ?", user_id)[0]["currency"]
    session["currency"] = currency_symbol

    incomes_row = db.execute("SELECT SUM(amount) AS total FROM transactions WHERE user_id = ? AND type = 'income'", user_id)
    incomes = incomes_row[0]["total"] if incomes_row and incomes_row[0]["total"] is not None else 0

    expenses_row = db.execute("SELECT SUM(amount) AS total FROM transactions WHERE user_id = ? AND type = 'expense'", user_id)
    expenses = expenses_row[0]["total"] if expenses_row and expenses_row[0]["total"] is not None else 0

    balance = incomes - expenses

    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 5", user_id)

    budgets = db.execute(
        "SELECT category, amount FROM budgets WHERE user_id = ? AND month = ? AND year = ?",
        user_id, current_month, current_year
    )

    budget_data = []
    for budget in budgets:

        spent_row = db.execute(
            "SELECT SUM(amount) AS total FROM transactions WHERE user_id = ? AND category = ? AND type = 'expense' AND strftime('%m', date) = ? AND strftime('%Y', date) = ?",
            user_id, budget["category"], f"{current_month:02d}", str(current_year)
        )
        spent = spent_row[0]["total"] if spent_row and spent_row[0]["total"] is not None else 0

        budget_data.append({
            "category": budget["category"],
            "budgeted": budget["amount"],
            "spent": spent,
            "remaining": budget["amount"] - spent
        })

    return render_template("index.html", balance=balance, transactions=transactions, budgets=budget_data, currency=currency_symbol)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add a new transaction (income or expense)"""
    if request.method == "POST":
        amount_str = request.form.get("amount")
        category = request.form.get("category")
        description = request.form.get("description")
        transaction_type = request.form.get("type")
        date = request.form.get("date")

        if not amount_str or not category or not transaction_type:
            return apology("missing required fields", 400)

        try:
            amount = float(amount_str)
            if amount <= 0:
                return apology("amount must be positive", 400)
        except ValueError:
            return apology("invalid amount", 400)

        db.execute(
            "INSERT INTO transactions (user_id, amount, category, description, type, date) VALUES (?, ?, ?, ?, ?, ?)",
            session["user_id"], amount, category, description, transaction_type, date or datetime.now().strftime("%Y-%m-%d")
        )

        flash("Transaction added!")
        return redirect("/")

    else:

        transactions = db.execute(
            "SELECT category FROM transactions WHERE user_id = ? GROUP BY category", session["user_id"])
        categories = [t["category"] for t in transactions]
        return render_template("add.html", categories=categories)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/transaction/delete", methods=["POST"])
@login_required
def delete_transaction():
    """Delete a transaction"""
    transaction_id = request.form.get("transaction_id")
    user_id = session["user_id"]

    if not transaction_id:
        flash("Invalid request: No transaction ID provided.", "danger")
        return redirect("/history")

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        flash("Invalid transaction ID format.", "danger")
        return redirect("/history")

    rows_affected = db.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        transaction_id, user_id
    )

    if rows_affected > 0:
        flash("Transaction deleted successfully!", "success")
    else:
        flash("Could not delete transaction. It might not exist or you don't have permission.", "danger")

    return redirect("/history")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""


    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        session["currency"] = rows[0]["currency"]

        flash("Logged in successfully!")

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username already exists", 400)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                   username, generate_password_hash(password))

        rows = db.execute("SELECT id, currency FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        session["currency"] = rows[0]["currency"]

        flash("Registered successfully!")
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    user_id = session["user_id"]
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    if request.method == "POST":
        category = request.form.get("category")
        amount_str = request.form.get("amount")

        month_str = request.form.get("month", str(current_month))
        year_str = request.form.get("year", str(current_year))

        if not category or not amount_str:
            flash("Category and amount are required.", "danger")
            return redirect("/budget")

        try:
            amount = float(amount_str)
            if amount <= 0:
                flash("Amount must be a positive number.", "danger")
                return redirect("/budget")
            month = int(month_str)
            year = int(year_str)
        except (ValueError, TypeError):
            flash("Invalid amount, month, or year format.", "danger")
            return redirect("/budget")

        existing_budget = db.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND category = ? AND month = ? AND year = ?",
            user_id, category, month, year
        )

        if existing_budget:

            db.execute(
                "UPDATE budgets SET amount = ? WHERE user_id = ? AND category = ? AND month = ? AND year = ?",
                amount, user_id, category, month, year
            )
            flash("Budget updated successfully!", "success")
        else:

            db.execute(
                "INSERT INTO budgets (user_id, category, amount, month, year) VALUES (?, ?, ?, ?, ?)",
                user_id, category, amount, month, year
            )
            flash("Budget set successfully!", "success")

        return redirect("/budget")

    else:
        budgets = db.execute(
            "SELECT category, amount FROM budgets WHERE user_id = ? AND month = ? AND year = ?",
            user_id, current_month, current_year
        )
        categories = db.execute(
            "SELECT category FROM transactions WHERE user_id = ? GROUP BY category", user_id)
        user_currency = db.execute("SELECT currency FROM users WHERE id = ?", user_id)[0]["currency"]

        return render_template(
            "budget.html",
            budgets=budgets,
            categories=categories,
            currency=user_currency,
            current_month=current_month,
            current_year=current_year
        )

@app.route("/reports")
@login_required
def reports():
    """Generate and display financial reports without charts"""

    user_id = session["user_id"]
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    monthly_data = db.execute(
        """SELECT strftime('%Y-%m', date) AS month,
                  SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income,
                  SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense
           FROM transactions
           WHERE user_id = ?
           GROUP BY strftime('%Y-%m', date)
           ORDER BY month DESC
           LIMIT 12""",
        user_id
    )

    category_data = db.execute(
        """SELECT category, SUM(amount) AS total
           FROM transactions
           WHERE user_id = ? AND type = 'expense'
                 AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
           GROUP BY category
           ORDER BY total DESC""",
        user_id, f"{current_month:02d}", str(current_year)
    )

    return render_template(
        "reports.html",
        monthly_data=monthly_data,
        category_data=category_data
    )



@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    """Allow user to change their password"""
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        flash("All fields are required.", "danger")
        return redirect("/settings")

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect("/settings")

    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    if not user or not check_password_hash(user[0]["hash"], current_password):
        flash("Incorrect current password.", "danger")
        return redirect("/settings")

    db.execute("UPDATE users SET hash = ? WHERE id = ?",
               generate_password_hash(new_password), user_id)
    flash("Password updated successfully!", "success")
    return redirect("/settings")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Manage user settings, e.g., currency"""
    user_id = session["user_id"]

    if request.method == "POST":
        currency_preference = request.form.get("currency")
        if currency_preference:
            db.execute("UPDATE users SET currency = ? WHERE id = ?", currency_preference, user_id)
            session["currency"] = currency_preference
            flash("Settings updated!")
            return redirect("/")
        else:
            flash("Please select a currency.", "warning")
            return redirect("/settings")
    else:
        user = db.execute("SELECT username, currency FROM users WHERE id = ?", user_id)[0]
        return render_template("settings.html", user=user)


@app.route("/budget/delete", methods=["POST"])
@login_required
def delete_budget():
    user_id = session["user_id"]
    category = request.form.get("category")
    month = request.form.get("month")
    year = request.form.get("year")

    if not user_id or not category or not month or not year:
        flash("Invalid request to delete budget (missing parameters).", "danger")
        return redirect("/budget")

    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        flash("Invalid month or year provided for deletion.", "danger")
        return redirect("/budget")

    db.execute(
        "DELETE FROM budgets WHERE user_id = ? AND category = ? AND month = ? AND year = ?",
        user_id, category, month, year
    )
    flash("Budget deleted successfully!", "info")
    return redirect("/budget")


@app.route("/contact")
def contacts():
    """Display contact information (example static page)"""
    return render_template("contact.html")



if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
