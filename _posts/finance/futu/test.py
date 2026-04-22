from edgar import *
import google.generativeai as genai
from google.genai import types
import asyncio

# --- 設定 ---
set_identity("boonhong565059@gmail.com") # SEC 要求必須設定身份
BOT_TOKEN = "8312172130:AAHVyEpIItPeuiAykeuN9CMCJya_Gz6U7uk"
CHAT_ID = "-1003370646305"
GEMINI_API_KEY = "AIzaSyCpxUETaUx7SOWVBxYwC2rnJJULbzOTv6g"
# model = genai.GenerativeModel('gemini-1.5-pro') # 建議用 Pro 處理長文本財報

def get_latest_filings(ticker):
    company = Company(ticker)
    # 獲取最新的 10-Q (季報)
    filings = company.get_filings(form="10-Q").latest(1)
    # 提取 MD&A 部分（管理層討論與分析），這是財報的核心
    return filings.obj().get_section('mda')

async def analyze_report(ticker):
    mda_text = get_latest_filings(ticker)
    
    prompt = f"""
    你是一位資深的金融工程師。請分析以下 {ticker} 的最新財報 (MD&A 部分)。
    請為我的 Obsidian 筆記輸出以下結構：
    1. ## 💰 營收與盈利能力 (Revenue & Profitability)
    2. ## 🚀 成長動能 (Growth Drivers)
    3. ## ⚠️ 潛在風險 (Risk Factors)
    4. ## 📊 給投資者的建議 (適合加倉或減倉？)
    
    請保持專業、簡練，並使用繁體中文。
    財報內容：{mda_text[:10000]} # 截取部分文本避免超出 Token 限制
    """
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low")
            ),
        )
    content = f"{response.text}"
    return content

# 執行分析
report = asyncio.run(analyze_report("NVDA"))
print(report)