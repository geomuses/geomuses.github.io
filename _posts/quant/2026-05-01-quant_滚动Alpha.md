---
layout: post
title: 量化金融 投资组合 滚动Alpha
date: 2026-05-01 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - python
---
**滚动Alpha（Rolling Alpha）** 在投资组合管理中通常指通过滚动窗口（Rolling Window）计算出的动态超额收益。它不再是一个静态的数值，而是一个随时间变化的序列，用于衡量策略在不同市场环境下的持续获利能力

根据资本资产定价模型（CAPM），我们要计算的是残差项：

$$\alpha_t = R_{p} - [R_{f} + \beta \times (R_{m} - R_{f})]$$

但在实际波动的可视化中，我们通常关注**滚动 Alpha (Rolling Alpha)**，以观察其随时间的变化

```python
import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# 1. 获取数据 (以某个基金/股票 vs 标普500为例)
tickers = ['AAPL', '^GSPC'] # AAPL作为投资组合，^GSPC作为基准
data = yf.download(tickers, start="2020-01-01", end="2024-01-01")['Adj Close']
returns = data.pct_change().dropna()
rf = 0.04 / 252
# 2. 定义滚动窗口 (例如 60 天)
window = 60
alphas = []
dates = returns.index[window:]

for i in range(len(returns) - window):
    # 提取窗口内的数据
    window_data = returns.iloc[i:i+window]
    y = window_data['AAPL'] - rf # 因变量：投资组合收益
    X = window_data['^GSPC'] - rf # 自变量：市场收益
    X = sm.add_constant(X)   # 添加常数项，即 Alpha
    
    model = sm.OLS(y, X).fit()
    alphas.append(model.params['const']  ) # 提取 Alpha

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
```

# 建议

- ** 不要只看 Alpha 的正负，要看它的 **稳定性 (Tracking Error)**。如果 Alpha 波动极大，那它大概率是运气；如果 Alpha 曲线非常平滑，那它才更接近真正的“能力”

|**情况**|**过去的正 Alpha 说明了什么**|**未来会跌吗？**|
|---|---|---|
|**均值回归型**|纯属运气或短期情绪推动|**大概率下跌**|
|**规模效应型**|策略太成功导致资金过载|**收益率会回落**|
|**能力驱动型**|拥有持续的定价/技术优势|**可能持续保持正向**|

- **单一的 Beta** 可能无法完全解释收益。建议使用 **Fama-French 五因子模型**

- **置信区间 (Confidence Interval)：** 如果 Alpha 波动在置信区间内，说明该超额收益在统计上不显著（可能是运气）。
    
- **最大回撤对比：** 在 Alpha 曲线下方叠加 Alpha 的回撤图，观察超额收益的稳定性


