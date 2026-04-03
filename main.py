import sqlite3
import random
import uuid
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Quote Generator API", description="Генератор случайных цитат с избранным", version="2.0.0")


# ----- Модели данных -----
class FavoriteAdd(BaseModel):
    quote_id: int
    session_id: str


class FavoriteDelete(BaseModel):
    favorite_id: int
    session_id: str


# ----- Вспомогательные функции -----
def get_db_connection():
    conn = sqlite3.connect("quotes.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_random_quote(category: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if category:
        cursor.execute("SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT 1", (category,))
    else:
        cursor.execute("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1")

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_quote_by_id(quote_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM quotes ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    return [row["category"] for row in rows]


def get_quotes_by_category(category: str, limit: int = 20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, author FROM quotes WHERE category = ? LIMIT ?", (category, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ----- Работа с избранным -----
def add_favorite(quote_id: int, session_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM favorites WHERE quote_id = ? AND session_id = ?", (quote_id, session_id))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute("INSERT INTO favorites (quote_id, session_id) VALUES (?, ?)", (quote_id, session_id))
    conn.commit()
    conn.close()
    return True


def remove_favorite(favorite_id: int, session_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE id = ? AND session_id = ?", (favorite_id, session_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_favorites(session_id: str, limit: int = 50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT f.id as favorite_id, f.created_at, q.id, q.text, q.author, q.category
                   FROM favorites f
                            JOIN quotes q ON f.quote_id = q.id
                   WHERE f.session_id = ?
                   ORDER BY f.created_at DESC LIMIT ?
                   """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()

    return [{
        "favorite_id": row["favorite_id"],
        "quote_id": row["id"],
        "text": row["text"],
        "author": row["author"],
        "category": row["category"],
        "saved_at": row["created_at"]
    } for row in rows]


def is_favorite(quote_id: int, session_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM favorites WHERE quote_id = ? AND session_id = ?", (quote_id, session_id))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


# ----- Эндпоинты API -----

@app.get("/")
def root():
    return {"message": "Quote Generator API", "docs": "/docs", "frontend": "/frontend"}


@app.get("/frontend", response_class=HTMLResponse)
def frontend():
    """Полноценный фронтенд с избранным"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Генератор цитат</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            .quote { background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; margin: 5px; }
            select, input { padding: 5px; margin: 10px 0; }
            .nav-buttons { margin: 20px 0; }
            .quote-list { list-style: none; padding: 0; }
            .quote-list li { background: #e0e0e0; margin: 10px 0; padding: 15px; border-radius: 8px; }
            hr { margin: 30px 0; }
        </style>
    </head>
    <body>
        <h1>📖 Генератор цитат</h1>

        <div class="nav-buttons">
            <button onclick="showRandomTab()">🎲 Случайная цитата</button>
            <button onclick="showFavoritesTab()">⭐ Избранное</button>
        </div>

        <div id="randomTab">
            <div>
                <label>Категория: </label>
                <select id="category">
                    <option value="">Все категории</option>
                </select>
                <button onclick="getQuote()">Показать случайную цитату</button>
            </div>

            <div class="quote" id="quoteArea">
                <p id="quoteText">Нажмите кнопку, чтобы получить цитату</p>
                <p id="quoteAuthor" style="color: gray;"></p>
                <p id="quoteCategory" style="color: gray; font-size: 0.9em;"></p>
                <button id="favoriteBtn" onclick="saveToFavorites()" style="display:none;">⭐ В избранное</button>
            </div>
        </div>

        <div id="favoritesTab" style="display:none;">
            <h2>⭐ Избранные цитаты</h2>
            <div id="favoritesList">Загрузка...</div>
        </div>

        <script>
            let sessionId = localStorage.getItem('quote_session_id');
            if (!sessionId) {
                sessionId = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
                localStorage.setItem('quote_session_id', sessionId);
            }

            let currentQuote = null;

            // Загружаем категории
            fetch('/categories')
                .then(res => res.json())
                .then(data => {
                    const select = document.getElementById('category');
                    data.categories.forEach(cat => {
                        const option = document.createElement('option');
                        option.value = cat;
                        option.textContent = cat;
                        select.appendChild(option);
                    });
                });

            function showRandomTab() {
                document.getElementById('randomTab').style.display = 'block';
                document.getElementById('favoritesTab').style.display = 'none';
            }

            function showFavoritesTab() {
                document.getElementById('randomTab').style.display = 'none';
                document.getElementById('favoritesTab').style.display = 'block';
                loadFavorites();
            }

            function getQuote() {
                const category = document.getElementById('category').value;
                let url = '/quote/random';
                if (category) {
                    url += `?category=${encodeURIComponent(category)}`;
                }

                fetch(url)
                    .then(res => res.json())
                    .then(data => {
                        if (data.error) {
                            document.getElementById('quoteText').innerHTML = data.error;
                            return;
                        }
                        currentQuote = data;
                        document.getElementById('quoteText').innerHTML = `&ldquo;${data.text}&rdquo;`;
                        document.getElementById('quoteAuthor').innerHTML = `— ${data.author}`;
                        document.getElementById('quoteCategory').innerHTML = `📂 ${data.category}`;

                        fetch(`/favorites/check/${data.id}/${sessionId}`)
                            .then(res => res.json())
                            .then(check => {
                                const btn = document.getElementById('favoriteBtn');
                                if (check.is_favorite) {
                                    btn.textContent = '✔ В избранном';
                                    btn.disabled = true;
                                } else {
                                    btn.textContent = '⭐ В избранное';
                                    btn.disabled = false;
                                }
                                btn.style.display = 'inline-block';
                            });
                    })
                    .catch(err => {
                        document.getElementById('quoteText').innerHTML = 'Ошибка загрузки цитаты';
                        console.error(err);
                    });
            }

            function saveToFavorites() {
                if (!currentQuote) return;

                fetch('/favorites/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        quote_id: currentQuote.id,
                        session_id: sessionId
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('Цитата добавлена в избранное!');
                        getQuote();
                    } else {
                        alert(data.message);
                    }
                });
            }

            function loadFavorites() {
                fetch(`/favorites/${sessionId}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.count === 0) {
                            document.getElementById('favoritesList').innerHTML = '<p>Нет избранных цитат. Добавьте понравившиеся!</p>';
                            return;
                        }

                        let html = '<ul class="quote-list">';
                        data.favorites.forEach(fav => {
                            html += `
                                <li>
                                    <p>&ldquo;${fav.text}&rdquo;</p>
                                    <p>— ${fav.author} <span style="color:gray">(${fav.category})</span></p>
                                    <small>Добавлено: ${new Date(fav.saved_at).toLocaleString()}</small>
                                    <br>
                                    <button onclick="removeFavorite(${fav.favorite_id})">🗑 Удалить</button>
                                </li>
                            `;
                        });
                        html += '</ul>';
                        document.getElementById('favoritesList').innerHTML = html;
                    });
            }

            function removeFavorite(favoriteId) {
                fetch('/favorites/remove', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        favorite_id: favoriteId,
                        session_id: sessionId
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        loadFavorites();
                    } else {
                        alert(data.message);
                    }
                });
            }

            getQuote();
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/categories")
def categories():
    return {"categories": get_categories()}


@app.get("/quote/random")
def random_quote(category: Optional[str] = Query(None, description="Категория цитаты")):
    quote = get_random_quote(category)
    if not quote:
        return {"error": "Цитата не найдена"}
    return {
        "id": quote["id"],
        "text": quote["text"],
        "author": quote["author"],
        "category": quote["category"]
    }


@app.get("/quote/{quote_id}")
def quote_by_id(quote_id: int):
    quote = get_quote_by_id(quote_id)
    if not quote:
        return {"error": f"Цитата с id={quote_id} не найдена"}
    return {
        "id": quote["id"],
        "text": quote["text"],
        "author": quote["author"],
        "category": quote["category"]
    }


@app.get("/quotes/{category}")
def quotes_by_category(category: str, limit: int = Query(20, ge=1, le=100)):
    quotes = get_quotes_by_category(category, limit)
    if not quotes:
        return {"error": f"Категория '{category}' не найдена или пуста"}
    return {
        "category": category,
        "count": len(quotes),
        "quotes": quotes
    }


@app.get("/stats")
def stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM quotes GROUP BY category ORDER BY category")
    stats = [{"category": row["category"], "count": row["count"]} for row in cursor.fetchall()]
    cursor.execute("SELECT COUNT(*) as total FROM quotes")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total_favorites FROM favorites")
    total_fav = cursor.fetchone()["total_favorites"]
    conn.close()

    return {"total_quotes": total, "total_favorites": total_fav, "by_category": stats}


# ----- Эндпоинты избранного -----

@app.post("/favorites/add")
def add_favorite_endpoint(fav: FavoriteAdd):
    quote = get_quote_by_id(fav.quote_id)
    if not quote:
        return {"error": f"Цитата с id={fav.quote_id} не найдена"}

    success = add_favorite(fav.quote_id, fav.session_id)
    if success:
        return {"success": True, "message": "Цитата добавлена в избранное"}
    else:
        return {"success": False, "message": "Цитата уже в избранном"}


@app.post("/favorites/remove")
def remove_favorite_endpoint(fav: FavoriteDelete):
    success = remove_favorite(fav.favorite_id, fav.session_id)
    if success:
        return {"success": True, "message": "Цитата удалена из избранного"}
    else:
        return {"success": False, "message": "Цитата не найдена или нет прав"}


@app.get("/favorites/{session_id}")
def get_favorites_endpoint(session_id: str, limit: int = 50):
    favorites = get_favorites(session_id, limit)
    return {"session_id": session_id, "count": len(favorites), "favorites": favorites}


@app.get("/favorites/check/{quote_id}/{session_id}")
def check_favorite(quote_id: int, session_id: str):
    favorite = is_favorite(quote_id, session_id)
    return {"quote_id": quote_id, "is_favorite": favorite}