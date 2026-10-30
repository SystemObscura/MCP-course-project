import asyncio
import sys
from mcp import Client, StdioServerParameters

def unwrap(res):
    sc = res.structured_content
    if sc is not None:
        return sc.get("result", sc)
    return [c.text for c in res.content if getattr(c, "type", None) == "text"]

async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["db_mcp_server.py"],
    )
    async with Client(server_params) as client:
        tables = await client.call_tool("list_tables", {})
        print("Таблицы:", unwrap(tables))

        schema = await client.call_tool(
            "describe_table", {"table_name": "products"})
        print("Схема products:", unwrap(schema))

        result = await client.call_tool(
            "query_products", {"category": "Электроника", "max_price": 5000})
        print("Результат запроса:", unwrap(result))

if __name__ == "__main__":
    asyncio.run(main())
