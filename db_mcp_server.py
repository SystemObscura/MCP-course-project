import sqlite3
from pathlib import Path
from mcp.server.mcpserver import MCPServer

DB_PATH = Path(__file__).resolve().parent / "shop.db"
mcp = MCPServer("ShopDB")

def _readonly_conn():
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

@mcp.tool()
def list_tables() -> list[str]:
    """Перечислить доступные таблицы базы данных."""
    with _readonly_conn() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    return [r[0] for r in rows]

@mcp.tool()
def describe_table(table_name: str) -> list[dict]:
    """Вернуть схему таблицы: имена и типы полей."""
    allowed = {"products", "orders"}
    if table_name not in allowed:
        raise ValueError(f"Таблица '{table_name}' недоступна")
    with _readonly_conn() as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [{"column": r[1], "type": r[2]} for r in rows]

@mcp.tool()
def query_products(
    max_price: float | None = None,
    category: str | None = None,
    limit: int = 10
) -> list[dict]:
    """Выбрать товары по максимальной цене и/или категории."""
    limit = max(1, min(limit, 50))
    sql = "SELECT name, category, price, stock FROM products WHERE 1=1"
    params: list = []
    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)
    if category is not None:
        sql += " AND category = ?"
        params.append(category)
    sql += " LIMIT ?"
    params.append(limit)
    with _readonly_conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    mcp.run()
