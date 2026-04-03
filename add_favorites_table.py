import sqlite3

conn = sqlite3.connect("quotes.db")
cursor = conn.cursor()

# Создаём таблицу избранного
cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quote_id) REFERENCES quotes (id)
)
""")

# Создаём индекс для быстрого поиска по session_id
cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_session ON favorites(session_id)")

conn.commit()
conn.close()

print("Таблица 'favorites' создана")