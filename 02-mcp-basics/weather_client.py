"""MCP CLIENT minh hoạ — kết nối tới weather_server.py qua giao thức MCP.

Điểm mấu chốt: client KHÔNG hard-code tool. Nó hỏi server "anh có tool gì?"
(list_tools) tại runtime, rồi gọi tool (call_tool) để SERVER thực thi và trả
kết quả về qua MCP.

Ví dụ này không cần ANTHROPIC_API_KEY — nó cho thấy lớp giao thức MCP hoạt
động độc lập với model. (Trong thực tế, một LLM sẽ dùng Function Calling để
quyết định khi nào gọi tool đã khám phá được.)

Cách chạy (cùng thư mục với weather_server.py, client tự khởi động server):
    pip install -r ../requirements.txt
    python weather_client.py
"""

import asyncio
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    # Dùng đường dẫn tương đối theo file hiện tại để chạy được từ bất kỳ đâu
    server_path = str(Path(__file__).parent / "weather_server.py")
    params = StdioServerParameters(command=sys.executable, args=[server_path])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. KHÁM PHÁ tool mà server công bố (không hard-code)
            tools = await session.list_tools()
            print("Tools server cung cấp:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            # 2. Gọi tool get_weather
            print("\n--- Thử nghiệm get_weather ---")
            for city in ["Hanoi", "Danang", "Haiphong"]:
                result = await session.call_tool("get_weather", {"city": city})
                print(f"call_tool get_weather(city={city!r}):")
                print("  ->", result.content[0].text)

            # 3. Gọi tool get_forecast mới thêm
            print("\n--- Thử nghiệm get_forecast ---")
            forecast_result = await session.call_tool(
                "get_forecast", {"city": "Hanoi", "days": 3}
            )
            print("call_tool get_forecast(city='Hanoi', days=3):")
            print("  ->", forecast_result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
