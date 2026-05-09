# FinTrack — Personal Finance Tracker

**Live Demo:** [fintrack-iudq.onrender.com](https://fintrack-iudq.onrender.com)

## About

FinTrack was originally built inside Harvard's CS50x virtual codespace as my final project submission. I'm now making it public with some UI improvements — cleaner dark theme, better typography, and a more polished layout. The core logic and functionality are unchanged from the original submission.

It's not trying to compete with Walnut or ET Money. It's a technical exercise in building something end to end: from schema design and auth to deployment.

## Features

**Authentication** — Register, login, logout with hashed passwords (Werkzeug)

**Transactions** — Add income or expense entries with category, description, and date

**Budget Tracking** — Set monthly budgets per category; see remaining vs spent in real time

**Transaction History** — View and delete all past transactions

**Financial Reports** — Monthly income vs expense summary + top expense categories

**Multi-currency** — Supports USD, INR, EUR, GBP, JPY, and more

**Settings** — Change password and currency preference

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite (via cs50 library) |
| Auth | Werkzeug password hashing, Flask-Session |
| Frontend | Jinja2, Bootstrap 5, custom CSS |
| Deployment | Render (gunicorn) |

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/udarshcodes/pft.git
cd pft
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create the database**
```bash
python create_db.py
```

**4. Run the app**
```bash
python app.py
```

Visit `http://127.0.0.1:5000`

## Project Structure

```
pft/
├── app.py              # All Flask routes and business logic
├── helpers.py          # Auth decorator, currency filter, date parser
├── create_db.py        # Database initialisation script
├── schema.sql          # SQLite schema (users, transactions, budgets)
├── requirements.txt
├── Procfile            # For Render deployment
├── static/
│   ├── styles.css      # Custom dark theme
│   └── scripts.js
└── templates/
    ├── layout.html     # Base template
    ├── index.html      # Dashboard
    ├── add.html        # Add transaction
    ├── history.html    # Transaction history
    ├── budget.html     # Budget management
    ├── reports.html    # Financial reports
    ├── settings.html   # User settings
    ├── login.html
    ├── register.html
    ├── contact.html
    └── apology.html
```

## A Note on the UI

The original submission used default Bootstrap styling. The public version uses a custom dark theme inspired by fintech dashboards — DM Sans + Syne fonts, glassmorphism cards, and a consistent design system. No functionality was changed.

## What I Learned

Designing a relational database schema from scratch

Session-based authentication and password hashing

Flask routing, Jinja2 templating, and custom filters

Writing SQL aggregate queries for reports and budget tracking

Deploying a Python web app to production with gunicorn and Render

## Author

**Udarsh Goyal** 
[GitHub](https://github.com/udarshcodes) · [Portfolio](https://udarshcodes.github.io/personal_portfolio/) · [LinkedIn](https://www.linkedin.com/in/udarshgoyal-256095383)


*CS50x Final Project — Harvard University, 2025*
