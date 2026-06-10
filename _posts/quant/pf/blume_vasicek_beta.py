import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import matplotlib.pyplot as plt

# ==========================================
# 1. 数据获取与准备
# ==========================================
def get_market_data(tickers, market_ticker="^GSPC", start_date="2021-01-01", end_date="2025-12-31"):
    """
    获取个股和市场（默认标普500）的收盘价，并计算日收益率
    """
    all_tickers = tickers + [market_ticker]
    data = yf.download(all_tickers, start=start_date, end=end_date, progress=False)['Adj Close']
    
    # 计算日收益率并剔除缺失值
    returns = data.pct_change().dropna()
    
    market_ret = returns[market_ticker]
    stock_rets = returns[tickers]
    return stock_rets, market_ret

# ==========================================
# 2. 核心算法：计算历史 Beta 及 Vasicek 所需的方差
# ==========================================
def calculate_historical_beta_info(stock_rets, market_ret):
    """
    使用 OLS 回归计算历史 Beta 以及该 Beta 估计值的方差 (Standard Error 的平方)
    """
    betas = {}
    beta_vars = {}
    
    # 市场收益率（自变量），添加常数项
    X = sm.add_constant(market_ret)
    
    for col in stock_rets.columns:
        Y = stock_rets[col]
        model = sm.OLS(Y, X).fit()
        
        # model.params[0] 是常数项 (Alpha), model.params[1] 是市场系数 (Beta)
        beta_hist = model.params.iloc[1]
        # model.bse[1] 是 Beta 的标准误差 (Standard Error)
        beta_var = model.bse.iloc[1] ** 2 
        
        betas[col] = beta_hist
        beta_vars[col] = beta_var
        
    return pd.Series(betas), pd.Series(beta_vars)

# ==========================================
# 3. 贝塔调整函数
# ==========================================
def blume_adjustment(beta_hist):
    """
    布卢姆调整法（采用彭博经典参数：0.33 + 0.67 * Beta）
    """
    return 0.33 + 0.67 * beta_hist

def vasicek_adjustment(beta_hist, beta_vars):
    """
    瓦希切克调整法（贝叶斯推断）
    """
    # 计算全市场（当前样本）Beta 的均值和横截面方差
    market_beta_mean = beta_hist.mean()
    market_beta_var = beta_hist.var()
    
    # 运用 Vasicek 公式
    weight_hist = market_beta_var / (beta_vars + market_beta_var)
    weight_market = beta_vars / (beta_vars + market_beta_var)
    
    beta_vasicek = weight_hist * beta_hist + weight_market * market_beta_mean
    return beta_vasicek

# ==========================================
# 4. 主程序运行
# ==========================================
if __name__ == "__main__":
    # 选择一些不同行业、不同风险特征的股票
    # TSLA (高Beta), JNJ (低Beta), AAPL (稳健型), NVDA (高增长/高波动)
    tickers = ["TSLA", "JNJ", "AAPL", "NVDA", "MSFT", "AMZN", "XOM"]
    
    print("正在获取数据并计算...")
    stock_rets, market_ret = get_market_data(tickers)
    
    # 计算历史 Beta 及其估计方差
    beta_hist, beta_vars = calculate_historical_beta_info(stock_rets, market_ret)
    
    # 执行 Blume 调整
    beta_blume = blume_adjustment(beta_hist)
    
    # 执行 Vasicek 调整
    beta_vasicek = vasicek_adjustment(beta_hist, beta_vars)
    
    # 汇总结果
    df_result = pd.DataFrame({
        "Historical Beta": beta_hist,
        "Beta Variance (Error)": beta_vars,
        "Blume Beta": beta_blume,
        "Vasicek Beta": beta_vasicek
    })
    
    # 打印结果表格
    print("\n" + "="*50)
    print("Beta 调整结果对比")
    print("="*50)
    print(df_result.round(4))
    
    # ==========================================
    # 5. 可视化对比
    # ==========================================
    df_result[['Historical Beta', 'Blume Beta', 'Vasicek Beta']].plot(kind='bar', figsize=(12, 6))
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Market Mean (1.0)')
    plt.title("Comparison of Beta Adjustments: Blume vs Vasicek")
    plt.ylabel("Beta Value")
    plt.xlabel("Stocks")
    plt.legend()
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    plt.xticks(rotation=0)
    plt.show()