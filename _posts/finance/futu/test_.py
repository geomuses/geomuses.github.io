import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# 1. 获取数据 (以某个基金/股票 vs 标普500为例)
tickers = ['AAPL', '^GSPC'] # AAPL作为投资组合，^GSPC作为基准
data = yf.download(tickers, start="2023-01-01", end="2024-01-01")['Close']
returns = data.pct_change().dropna()
# 2. 定义滚动窗口 (例如 60 天)
window = 60
alphas = []
dates = returns.index[window:]

for i in range(len(returns) - window):
    # 提取窗口内的数据
    window_data = returns.iloc[i:i+window]
    y = window_data['AAPL']  # 因变量：投资组合收益
    X = window_data['^GSPC'] # 自变量：市场收益
    X = sm.add_constant(X)   # 添加常数项，即 Alpha
    
    model = sm.OLS(y, X).fit()
    alphas.append(model.params['const']) # 提取 Alpha

# 3. 转换为 Series 方便绘图
alpha_series = pd.Series(alphas, index=dates)

# 4. 可视化
plt.figure(figsize=(12, 6))
plt.plot(alpha_series, label='60-Day Rolling Alpha', color='blue', lw=1.5)
plt.axhline(0, color='red', linestyle='--', alpha=0.7) # 零基准线
plt.title('Investment Portfolio Rolling Alpha (60-Day Window)')
plt.ylabel('Alpha Value')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()