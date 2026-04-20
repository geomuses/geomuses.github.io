import pandas as pd
import matplotlib.pyplot as plt
from futu import *

# --- 1. 配置与连接 ---
# 请确保 Futu OpenD 已打开并登录
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
trd_ctx = OpenUSTradeContext(host='127.0.0.1', port=11111) # 这里以美股交易上下文为例
pwd_unlock = '670915'

def calculate_vwap_and_plot(stock_code):
    # --- 2. 获取日内 5 分钟数据 ---
    # 分时数据在富途对应为 get_rt_ticker 或通过 K 线接口获取
    # 这里使用 K 线接口获取当天的 5 分钟数据
    ret, data, page_req_key = quote_ctx.request_history_kline(
        stock_code, 
        interval=KType.K_5M, 
        start=pd.Timestamp.now().strftime('%Y-%m-%d'), 
        max_count=200
    )
    
    if ret != RET_OK:
        print(f"获取 {stock_code} 数据失败: {data}")
        return

    df = data.copy()
    
    # --- 3. 计算 VWAP ---
    # 富途返回的列名通常是 'high', 'low', 'close', 'volume'
    # 1. 计算典型价格 (TP)
    df['TP'] = (df['high'] + df['low'] + df['close']) / 3

    # 2. 计算累计成交量权重价格 (PV) 和累计成交量
    df['Cum_PV'] = (df['TP'] * df['volume']).cumsum()
    df['Cum_Vol'] = df['volume'].cumsum()

    # 3. 得到 VWAP
    df['VWAP'] = df['Cum_PV'] / df['Cum_Vol']

    # --- 4. 绘图 ---
    plt.figure(figsize=(12, 6))
    plt.plot(df['time_key'], df['close'], label=f'Price ({stock_code})', color='blue', alpha=0.6)
    plt.plot(df['time_key'], df['VWAP'], label='VWAP', color='orange', linestyle='--')
    plt.title(f"Intraday Price vs VWAP for {stock_code}")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

try:

    target_acc_id = 4579635
    target_env = TrdEnv.SIMULATE  # 必须是 SIMULATE
    
    ret, pos_df = trd_ctx.position_list_query(acc_id=target_acc_id, trd_env=target_env)
    
    if ret == RET_OK:
        if not pos_df.empty:
            print(f"--- 模拟账户 {target_acc_id} 持仓清单 ---")
            # 打印代码、名称、持有数量、成本价
            print(pos_df[['code', 'stock_name', 'qty', 'cost_price']])
            
            # 提取代码列表供后续计算 VWAP
            my_stocks = pos_df['code'].tolist()
            print(f"\n准备计算以下标的的 VWAP: {my_stocks}")
            
            
            # for stock in my_stocks:
            #     calculate_vwap_and_plot(stock)
                
        else:
            print(f"账户 {target_acc_id} 目前是空仓，请先在富途牛牛模拟盘里买入一点股票。")
    else:
        print(f"查询失败，错误信息: {pos_df}")

finally:
    trd_ctx.close()
    quote_ctx.close()