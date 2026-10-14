"""Minh hoạ FUNCTION CALLING thuần với Google Gemini SDK.

Tool `get_weather` được định nghĩa schema thủ công VÀ thực thi ngay trong
chính file app này. Model chỉ QUYẾT ĐỊNH gọi tool nào; app mới là nơi chạy.

Cách chạy:
    pip install -r ../requirements.txt
    export GEMINI_API_KEY=...
    python weather_function_calling.py
"""

import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from google import genai
from google.genai import types

client = genai.Client()

MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = (
    "Bạn là trợ lý thời tiết thân thiện, trả lời bằng tiếng Việt tự nhiên. "
    "Dùng emoji phù hợp (🌧️ 🌤️ 💨 💧). "
    "Tóm tắt ngắn gọn, dễ hiểu, và đưa ra lời khuyên thực tế "
    "(ví dụ: mang ô, mặc áo mỏng, ...)."
)

# 1. App tự định nghĩa schema của các tool
get_weather_declaration = types.FunctionDeclaration(
    name="get_weather",
    description="Lấy thời tiết hiện tại của một thành phố",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "city": types.Schema(
                type=types.Type.STRING, description="Tên thành phố"
            )
        },
        required=["city"],
    ),
)

get_forecast_declaration = types.FunctionDeclaration(
    name="get_forecast",
    description="Lấy dự báo thời tiết trong các ngày tới của một thành phố",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "city": types.Schema(
                type=types.Type.STRING, description="Tên thành phố"
            ),
            "days": types.Schema(
                type=types.Type.INTEGER,
                description="Số ngày dự báo (ví dụ 1, 3, 5 ngày)",
            ),
        },
        required=["city"],
    ),
)

TOOLS = [
    types.Tool(
        function_declarations=[
            get_weather_declaration,
            get_forecast_declaration,
        ]
    )
]


# 2. App tự thực thi tool (trong thực tế sẽ gọi API thời tiết thật)
def _normalize_city(city: str) -> str:
    """Chuẩn hóa tên thành phố tìm kiếm trong mock database."""
    c = city.lower().strip()
    if any(k in c for k in ["hồ chí minh", "hcm", "sài gòn"]):
        return "Hồ Chí Minh"
    if "hà nội" in c or "ha noi" in c:
        return "Hà Nội"
    if "đà nẵng" in c or "da nang" in c:
        return "Đà Nẵng"
    return city


def get_weather(city: str) -> str:
    """Trả về thời tiết hiện tại (mock) của *city*."""
    import json

    mock_data = {
        "Hà Nội": {
            "nhiệt_độ": "29°C",
            "thời_tiết": "trời mưa nhẹ",
            "độ_ẩm": "82%",
            "gió": {"hướng": "Đông Nam", "tốc_độ": "12 km/h"},
        },
        "Hồ Chí Minh": {
            "nhiệt_độ": "33°C",
            "thời_tiết": "mưa rào",
            "độ_ẩm": "75%",
            "gió": {"hướng": "Tây Nam", "tốc_độ": "15 km/h"},
        },
        "Đà Nẵng": {
            "nhiệt_độ": "30°C",
            "thời_tiết": "nhiều mây",
            "độ_ẩm": "78%",
            "gió": {"hướng": "Đông", "tốc_độ": "10 km/h"},
        },
    }
    norm_city = _normalize_city(city)
    default = {"nhiệt_độ": "28°C", "thời_tiết": "không có dữ liệu chi tiết"}
    return json.dumps({"city": city, **mock_data.get(norm_city, default)}, ensure_ascii=False)


def get_forecast(city: str, days: int = 3) -> str:
    """Trả về dự báo thời tiết (mock) của *city* trong các ngày tới."""
    import json

    mock_forecast = {
        "Hà Nội": [
            {"ngày": "Ngày mai", "nhiệt_độ": "28°C - 32°C", "thời_tiết": "nắng gián đoạn", "khả_năng_mưa": "20%"},
            {"ngày": "Ngày kia", "nhiệt_độ": "27°C - 31°C", "thời_tiết": "mưa rào rải rác", "khả_năng_mưa": "60%"},
            {"ngày": "3 ngày tới", "nhiệt_độ": "26°C - 30°C", "thời_tiết": "trời nhiều mây", "khả_năng_mưa": "40%"},
        ],
        "Hồ Chí Minh": [
            {"ngày": "Ngày mai", "nhiệt_độ": "26°C - 34°C", "thời_tiết": "nắng ráo, chiều tối mưa dông", "khả_năng_mưa": "70%"},
            {"ngày": "Ngày kia", "nhiệt_độ": "26°C - 33°C", "thời_tiết": "mưa rào", "khả_năng_mưa": "65%"},
            {"ngày": "3 ngày tới", "nhiệt_độ": "25°C - 33°C", "thời_tiết": "nắng nhẹ", "khả_năng_mưa": "30%"},
        ],
        "Đà Nẵng": [
            {"ngày": "Ngày mai", "nhiệt_độ": "27°C - 33°C", "thời_tiết": "nắng đẹp", "khả_năng_mưa": "10%"},
            {"ngày": "Ngày kia", "nhiệt_độ": "26°C - 32°C", "thời_tiết": "ít mây", "khả_năng_mưa": "15%"},
            {"ngày": "3 ngày tới", "nhiệt_độ": "27°C - 31°C", "thời_tiết": "có lúc mưa nhỏ", "khả_năng_mưa": "35%"},
        ],
    }

    norm_city = _normalize_city(city)
    default_list = [
        {"ngày": f"Ngày +{i+1}", "nhiệt_độ": "27°C - 32°C", "thời_tiết": "nhiều mây"}
        for i in range(days)
    ]
    data = mock_forecast.get(norm_city, default_list)[:days]
    return json.dumps({"city": city, "dự_báo": data}, ensure_ascii=False)


# Ánh xạ tên tool sang hàm python tương ứng
TOOL_MAP = {
    "get_weather": get_weather,
    "get_forecast": get_forecast,
}


def run(prompt: str) -> str:
    """Gửi *prompt* tới Gemini, tự động xử lý function calling và trả về câu trả lời cuối."""
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    ]

    # 3. Gọi model — model quyết định có gọi tool hay không
    resp = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            tools=TOOLS,
            system_instruction=SYSTEM_INSTRUCTION,
        ),
    )

    # 4. Vòng lặp: nếu model yêu cầu tool, app TỰ THỰC THI rồi đưa kết quả trả lại
    while resp.function_calls:
        # Thêm phản hồi của model vào lịch sử hội thoại
        contents.append(resp.candidates[0].content)

        function_responses = []
        for fc in resp.function_calls:
            print(f"  [model yêu cầu] {fc.name}({fc.args})")
            tool_func = TOOL_MAP.get(fc.name)
            if tool_func:
                result = tool_func(**fc.args)  # <-- app chạy hàm tương ứng
            else:
                result = f'{{"error": "Không tìm thấy tool {fc.name}"}}'
            print(f"  [app thực thi]  -> {result}")
            function_responses.append(
                types.Part.from_function_response(
                    name=fc.name, response={"result": result}
                )
            )

        # Gửi kết quả tool trả về cho model
        contents.append(types.Content(role="user", parts=function_responses))
        resp = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=TOOLS,
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )

    # 5. Model tổng hợp câu trả lời cuối
    return resp.text


if __name__ == "__main__":
    question = "Dự báo thời tiết Hà Nội 3 ngày tới và thời tiết hiện tại ở TP Hồ Chí Minh thế nào?"
    print(f"User: {question}\n")
    print("Trả lời:\n", run(question))
