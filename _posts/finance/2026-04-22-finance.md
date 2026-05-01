---
layout: post
title: 量化金融 通过futu捉取数据
date: 2026-04-22 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - python
---

检查什么账号可以用?

```python
from futu import *

# 1. 尝试连接（建议先用通用的上下文查看账户列表）
trd_ctx = OpenUSTradeContext(host='127.0.0.1', port=11111)
try:
    # 2. 获取所有账户列表（核心诊断步骤）
    ret, data = trd_ctx.get_acc_list()
    if ret == RET_OK:
        print("--- 找到可用账户列表 ---")
        print(data) 
        # 观察结果里的 trd_env (1是真实, 0是模拟) 和 acc_id
    else:
        print(f"获取账户列表失败: {data}")

finally:
    trd_ctx.close()
```

通过 `python` 基于 `futu` 得到模拟账号后访问模拟账户股票的持仓清单

```python
import pandas as pd
import matplotlib.pyplot as plt
from futu import *

# 请确保 Futu OpenD 已打开并登录
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
trd_ctx = OpenUSTradeContext(host='127.0.0.1', port=11111) # 这里以美股交易上下文为例
try:
	target_acc_id = 4579635
	target_env = TrdEnv.SIMULATE  # 必须是 SIMULATE
	ret, pos_df = trd_ctx.position_list_query(acc_id=target_acc_id, trd_env=target_env)
	if ret == RET_OK:
		if not pos_df.empty:
			print(f"--- 模拟账户 {target_acc_id} 持仓清单 ---")
			# 打印代码、名称、持有数量、成本价
			print(pos_df[['code', 'stock_name', 'qty', 'cost_price']])  
		else:
			print(f"账户 {target_acc_id} 目前是空仓，请先在富途牛牛模拟盘里买入一点股票。")
	else:
		print(f"查询失败，错误信息: {pos_df}")

finally:
	trd_ctx.close()
	quote_ctx.close()
```

```bash
--- 模拟账户 4579635 持仓清单 ---
      code stock_name    qty  cost_price
0  US.INTC      Intel  100.0      61.800
1  US.NVDA     NVIDIA  200.0     185.425
2  US.SNDK    SanDisk  100.0     902.255
3    US.KO  Coca-Cola  100.0      78.270
```