#%%
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

data = yf.download(["SNDK", "GOOG", "NVDA","COHR"], period="5y")
data = data['Close']

returns = data.pct_change().dropna()
mean_returns = returns.mean() * 252
cov_matrix = sigma  = returns.cov() * 252
risk_free_rate = 0.02

def portfolio_performance(weights, mean_returns, cov_matrix):
    p_ret = np.sum(mean_returns * weights)
    p_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return p_ret, p_std

# 目标函数（-Sharpe）
def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    p_ret, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
    return -(p_ret - risk_free_rate) / p_std

# 最小方差目标
def min_variance(weights, mean_returns, cov_matrix, risk_free_rate=None):
    return portfolio_performance(weights, mean_returns, cov_matrix)[1]

# 优化函数
def optimize_portfolio(mean_returns, cov_matrix, objective_func):
    num_assets = len(mean_returns)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for _ in range(num_assets))
    initial_weights = num_assets * [1./num_assets]
    
    result = minimize(objective_func, initial_weights,
                      args=(mean_returns, cov_matrix, risk_free_rate),
                      method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x

# 最大 Sharpe 比率组合
max_sharpe_weights = optimize_portfolio(mean_returns, cov_matrix, negative_sharpe_ratio)
max_sharpe_ret, max_sharpe_std = portfolio_performance(max_sharpe_weights, mean_returns, cov_matrix)
max_sharpe_ratio = (max_sharpe_ret - risk_free_rate) / max_sharpe_std

# 最小波动率组合
min_vol_weights = optimize_portfolio(mean_returns, cov_matrix, min_variance)
min_vol_ret, min_vol_std = portfolio_performance(min_vol_weights, mean_returns, cov_matrix)

print("=== Max Sharpe Weights ===")
print(pd.Series(max_sharpe_weights, index=mean_returns.index))
print("\n=== Min Volatility Weights ===")
print(pd.Series(min_vol_weights, index=mean_returns.index))

# 1. 定义效用函数
def utility_func(vol, utility_level, lmbda):
    # 根据 U = R - 0.5 * lambda * var 变形得出 R
    return utility_level + 0.5 * lmbda * (vol**2)

# 2. 设置参数
# lmbda 越大，曲线越陡（越保守）；lmbda 越小，曲线越平缓（越冒险）
lmbda = 3.0  
vols_range = np.linspace(min_vol_std * 0.8, max_sharpe_std * 1.5, 100)

# 3. 计算特定点的效用（例如：最大 Sharpe 点或最小波动点的效用）
# 这里我们以最大 Sharpe 点为切点示例
utility_at_max_sharpe = max_sharpe_ret - 0.5 * lmbda * (max_sharpe_std**2)
utility_at_min_vol = min_vol_ret - 0.5 * lmbda * (min_vol_std**2)

# 1. 定义有效边界计算函数
def efficient_frontier(mean_returns, cov_matrix, returns_range):
    eff_vols = []
    num_assets = len(mean_returns)
    initial_weights = num_assets * [1./num_assets]
    bounds = tuple((0, 1) for _ in range(num_assets))
    
    for target_ret in returns_range:
        # 约束条件：1. 权重之和为1  2. 收益率等于目标收益率
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.sum(mean_returns * x) - target_ret}
        )
        
        result = minimize(min_variance, initial_weights, 
                          args=(mean_returns, cov_matrix),
                          method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            eff_vols.append(result.fun)
        else:
            eff_vols.append(None)
            
    return eff_vols

# 3. 设置市场权重 (假设值，实际可用市值占比)
mkt_weights = np.array([0.35, 0.30, 0.20, 0.15])

# 4. 计算风险厌恶系数 delta
# 假设市场超额收益率为 8%，风险溢价 / 市场方差
market_var = mkt_weights.T @ sigma @ mkt_weights
delta = 0.08 / market_var

# 5. 逆向优化得出均衡收益率 Pi
pi = delta * (sigma @ mkt_weights)

P = np.array([
    [1, -1, 0, 0],  # AAPL vs MSFT
    [0, 0, 1, 0]    # GOOGL absolute
])
Q = np.array([0.02, 0.10])

# tau: 标量参数，通常取值很小 (0.025 - 0.05)，表示对先验估值的信心程度
tau = 0.05

# Omega: 观点的协方差矩阵 (不确定性)
# 常用启发式方法: Omega = diag(P * (tau * Sigma) * P.T)
omega = np.diag(np.diag(P @ (tau * sigma) @ P.T))

# 计算公式的第一部分和第二部分
term1_inv = np.linalg.inv(tau * sigma)
term2_inv = P.T @ np.linalg.inv(omega) @ P

# 最终 BL 预期收益率
mu_bl = np.linalg.inv(term1_inv + term2_inv) @ (term1_inv @ pi + P.T @ np.linalg.inv(omega) @ Q)

# 计算新权重
# 注意：这只是原始权重，未考虑约束条件（如禁止空头）
new_weights = np.linalg.inv(delta * sigma) @ mu_bl
new_weights /= new_weights.sum()

print("市场均衡收益率 (Pi):\n", pi)
print("\nBL 修正收益率 (Mu_BL):\n", mu_bl)
print("\nBL 建议权重:\n", new_weights)

bl_ret, bl_std = portfolio_performance(new_weights, mean_returns, cov_matrix)
print("BL 收益率:", bl_ret)
print("BL 波动率:", bl_std) 

target_returns = np.linspace(min_vol_ret, mean_returns.max(), 30)
efficient_vols = efficient_frontier(mean_returns, cov_matrix, target_returns)

plt.figure(figsize=(10, 6))

# 绘制有效边界
plt.plot(efficient_vols, target_returns, 'b--', linewidth=2, label='Efficient Frontier')

# 标注最大 Sharpe 比率组合
plt.scatter(max_sharpe_std, max_sharpe_ret, color='red', marker='*', s=200, label='Max Sharpe Ratio')

# 标注最小波动率组合
plt.scatter(min_vol_std, min_vol_ret, color='green', marker='o', s=100, label='Min Volatility')

# 绘制不同效用水平的无异曲线
plt.plot(vols_range, utility_func(vols_range, utility_at_max_sharpe, lmbda), 
         'g-', alpha=0.6, label=f'Indifference Curve (Utility Max Sharpe, $\lambda$={lmbda})')

plt.plot(vols_range, utility_func(vols_range, utility_at_min_vol, lmbda), 
         'g:', alpha=0.4, label=f'Indifference Curve (Utility Min Vol)')

#bl
plt.scatter(bl_std, bl_ret, color='blue', marker='o', s=100, label='BL')
plt.title('Portfolio Optimization: Efficient Frontier')
plt.xlabel('Annualized Volatility (Std Dev)')
plt.ylabel('Annualized Returns')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()