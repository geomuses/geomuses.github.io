---
layout: post
title: 量化金融 telegram 发送讯息
date: 2026-04-25 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - python
---

# 环境准备

```bash
pip install python-telegram-bot
```

# 基础发送代码 

这是最标准的发送消息方式：

```python
import asyncio
from telegram import Bot

async def send_notice():
    bot_token = "123456789:ABCDefGhIJKlmNoP..."
    chat_id = "123456789"
    bot = Bot(token=bot_token)
    
    async with bot:
        await bot.send_message(
            chat_id=chat_id, 
            text="测试消息。"
        )

if __name__ == '__main__':
    asyncio.run(send_notice())
```

## 发送 Markdown 或按钮

```python
async def send_fancy_msg():
	bot_token = "123456789:ABCDefGhIJKlmNoP..."
    chat_id = "123456789"
    bot = Bot(token="YOUR_TOKEN")
    
    async with bot:
        text = "*通知*: 测试消息"
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="MarkdownV2" # 支持加粗、链接等
        )
```