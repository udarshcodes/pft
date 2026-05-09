CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    currency TEXT DEFAULT 'USD'
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type TEXT CHECK(type IN ('income', 'expense')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, category, month, year)
);
