import os
import pytest
from scraper import get_book_data, scrape_books

# Ссылка на тестовую книгу
BOOK_URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

# В каталоге Books to Scrape 50 страниц по 20 книг
EXPECTED_PAGES = 50
EXPECTED_BOOKS = 1000

class TestBookScraper:
    """Тесты  парсинга страниц сайта и его католога"""

    def test_return_keys(self):
        """Проверка возвращаемых ключей"""

        result = get_book_data(BOOK_URL)

        expected_keys = {
            "name", "price", "in_stock", "score", "description",
            "upc", "prod_type", "price_excl_tax", "price_incl_tax",
            "tax", "availabl", "num_reviews",
        }

        assert isinstance(result, dict)
        assert set(result.keys()) == expected_keys

    def test_scraper_known_values(self):
        """Проверка значений результата парсера"""
        result = get_book_data(BOOK_URL)

        assert result["name"] == "A Light in the Attic"
        assert result["price"] == 51.77
        assert result["in_stock"] == 22
        assert result["score"] == 3
        assert result["upc"] == "a897fe39b1053632"
        assert result["prod_type"] == "Books"
        assert result["price_excl_tax"] == 51.77
        assert result["price_incl_tax"] == 51.77
        assert result["num_reviews"] == 0

    def test_full_catalogue_count(self):
        """Обход всего каталога даёт 1000 книг (50 страниц по 20)."""
        books = scrape_books(is_save=False, max_pages=EXPECTED_PAGES)

        assert len(books) == EXPECTED_BOOKS
