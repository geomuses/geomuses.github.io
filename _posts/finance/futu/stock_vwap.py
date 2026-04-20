import pandas as pd
import matplotlib.pyplot as plt
from futu import *

# --- 1. 配置与连接 ---
# 请确保 Futu OpenD 已打开并登录
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
trd_ctx = OpenUSTradeContext(host='127.0.0.1', port=11111) # 这里以美股交易上下文为例

try:

    target_acc_id = 4579635
    target_env = TrdEnv.SIMULATE  # 必须是 SIMULATE
    
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