---
layout: post
title: 量化金融 AI 发送讯息
date: 2026-04-26 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - python
---

```bash
pip install -q -U google-generativeai
```

- `-q`: 安靜模式（Quiet），減少安裝過程中的日誌輸出。
- `-U`: 升級（Upgrade），如果你之前安裝過，這會將它更新到最新版本（這對使用 Gemini 1.5 Pro/Flash 非常重要）。

安裝完代碼庫後，你需要一個密鑰才能調用 Gemini AI：

1. 訪問 **[Google AI Studio](https://aistudio.google.com/)**。
2. 使用你的 Google 帳號登錄。
3. 點擊左側的 **"Get API key"** 並創建一個新密鑰。

```python
import google.generativeai as genai
import os

# 設定你的 API Key
GEMINI_API_KEY = "AIzaSyCpxUETaUx7SOWVBxYwC2rnJJULbzOTv6g"

client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
     model="gemini-3-flash-preview",
     contents="請用一句話介紹美股 NVDA 的前景。",
     config=types.GenerateContentConfig(
     thinking_config=types.ThinkingConfig(thinking_level="low")
    ),
)

print(response.text)
```

```bash
NVIDIA 作為全球 **AI 革命的核心算力引擎**，憑藉其在高效能晶片與 CUDA 軟體生態系的絕對領先地位，將持續引領人工智慧與資料中心市場的長期爆發性增長。
```