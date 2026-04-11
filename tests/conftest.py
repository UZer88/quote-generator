# tests/conftest.py
import sys
from pathlib import Path

# Добавляем корневую папку проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app, init_db

# Инициализируем БД ДО того, как тесты начнутся
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Создаёт БД и таблицы перед запуском всех тестов"""
    init_db()
    # Также можно импортировать цитаты из quotes.txt
    from migrate import import_quotes_from_txt
    import_quotes_from_txt()


@pytest.fixture
def client():
    return TestClient(app)