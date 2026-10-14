"""MCP SERVER minh hoạ — công bố tool `get_weather` qua giao thức MCP.

Khác với function calling: tool nằm ở một server ĐỘC LẬP. Server tự "khai
báo" tool của mình; bất kỳ MCP client nào (Claude Code, Claude Desktop,
Cursor, hoặc weather_client.py) cũng cắm vào dùng được mà không cần biết
code bên trong.

Schema của tool được TỰ ĐỘNG sinh ra từ type hints + docstring.

Chạy trực tiếp:
    pip install -r ../requirements.txt
    python weather_server.py

Đăng ký với Claude Code (làm 1 lần, dùng mãi):
    claude mcp add weather -- python /đường/dẫn/tới/weather_server.py
"""

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("weather")

_MOCK_DB = {
    "Hanoi": "29°C, trời mưa",
    "Haiphong": "33°C, mưa rào",
    "Danang": "30°C, nhiều mây",
}

_MOCK_FORECAST = {
    "Hanoi": [
        "Ngày mai: 28°C - 32°C, nắng gián đoạn",
        "Ngày kia: 27°C - 31°C, mưa rào rải rác",
        "3 ngày tới: 26°C - 30°C, trời nhiều mây",
    ],
    "Haiphong": [
        "Ngày mai: 27°C - 31°C, nhiều gió, có mưa",
        "Ngày kia: 26°C - 30°C, mưa nhẹ",
        "3 ngày tới: 27°C - 32°C, trời hửng nắng",
    ],
    "Danang": [
        "Ngày mai: 27°C - 33°C, nắng đẹp",
        "Ngày kia: 26°C - 32°C, ít mây",
        "3 ngày tới: 27°C - 31°C, có lúc mưa nhỏ",
    ],
}


@mcp.tool()
def get_weather(city: str) -> str:
    """Lấy thời tiết hiện tại của một thành phố."""
    return f"{city}: {_MOCK_DB.get(city, '28°C, không có dữ liệu chi tiết')}"


@mcp.tool()
def get_forecast(city: str, days: int = 3) -> str:
    """Lấy dự báo thời tiết cho các ngày tới của một thành phố."""
    forecasts = _MOCK_FORECAST.get(
        city,
        [f"Ngày +{i+1}: 28°C, có mây" for i in range(days)],
    )[:days]
    details = "\n  * ".join(forecasts)
    return f"Dự báo thời tiết {city} ({days} ngày tới):\n  * {details}"


if __name__ == "__main__":
    mcp.run()  # mặc định chạy qua stdio
