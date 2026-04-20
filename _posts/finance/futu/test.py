import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 获取数据
df = yf.download("GLW", period="1d", interval="5m")
sp500 = yf.download("SPY", period="1d", interval="5m")
# --- 关键修正：处理多级索引 ---
# 如果列名是多级的 (例如 ('Close', 'GLW'))，只保留第一级
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# 现在 df['High'], df['Low'], df['Close'] 都是单级索引了，计算将恢复正常
# 1. 计算每一根 K 线的典型价格 (TP)
df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3

# 2. 计算累计成交量权重价格 和 累计成交量
df['Cum_PV'] = (df['TP'] * df['Volume']).cumsum()
df['Cum_Vol'] = df['Volume'].cumsum()

# 3. 得到 VWAP
df['VWAP'] = df['Cum_PV'] / df['Cum_Vol']

# 绘图对比
plt.figure(figsize=(12,6))
plt.plot(df.index, df['Close'], label='Price (GLW)', color='blue', alpha=0.6)
# plt.plot(sp500.index, sp500['Close'], label='Price (SPY)', color='red', alpha=0.6)
plt.plot(df.index, df['VWAP'], label='VWAP', color='orange', linestyle='--')
plt.title("Intraday Price vs VWAP - GLW")
plt.legend()
plt.xticks(rotation=45)
plt.show()