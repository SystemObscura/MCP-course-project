"""
Генерирует файл shop.db с таблицами products и orders.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "shop.db"
#генерирует в той же папке где seed

#пересоздаём базу с нуля, чтобы повторный запуск не плодил дубли,
if DB_PATH.exists():
    DB_PATH.unlink() #удаляется прошлый экземпляр

#соединяет с файлом бд БЕЗ read only
conn = sqlite3.connect(DB_PATH)
#создание схемы в два запроса
conn.executescript("""
CREATE TABLE products (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    category TEXT    NOT NULL,
    price    REAL    NOT NULL CHECK (price > 0),
    stock    INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    order_date TEXT    NOT NULL
);
""")

products = [
    #название товара,           категория,   цена,  в наличии
    ("Наушники беспроводные", "Электроника", 2999.0, 15),
    ("Смартфон 6.5\"",         "Электроника", 18990.0, 8),
    ("Powerbank 20000 mAh",   "Электроника", 1990.0, 32),
    ("USB-C кабель 2 м",       "Электроника", 490.0,  120),
    ("Умная колонка",         "Электроника", 4990.0, 6),
    ("Рюкзак городской 20 л",  "Аксессуары",  2500.0, 40),
    ("Чехол для смартфона",    "Аксессуары",  790.0,  75),
    ("Защитное стекло",        "Аксессуары",  350.0,  200),
    ("Кофеварка капсульная",   "Бытовая техника", 6990.0, 10),
    ("Блендер 600 Вт",         "Бытовая техника", 3490.0, 12),
    ("Микроволновка 20 л",     "Бытовая техника", 5490.0, 5),
    ("Электрочайник 1.7 л",    "Бытовая техника", 1290.0, 25),
    ("Книга «Python для чайников»", "Книги",     1490.0, 18),
    ("Книга «Алгоритмы»",      "Книги",      2290.0, 9),
    ("Книга «Чистый код»",     "Книги",      1890.0, 14),
]

#выполняет insert для каждого кортежа в списке
conn.executemany( #id само проставит sqlite,        плейсхолдеры v  v  v  v
    "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
    products,
)

#несколько заказов по id товаров, их количество, дата
orders = [ 
    (1, 2, "2026-09-15"),
    (1, 1, "2026-09-20"),
    (3, 5, "2026-09-22"),
    (2, 1, "2026-10-01"),
    (5, 2, "2026-10-03"),
    (4, 10, "2026-10-07"),
    (9, 1, "2026-10-12"),
    (12, 3, "2026-10-15"),
    (13, 2, "2026-10-18"),
    (10, 1, "2026-10-20"),
]
conn.executemany(
    "INSERT INTO orders (product_id, quantity, order_date) VALUES (?, ?, ?)",
    orders,
)

conn.execute("PRAGMA foreign_keys = ON") #ссылочная целостность вкл
conn.commit() #фиксация на диск

#короткий отчёт для наглядности,   берёт число из первой строки кортёжа
n_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
n_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
conn.close()

print(f"Готово: {DB_PATH}")
print(f"  products: {n_products} строк")
print(f"  orders:   {n_orders} строк")
