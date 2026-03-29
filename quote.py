import random
import os
import datetime
import json
from datetime import date
import webbrowser
import urllib.parse


def load_quotes(filename='quotes.txt'):
    """Загружает цитаты из файла. Формат: категория|текст цитаты — автор"""
    quotes = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Разделяем категорию и остальное
                if '|' in line:
                    category, content = line.split('|', 1)
                else:
                    category = "Общее"
                    content = line

                # Разделяем текст и автора
                text, author = parse_quote(content)
                quotes.append({
                    'category': category.strip(),
                    'text': text,
                    'author': author
                })
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден")
        print("Создайте файл quotes.txt с цитатами в той же папке")
        return None
    except UnicodeDecodeError:
        print(f"Ошибка: файл {filename} имеет неправильную кодировку")
        print("Сохраните файл в кодировке UTF-8")
        return None

    if not quotes:
        print(f"Ошибка: файл {filename} пуст")
        print("Добавьте цитаты в файл (по одной на строку)")
        return None

    return quotes


def parse_quote(line):
    """Разделяет строку на текст цитаты и автора"""
    separators = [' — ', ' - ']

    for sep in separators:
        if sep in line:
            parts = line.rsplit(sep, 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()

    return line.strip(), "Неизвестен"


def get_categories(quotes):
    """Возвращает список уникальных категорий"""
    categories = set()
    for q in quotes:
        categories.add(q['category'])
    return sorted(categories)


def filter_by_category(quotes, category):
    """Возвращает цитаты только из выбранной категории"""
    if category == "Все":
        return quotes
    return [q for q in quotes if q['category'] == category]


def choose_category(categories):
    """Показывает меню категорий и возвращает выбранную"""
    print("\n" + "=" * 50)
    print("     ВЫБЕРИТЕ КАТЕГОРИЮ")
    print("=" * 50)

    for i, cat in enumerate(categories, start=1):
        print(f"{i}. {cat}")

    print(f"{len(categories) + 1}. Все категории")

    while True:
        try:
            choice = int(input(f"\nВаш выбор (1-{len(categories) + 1}): "))
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
            elif choice == len(categories) + 1:
                return "Все"
            else:
                print(f"Пожалуйста, введите число от 1 до {len(categories) + 1}")
        except ValueError:
            print("Пожалуйста, введите число")


def random_quote(quotes):
    """Возвращает случайную цитату из списка"""
    quote = random.choice(quotes)
    return quote['text'], quote['author']


def format_quote(text, author, total=None):
    """Форматирует цитату для вывода"""
    return f"\"{text}\"\n\t\t\t\t— {author}"


def save_to_favorites(text, author, category, filename='favorites.txt'):
    """Сохраняет цитату в избранное"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n[{timestamp}] [{category}]\n")
        f.write(f"\"{text}\"\n")
        f.write(f"    — {author}\n")
        f.write("-" * 50 + "\n")

    print(f"✅ Цитата сохранена в {filename}")


def show_favorites(filename='favorites.txt'):
    """Показывает все сохранённые цитаты"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            print("📭 Избранное пусто")
            return

        print("\n" + "=" * 50)
        print("     🌟 ИЗБРАННЫЕ ЦИТАТЫ 🌟")
        print("=" * 50)
        print(content)

    except FileNotFoundError:
        print("📭 Избранное пока пусто")


def get_daily_quote(quotes, stats_file='stats.json'):
    """Возвращает цитату дня (одинаковую для одного дня)"""
    today = str(date.today())

    # Загружаем статистику
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats = {"last_date": "", "daily_quote_index": 0, "total_launches": 0}

    # Обновляем счётчик запусков
    stats["total_launches"] = stats.get("total_launches", 0) + 1

    # Если сегодня ещё не показывали цитату
    if stats.get("last_date") != today:
        # Выбираем новую случайную цитату
        stats["last_date"] = today
        stats["daily_quote_index"] = random.randrange(len(quotes))
        # Сохраняем полную строку цитаты
        quote_data = quotes[stats["daily_quote_index"]]
        stats["daily_quote_text"] = f"{quote_data['category']}|{quote_data['text']} — {quote_data['author']}"

        # Сохраняем
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

    # Возвращаем цитату дня
    quote_line = stats["daily_quote_text"]
    if '|' in quote_line:
        _, content = quote_line.split('|', 1)
    else:
        content = quote_line
    text, author = parse_quote(content)
    return text, author, stats["total_launches"]


def show_daily_quote(quotes):
    """Показывает цитату дня при запуске"""
    text, author, launches = get_daily_quote(quotes)

    print("\n" + "=" * 50)
    print("     🌟 ЦИТАТА ДНЯ 🌟")
    print("=" * 50)
    print(f"\n\"{text}\"")
    print(f"    — {author}\n")
    print(f"📊 Запусков сегодня: {launches}")
    print("=" * 50)
    print()


def share_quote(text, author):
    """Предлагает поделиться цитатой"""
    print("\n--- Поделиться цитатой ---")
    print("1. Telegram")
    print("2. WhatsApp")
    print("3. Копировать в буфер обмена")
    print("4. Отмена")

    quote_text = f"«{text}» — {author}"
    quote_encoded = urllib.parse.quote(quote_text)

    while True:
        choice = input("Ваш выбор (1-4): ")

        if choice == '1':
            # Telegram
            url = f"https://t.me/share/url?url={quote_encoded}"
            webbrowser.open(url)
            print("✅ Открыт Telegram. Отправьте сообщение в любой чат.")
            break

        elif choice == '2':
            # WhatsApp
            url = f"https://wa.me/?text={quote_encoded}"
            webbrowser.open(url)
            print("✅ Открыт WhatsApp. Выберите контакт.")
            break

        elif choice == '3':
            # Копировать в буфер обмена
            try:
                import subprocess
                subprocess.run(['clip'], input=quote_text.encode('utf-8'), check=True)
                print("✅ Цитата скопирована в буфер обмена!")
            except:
                print("❌ Не удалось скопировать")
            break

        elif choice == '4':
            print("Отмена")
            break

        else:
            print("Пожалуйста, введите 1-4")


def ask_continue():
    """Спрашивает пользователя, хочет ли он продолжить"""
    while True:
        answer = input('Показать ещё? (y/n): ').lower()
        if answer in ['y', 'yes', 'д', 'да']:
            return True
        elif answer in ['n', 'no', 'н', 'нет']:
            return False
        else:
            print("Пожалуйста, введите y (да) или n (нет)")


def ask_favorite():
    """Спрашивает, сохранить ли цитату в избранное"""
    while True:
        answer = input('Сохранить в избранное? (y/n): ').lower()
        if answer in ['y', 'yes', 'д', 'да']:
            return True
        elif answer in ['n', 'no', 'н', 'нет']:
            return False
        else:
            print("Пожалуйста, введите y (да) или n (нет)")


def ask_share():
    """Спрашивает, хочет ли пользователь поделиться цитатой"""
    while True:
        answer = input('Поделиться цитатой? (y/n): ').lower()
        if answer in ['y', 'yes', 'д', 'да']:
            return True
        elif answer in ['n', 'no', 'н', 'нет']:
            return False
        else:
            print("Пожалуйста, введите y (да) или n (нет)")


def main():
    """Основная функция программы"""
    # Загрузка цитат
    quotes = load_quotes()
    if quotes is None:
        return

    # Показываем цитату дня
    show_daily_quote(quotes)

    # Получаем категории
    categories = get_categories(quotes)
    total_quotes = len(quotes)

    # Приветствие
    print("=" * 50)
    print("     Генератор случайных цитат")
    print("=" * 50)
    print(f"📚 Загружено цитат: {total_quotes}")
    print(f"📂 Категорий: {len(categories)}")

    # Выбор категории
    selected_category = choose_category(categories)

    # Фильтруем цитаты
    filtered_quotes = filter_by_category(quotes, selected_category)

    if selected_category == "Все":
        print(f"\n🎲 Все категории: {len(filtered_quotes)} цитат")
    else:
        print(f"\n📂 Категория '{selected_category}': {len(filtered_quotes)} цитат")

    if not filtered_quotes:
        print("В этой категории нет цитат")
        return

    print()

    # Основной цикл
    while True:
        text, author = random_quote(filtered_quotes)
        print(format_quote(text, author))
        print()

        # Спрашиваем про избранное
        if ask_favorite():
            save_to_favorites(text, author, selected_category)
            print()

        # Спрашиваем про публикацию
        if ask_share():
            share_quote(text, author)
            print()

        if not ask_continue():
            break

    # Показываем избранное в конце
    show_favorites()
    print("\nДо свидания! Хорошего дня!")


if __name__ == "__main__":
    main()