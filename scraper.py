import os
import time
import requests
import schedule
from bs4 import BeautifulSoup

def get_book_data(book_url: str) -> dict:
    """
    Получает данные о книге со страницы каталога Books to Scrape.

    Загружает HTML-страницу книги, разбирает её с помощью BeautifulSoup
    и возвращает словарь с основной информацией: названием, ценой,
    рейтингом, наличием, описанием и характеристиками из таблицы
    Product Information.

    Args:
        book_url (str): URL страницы книги, например
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    
    Returns:
        dict: Словарь со следующими ключами:
            - "name" (str): название книги;
            - "price" (float): цена с сайта (только число);
            - "in_stock" (int): количество книг в наличии;
            - "score" (int): рейтинг от 0 до 5
              (звёзды переводятся в число, при ошибке — 0);
            - "description" (str): текст описания книги;
            - "upc" (str): уникальный код товара;
            - "prod_type" (str): тип продукции;
            - "price_excl_tax" (float): цена без налогов;
            - "price_incl_tax" (float): цена с налогом;
            - "tax" (float): величина налога;
            - "availabl" (str): строка доступности из таблицы;
            - "num_reviews" (int): количество отзывов.
            Если какое-то поле не найдено на странице, возвращается
            значение по умолчанию из заготовки ("None", 0, 0.0 и т.д.).
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    get_dict = {
        "name": "",
        "price": 0.0,
        "in_stock": 0,
        "score": 0,
        "description": "",
        "upc": "",
        "prod_type": "",
        "price_excl_tax": 0.0,
        "price_incl_tax": 0.0,
        "tax": 0.0,
        "availabl": "",
        "num_reviews": 0
    }

    book_page = requests.get(book_url)
    book_page.encoding = "utf-8"

    soup = BeautifulSoup(book_page.text, "html.parser")

    # Поиск названия книги
    name = soup.find("h1")
    get_dict["name"] = name.string if name else "None"

    # Поиск цены книги
    price = soup.find("p", class_="price_color")
    get_dict["price"] = float(price.string.replace("£", "")) if price else 0.0

    # Поиск кол-ва книг
    in_stock = soup.find("p", class_="instock availability")
    in_stock = in_stock.get_text().replace("\n", "").strip() if in_stock else "None"
    if "In stock" in in_stock:
        get_dict["in_stock"] = int("".join(char for char in in_stock if char.isdigit()))
    else:
        get_dict["in_stock"] = 0

    # Поиск Рейтинга
    score = soup.find("p", class_="star-rating")
    score = score["class"][1] if score else "None"
    match score:
        case "One": score = 1
        case "Two": score = 2
        case "Three": score = 3
        case "Four": score = 4
        case "Five": score = 5
        case _: score = 0
    get_dict["score"] = score

    # Поиск описания
    description = soup.find("div", id = "product_description")
    get_dict["description"] = description.find_next_sibling("p").get_text().strip() if description else "None"

    # Поиск UPC
    upc = soup.find("th", string = "UPC")
    get_dict["upc"] = upc.find_next_sibling("td").get_text().strip() if upc else "None"

    # Поиск Типа продукции
    prod_type = soup.find("th", string = "Product Type")
    get_dict["prod_type"] = prod_type.find_next_sibling("td").get_text().strip() if prod_type else "None"

    # Поиск Цены без налогов
    price_excl_tax = soup.find("th", string = "Price (excl. tax)")
    get_dict["price_excl_tax"] = float(price_excl_tax.find_next_sibling("td").get_text().strip().replace("£", "")) if price_excl_tax else 0.0

    # Поиск Цены с налогом
    price_incl_tax = soup.find("th", string = "Price (incl. tax)")
    get_dict["price_incl_tax"] = float(price_incl_tax.find_next_sibling("td").get_text().strip().replace("£", "")) if price_incl_tax else 0.0

    # Поиск Цены Налогов
    tax = soup.find("th", string = "Tax")
    get_dict["tax"] = float(tax.find_next_sibling("td").get_text().strip().replace("£", "")) if tax else 0.0

    # Поиск Доступности
    availabl = soup.find("th", string = "Availability")
    get_dict["availabl"] = availabl.find_next_sibling("td").get_text().strip() if availabl else "None"

    # Поиск кол-ва обзоров
    num_reviews = soup.find("th", string = "Number of reviews")
    get_dict["num_reviews"] = int(num_reviews.find_next_sibling("td").get_text().strip()) if num_reviews else 0

    # Возвращение словаря
    return get_dict
    # КОНЕЦ ВАШЕГО РЕШЕНИЯ


def scrape_books(is_save: bool = False, max_pages: int = 50) -> list[dict]:
    """
    Проходит по страницам каталога Books to Scrape и собирает данные
    о всех книгах с помощью функции get_book_data.
    
    Args:
        is_save (bool): если True — сохраняет собранные данные
            в файл books_data.txt в текущей папке; иначе пропускает
            шаг сохранения.
        max_pages (int): максимальное количество страниц каталога
            для обхода (по умолчанию 50 — весь каталог).
    
    Returns:
        list[dict]: список словарей с данными по каждой книге
        (структура словаря — результат get_book_data).
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ

    # Список для хранения книг
    all_books = []

    # Цикл в котором идёт итерация по страницам котолога
    for page in range(1, max_pages + 1):
        catolog_page = requests.get(f"https://books.toscrape.com/catalogue/page-{page}.html")
        catolog_page.encoding = "utf-8"

        cat_soup = BeautifulSoup(catolog_page.text, "html.parser")

        # Поиск ссылок на книги
        cat_book_list = cat_soup.find_all("a", title = True)

        # Проверка наличия книг на странице
        if not cat_book_list:
            # Книг на странице нет
            break

        # Цикл в котором идёт итерация по книгам
        for link in cat_book_list:
            # Добавление книги в список
            all_books.append(get_book_data(f"https://books.toscrape.com/catalogue/{link.get("href")}"))

            # Доп ожидание между запросами, для уменьшения нагрузки на сайт
            time.sleep(0.25)

        # Доп ожидание между запросами, для уменьшения нагрузки на сайт
        time.sleep(0.25)

    # Сохранение собранных книг
    if is_save:
        file_path = os.path.join(os.getcwd(), "books_data.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            for book in all_books:
                file.write(f"{book}\n")
        print(f"Данные сохранены в {file_path}")
    
    return all_books

    # КОНЕЦ ВАШЕГО РЕШЕНИЯ


# НАЧАЛО ВАШЕГО РЕШЕНИЯ

def scrape_books_job() -> None:
    """
    Запускает сбор данных о книгах и сохраняет результат в файл.
    """
    
    books = scrape_books(is_save=True)
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} — собрано книг: {len(books)}")

def daily_scheduler() -> None:
    """
    Планирует ежедневный запуск сбора данных в 19:00 и работает
    в бесконечном цикле, проверяя расписание раз в минуту.
    """

    schedule.every().day.at("18:15").do(scrape_books_job)

    print("Планировщик запущен. Ожидаем 19:00 каждый день...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # проверяем расписание раз в минуту

# КОНЕЦ ВАШЕГО РЕШЕНИЯ