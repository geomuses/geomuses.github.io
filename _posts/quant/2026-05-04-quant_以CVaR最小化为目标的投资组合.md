---
layout: post
title: 量化金融 投资组合 以 CVaR 最小化为目标的投资组合
date: 2026-05-04 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - python
---

构建以 **CVaR 最小化**为目标的投资组合，是量化金融中超越传统马科维茨（均值-方差）模型的高级阶段。在 Python 中，最成熟的工具是 `PyPortfolioOpt`，它通过集成 `CVXPY` 凸优化库，能够高效解决这个线性规划问题。

# Mean-CVaR 优化

传统的均值-方差优化假设收益率呈正态分布，但在现实中（尤其是加密货币或波动较大的科技股），收益率往往具有“肥尾”特征。

- **目标函数：** 在满足预期收益率（如年化 10%）的条件下，使 CVaR（尾部平均损失）最小。
    
- **数学特性：** 这是一个凸优化问题，可以通过线性规划求解。
    

---

# 最小化 CVaR 组合

找出在 95% 置信度下使 CVaR 最小的权重分配。

```python
import yfinance as yf
import pandas as pd
from pypfopt import expected_returns, EfficientFrontier, objective_functions

# 1. 下载历史数据 (2年数据)
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
data = yf.download(tickers, period="2y")['Close']
returns = data.pct_change().dropna()

# 2. 计算预期收益率 (这里使用历史均值)
mu = expected_returns.mean_historical_return(data)

# 3. 初始化 EfficientFrontier 优化器
# 我们直接传入收益率矩阵 returns，因为 CVaR 计算需要完整的历史分布，而不仅仅是均值和协方差
ef = EfficientFrontier(None, returns)

# 4. 添加目标：最小化 CVaR
# beta 代表置信水平 (0.95 对应 95%)
ef.efficient_risk(target_risk=None, market_neutral=False) # 占位
weights = ef.efficient_return(target_return=0.15) # 设定目标收益率为 15% 时的 CVaR 最小化

# 或者更直接：单纯追求全局 CVaR 最小
ef_min_cvar = EfficientFrontier(None, returns)
ef_min_cvar.add_objective(objective_functions.p_cvar, beta=0.95)
weights = ef_min_cvar.nonconvex_objective(
    objective_functions.p_cvar, 
    objective_args=(returns, 0.95)
)

clean_weights = ef_min_cvar.clean_weights()
print(f"优化后的资产权重: {clean_weights}")
```

---

# 结果对比与分析

通过 CVaR 优化得到的权重分配，通常会与马科维茨模型有显著不同：

|**特性**|**均值-方差优化 (Markowitz)**|**Mean-CVaR 优化**|
|---|---|---|
|**风险度量**|波动率 (标准差 $\sigma$)|尾部平均损失 (CVaR)|
|**分布假设**|必须假设为正态分布|**不依赖**分布假设，捕捉肥尾|
|**极端情况**|容易低估黑天鹅风险|专门针对极端负面情况优化|
|**资产偏好**|偏好低波动资产|偏好在崩盘时表现稳健的资产|

利用自有套件

```python
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

# 1. 核心风险函数：计算组合 CVaR
def get_portfolio_cvar(weights, returns_matrix, alpha=0.95):
    """
    计算给定权重下的组合 CVaR (基于历史模拟法)
    """
    # 计算组合每日收益率序列
    portfolio_returns = np.dot(returns_matrix, weights)
    
    # 排序并确定尾部索引
    sorted_returns = np.sort(portfolio_returns)
    n_worst = int(len(sorted_returns) * (1 - alpha))
    
    # 防止数据量过小导致索引为 0
    n_worst = max(1, n_worst)
    
    # 计算最差情况的平均值
    cvar = np.mean(sorted_returns[:n_worst])
    
    # minimize 默认寻找最小值，-cvar 将损失最大化（即寻找风险最小点）
    return -cvar

# 2. 优化执行器
def optimize_min_cvar(tickers, period="2y", alpha=0.95):
    # 下载并清洗数据
    data = yf.download(tickers, period=period)['Close']
    returns = data.pct_change().dropna()
    
    num_assets = len(tickers)
    returns_matrix = returns.values
    
    # 约束：权重之和等于 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # 边界：不允许卖空 (0, 1)
    bounds = tuple((0, 1) for _ in range(num_assets))
    
    # 初始权重：平权
    init_weights = np.array([1. / num_assets] * num_assets)
    
    # 执行优化 (使用 SLSQP 算法)
    result = minimize(
        get_portfolio_cvar,
        init_weights,
        args=(returns_matrix, alpha),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        tol=1e-9  # 提高容差精度
    )
    
    if not result.success:
        print("优化未成功收敛:", result.message)
        
    return result.x, returns

# --- 执行示例 ---
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
optimal_weights, historical_returns = optimize_min_cvar(tickers)

# 打印结果
print("\n=== 最小化 CVaR (95%) 权重分配 ===")
for ticker, weight in zip(tickers, optimal_weights):
    print(f"{ticker}: {weight:.2%}")

# 计算该组合的历史表现
final_cvar = -get_portfolio_cvar(optimal_weights, historical_returns.values)
print(f"\n该组合的历史单日 CVaR (95%): {final_cvar:.2%}")
```

这段代码会计算组合收益率，找到 95% 置信度下的 VaR 阈值，并将所有超过该阈值的损失区域

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_portfolio_cvar(weights, returns_df, alpha=0.95):
    # 1. 计算投资组合的历史收益率
    portfolio_returns = np.dot(returns_df.values, weights)
    
    # 2. 计算 VaR 和 CVaR
    sorted_returns = np.sort(portfolio_returns)
    index = int(len(sorted_returns) * (1 - alpha))
    var_threshold = sorted_returns[index]
    cvar_value = np.mean(sorted_returns[:index])
    
    # 3. 绘图设置
    plt.figure(figsize=(12, 6))
    sns.histplot(portfolio_returns, bins=50, kde=True, color='royalblue', alpha=0.6)
    
    # 4. 高亮 CVaR 区域（左侧尾部）
    # 获取直方图的 y 轴范围以绘制阴影
    plt.axvline(var_threshold, color='darkred', linestyle='--', label=f'VaR ({alpha:.0%}): {var_threshold:.2%}')
    plt.axvline(cvar_value, color='red', linestyle='-', linewidth=2, label=f'CVaR ({alpha:.0%}): {cvar_value:.2%}')
    
    # 填充颜色：从最小收益率到 VaR 阈值
    plt.fill_betweenx(y=[0, plt.gca().get_ylim()[1]], 
                     x1=min(portfolio_returns), 
                     x2=var_threshold, 
                     color='red', alpha=0.2, label='Tail Risk Area (CVaR)')
    
    # 5. 图表修饰
    plt.title(f'Portfolio Returns Distribution & CVaR Analysis', fontsize=14)
    plt.xlabel('Daily Returns')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.show()

# 使用之前优化出的权重进行绘图
plot_portfolio_cvar(optimal_weights, historical_returns)
```