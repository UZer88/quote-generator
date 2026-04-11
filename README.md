[![CI](https://github.com/UZer88/quote-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/UZer88/quote-generator/actions/workflows/ci.yml)

# Генератор случайных цитат

Веб-приложение для просмотра вдохновляющих цитат с категориями, избранным и статистикой. Бэкенд на FastAPI, фронтенд на чистом HTML/CSS/JS.

## Возможности

- 📖 **7 категорий**: Мотивация, Мудрость, Успех, Жизнь, Творчество, Любовь, Юмор
- 🎲 **Случайная цитата** (из всех категорий или выбранной)
- ⭐ **Избранное** — сохранение понравившихся цитат (привязка к session_id в localStorage)
- 📊 **Статистика** — количество цитат по категориям и общее число избранных
- 🌐 **Веб-интерфейс** — удобная страница с двумя вкладками
- 📱 **Адаптивный дизайн** — работает на компьютерах и телефонах
- 🔌 **REST API** — все возможности доступны через API

## Технологии

- **Backend**: FastAPI, Python 3.8+
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (без фреймворков)

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/UZer88/quote-generator.git
cd quote-generator
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Установите зависимости
```bash
pip install fastapi uvicorn
```

4. Создайте базу данных и импортируйте цитаты
```bash
python migrate.py
```

5. Добавьте таблицу избранного
```bash
python add_favorites_table.py
```

6. Запустите сервер
```bash
uvicorn main:app --reload
```

7. Откройте в браузере

http://localhost:8000/frontend

## Автор
UZer88

## Лицензия
MIT