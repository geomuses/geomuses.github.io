import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf

# 处理 matplotlib 中文显示问题（如需要）
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


def build_us_stock_capm_portfolio(tickers, market_ticker, start_date, end_date, weights, rf_annual):
    """下载美股真实数据并进行 CAPM 组合构建与画图"""
    print("正在从 Yahoo Finance 下载美股历史数据...")

    # 1. 批量下载个股和市场指数的收盘价
    all_tickers = tickers + [market_ticker]
    data = yf.download(all_tickers, start=start_date, end=end_date)["Close"]

    # 2. 计算每日收益率
    returns_df = data.pct_change().dropna()

    # 3. 参数初始化
    rf_daily = rf_annual / 252
    market_returns = returns_df[market_ticker]
    market_mean_annual = market_returns.mean() * 252  # 市场的年化平均历史收益率

    asset_betas = {}
    asset_expected_returns_annual = {}
    asset_historical_returns_annual = {}

    # 4. 对每只美股运行 OLS 回归计算 Beta
    X = market_returns - rf_daily
    X_with_const = sm.add_constant(X)

    for ticker in tickers:
        Y = returns_df[ticker] - rf_daily
        model = sm.OLS(Y, X_with_const).fit()

        # 提取 Beta
        beta = model.params[market_ticker]
        asset_betas[ticker] = beta

        # 依据 CAPM 公式计算理论年化预期收益率
        expected_return_annual = rf_annual + beta * (market_mean_annual - rf_annual)
        asset_expected_returns_annual[ticker] = expected_return_annual

        # 记录其过去 3 年的实际年化历史收益率 (对比用)
        asset_historical_returns_annual[ticker] = returns_df[ticker].mean() * 252

    # 5. 整合资产详情数据
    asset_details = pd.DataFrame(
        {
            "Weight": pd.Series(weights),
            "Beta": pd.Series(asset_betas),
            "CAPM_Expected_Return_Annual": pd.Series(asset_expected_returns_annual),
            "Historical_Return_Annual": pd.Series(asset_historical_returns_annual),
        }
    )

    # 6. 计算投资组合的整体指标
    portfolio_beta = np.sum(asset_details["Beta"] * asset_details["Weight"])
    portfolio_capm_return = np.sum(
        asset_details["CAPM_Expected_Return_Annual"] * asset_details["Weight"]
    )
    portfolio_hist_return = np.sum(
        asset_details["Historical_Return_Annual"] * asset_details["Weight"]
    )

    portfolio_summary = {
        "Portfolio_Beta": portfolio_beta,
        "Portfolio_CAPM_Expected_Return_Annual": portfolio_capm_return,
        "Portfolio_Historical_Return_Annual": portfolio_hist_return,
    }

    # ==========================================
    # 7. 绘图：证券 market 线 (SML) 与个股位置
    # ==========================================
    plt.figure(figsize=(10, 6))

    # 绘制 SML 理论直线 (从无风险资产连接到市场组合)
    beta_range = np.linspace(0, 2.0, 100)
    sml_line = rf_annual + beta_range * (market_mean_annual - rf_annual)
    plt.plot(beta_range, sml_line, "g--", label="Security Market Line (SML)")

    # 标注无风险利率点与市场指数点
    plt.scatter(0, rf_annual, color="blue", s=100, zorder=5)
    plt.text(-0.05, rf_annual + 0.005, f"Risk-Free ({rf_annual:.2%})", va="bottom")

    plt.scatter(1.0, market_mean_annual, color="red", s=100, zorder=5)
    plt.text(1.02, market_mean_annual, f"Market (SPY: {market_mean_annual:.2%})", ha="left")

    # 绘制个股在图中的实际历史位置（实际收益率 vs Beta）
    for ticker in tickers:
        b = asset_details.loc[ticker, "Beta"]
        r_hist = asset_details.loc[ticker, "Historical_Return_Annual"]
        plt.scatter(b, r_hist, s=150, label=f"{ticker} (Actual)")
        plt.text(b + 0.02, r_hist, ticker, fontsize=12, va="center")

    # 绘制我们构建的组合位置
    plt.scatter(
        portfolio_beta,
        portfolio_hist_return,
        color="purple",
        marker="*",
        s=250,
        label="Your Portfolio (Actual)",
        zorder=6,
    )
    plt.text(
        portfolio_beta + 0.02,
        portfolio_hist_return - 0.005,
        "Portfolio",
        fontsize=12,
        fontweight="bold",
        color="purple",
    )

    plt.title("美股资产与投资组合的 CAPM 证券市场线 (SML) 校验图", fontsize=14)
    plt.xlabel("系统性风险 Beta ($\\beta$)", fontsize=12)
    plt.ylabel("年化收益率 (Annual Return)", fontsize=12)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left")

    plt.show()

    return portfolio_summary, asset_details


# ==========================================
# 策略执行主程序
# ==========================================
if __name__ == "__main__":
    # 配置参数
    my_tickers = ["AAPL", "MSFT", "TSLA", "PG"]
    market_index = "SPY"  # 标普 500 指数 ETF

    # 定价时间窗口（取 3 年历史数据）
    start = "2023-06-01"
    end = "2026-06-01"

    # 分配权重 (权重和须为 1)
    # 科技与核心资产占大头，特斯拉冲高 Beta，宝洁平衡低 Beta 防御性
    my_weights = {"AAPL": 0.3, "MSFT": 0.3, "TSLA": 0.2, "PG": 0.2}

    # 当前美股无风险收益基准 (参考美国 10 年期国债收益率)
    current_us_rf = 0.045

    # 运行模型
    summary, details = build_us_stock_capm_portfolio(
        tickers=my_tickers,
        market_ticker=market_index,
        start_date=start,
        end_date=end,
        weights=my_weights,
        rf_annual=current_us_rf,
    )

    # 输出量化分析报告
    print("\n" + "=" * 20 + " 1. 美股单资产 CAPM 详情 " + "=" * 20)
    print(
        details[
            [
                "Weight",
                "Beta",
                "CAPM_Expected_Return_Annual",
                "Historical_Return_Annual",
            ]
        ].to_string(formatters={k: "{:.2%}".format for k in details.columns if k != "Beta"})
    )

    print("\n" + "=" * 20 + " 2. 最终投资组合汇总报告 " + "=" * 20)
    print(f"组合总体 Beta 敞口: {summary['Portfolio_Beta']:.3f}")
    print(f"组合 CAPM 理论年化收益率: {summary['Portfolio_CAPM_Expected_Return_Annual']:.2%}")
    print(f"组合 实际历史年化收益率: {summary['Portfolio_Historical_Return_Annual']:.2%}")