import sqlite3
import re

# Подключаемся к БД (создаст файл quotes.db)
conn = sqlite3.connect("quotes.db")
cursor = conn.cursor()

# Создаём таблицу цитат
cursor.execute("""
               CREATE TABLE IF NOT EXISTS quotes
               (
                   id
                   INTEGER
                   PRIMARY
                   KEY
                   AUTOINCREMENT,
                   category
                   TEXT
                   NOT
                   NULL,
                   text
                   TEXT
                   NOT
                   NULL,
                   author
                   TEXT,
                   created_at
                   TIMESTAMP
                   DEFAULT
                   CURRENT_TIMESTAMP
               )
               """)


def parse_quote_line(line):
    """Разбирает строку формата: категория|текст — автор"""
    line = line.strip()
    if not line or "|" not in line:
        return None, None, None

    # Разделяем категорию и остальное
    category, rest = line.split("|", 1)
    category = category.strip()

    # Ищем разделитель " — " (пробел, два дефиса, пробел)
    if " — " in rest:
        text, author = rest.rsplit(" — ", 1)
        text = text.strip()
        author = author.strip()
    else:
        text = rest.strip()
        author = "Неизвестен"

    return category, text, author


def import_quotes_from_txt(filename="quotes.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        category, text, author = parse_quote_line(line)
        if category is None:
            continue

        cursor.execute("""
                       INSERT INTO quotes (category, text, author)
                       VALUES (?, ?, ?)
                       """, (category, text, author))
        count += 1

    conn.commit()
    print(f"Импортировано {count} цитат")


def show_stats():
    cursor.execute("SELECT category, COUNT(*) FROM quotes GROUP BY category ORDER BY category")
    stats = cursor.fetchall()
    print("\n--- Статистика по категориям ---")
    for cat, cnt in stats:
        print(f"{cat}: {cnt} цитат")

    cursor.execute("SELECT COUNT(*) FROM quotes")
    total = cursor.fetchone()[0]
    print(f"\nВсего цитат: {total}")


if __name__ == "__main__":
    import_quotes_from_txt()
    show_stats()
    conn.close()