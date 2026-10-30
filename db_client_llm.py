import asyncio
import json
import sys
from openai import OpenAI
from mcp import Client, StdioServerParameters

EDEN_API_KEY = ""  # тут вставляется свой API в кавычки
client_llm = OpenAI(
    api_key=EDEN_API_KEY,
    base_url="https://api.edenai.run/v3"
)
MODEL = "google/gemma-4-26b-a4b-it"  # или другой endpoint модели


#преобразование MCP-инструментов в формат OpenAI
def mcp_tools_to_openai(tools):
    result = []
    for tool in tools:
        # MCP-схема аргументов лежит в tool.input_schema
        result.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,  #JSON Schema
            }
        })
    return result


#Основной цикл
async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["db_mcp_server.py"],
    )

    async with Client(server_params) as mcp_client:
        #получаем список инструментов от MCP-сервера
        tools_response = await mcp_client.list_tools()
        openai_tools = mcp_tools_to_openai(tools_response.tools)

        #вопрос пользователя
        print("Введите запрос.. \n")
        user_question = input()
        messages = [{"role": "user", "content": user_question}]

        #цикл LLM -> tool call -> MCP -> LLM -> ...
        while True:
            response = client_llm.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",  #LLM сама решает, вызвать ли инструмент
            )
            msg = response.choices[0].message
            messages.append(msg)  #добавляем ответ LLM в историю

            #если инструментов не вызвано - выходим и печатаем ответ
            if not msg.tool_calls:
                print("\nФинальный ответ LLM:")
                print(msg.content)
                break

            #выполняем каждый tool call через MCP
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"\nLLM решила вызвать: {name}({args})")

                result = await mcp_client.call_tool(name, args)

                #отправляем результат обратно в LLM
                #structured_content может быть None или {"result": ...}
                sc = result.structured_content
                if sc is not None:
                    content = json.dumps(sc.get("result", sc), ensure_ascii=False)
                else:
                    content = json.dumps(
                        [c.text for c in result.content if getattr(c, "type", None) == "text"],
                        ensure_ascii=False
                    )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": content,
                })


if __name__ == "__main__":
    asyncio.run(main())
