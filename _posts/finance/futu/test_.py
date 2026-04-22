from google import genai
from google.genai import types

# 1. 初始化 Client
GEMINI_API_KEY = "AIzaSyCpxUETaUx7SOWVBxYwC2rnJJULbzOTv6g"

# 2. 生成內容 (以分析 NVDA 為例)
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
     model="gemini-3-flash-preview",
     contents="請用一句話介紹美股 NVDA 的前景。",
    config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_level="low")
    ),
)
print(response.text)

print(response.text)