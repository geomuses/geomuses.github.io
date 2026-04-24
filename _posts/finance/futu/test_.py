import yfinance as yf
import numpy as np

# 1. 下载数据 (以苹果 AAPL 和标普500 ^GSPC 为例)
tickers = ['AAPL', '^GSPC']
data = yf.download(tickers, start="2023-01-01", end="2024-01-01")['Close']
print(data)


# 2. 计算日收益率
returns = data.pct_change().dropna()

# 3. 设定参数
rf = 0.04  # 假设无风险利率为 4% (年化)
# 将年化无风险利率转换为日化 (简单处理)
daily_rf = rf / 252

# 4. 计算 Beta (资产收益率与市场收益率的协方差 / 市场收益率的方差)
covariance = np.cov(returns['AAPL'], returns['^GSPC'])[0, 1]
market_variance = np.var(returns['^GSPC'])
beta = covariance / market_variance

# 5. 计算市场年化收益率
market_annual_return = returns['^GSPC'].mean() * 252

# 6. 计算风险溢价
market_risk_premium = market_annual_return - rf
asset_risk_premium = beta * market_risk_premium

print(f"Beta 系数: {beta:.2f}")
print(f"市场风险溢价: {market_risk_premium:.2%}")
print(f"该资产(AAPL)的风险溢价: {asset_risk_premium:.2%}")