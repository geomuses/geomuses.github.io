import yfinance as yf
from edgar import set_identity, Company
import pandas as pd

# 1. 必须步骤：设置 SEC Edgar 身份识别（请替换为您自己的真实名称和 Email）
set_identity("boonhong565059@gmail.com")

def get_latest_price(ticker):
    """获取最新收盘价"""
    stock = yf.Ticker(ticker)
    todays_data = stock.history(period='1d')
    return todays_data['Close'].iloc[0]

def get_ttm_eps_from_edgar(ticker):
    """
    通过 edgartools 获取过去四季(TTM)的 EPS (Basic)
    注意：为了计算准确的 TTM，我们需要提取过去四个季度的 EPS 并相加
    """
    # 实例化公司对象
    company = Company(ticker)
    
    # 获取公司的财务事实数据 (Facts)
    facts = company.get_facts()
    
    # 美股标准的 GAAP 财报中，基本每股盈余通常记录在 'EarningsPerShareBasic' 中
    # 或者是 'EarningsPerShareDiluted' (稀释每股盈余，更为保守评估时使用)
    eps_facts = facts.get_fact("EarningsPerShareBasic", gaap="us-gaap")
    
    if eps_facts is None:
        raise ValueError(f"无法在 SEC 数据库中找到 {ticker} 的 EPS 数据。")
        
    # 将数据转换为 Pandas DataFrame 方便清洗
    df = pd.DataFrame(eps_facts.data)
    
    # 过滤出季度报表 (10-Q) 的数据
    # SEC 的 10-Q 数据通常形式为：form='10-Q',且 frame 代表特定的季度(如 CY2025Q3)
    # 或者是根据 end 与 start 的时间差约为 90 天来筛选
    df_10q = df[df['form'] == '10-Q'].copy()
    
    # 转换为日期格式并排序
    df_10q['end'] = pd.to_datetime(df_10q['end'])
    df_10q = df_10q.sort_values(by='end', ascending=False)
    
    # 移除重复的季度数据（取最新修正的版本）
    df_10q = df_10q.drop_duplicates(subset=['frame'], keep='first')
    
    # 取得最近的 4 个季度数据
    recent_4_quarters = df_10q.head(4)
    
    if len(recent_4_quarters) < 4:
        # 如果季度数据不足，退而求其次寻找最新 10-K (年报) 的年度 EPS
        df_10k = df[df['form'] == '10-K'].copy()
        df_10k['end'] = pd.to_datetime(df_10k['end'])
        latest_10k = df_10k.sort_values(by='end', ascending=False).iloc[0]
        print(f"⚠️ 季度数据不足，采用最新 10-K 年报 EPS (日期: {latest_10k['end'].strftime('%Y-%m-%d')})")
        return float(latest_10k['value'])
        
    # 将过去四个季度的 EPS 加总，得到 TTM EPS
    ttm_eps = recent_4_quarters['value'].sum()
    
    print(f"--- {ticker} 过去四季 EPS 明细 ---")
    for idx, row in recent_4_quarters.iterrows():
        print(f"季度: {row['frame']} | 截止日期: {row['end'].strftime('%Y-%m-%d')} | EPS: ${row['value']:.2f}")
    print(f"累计 TTM EPS: ${ttm_eps:.2f}")
    print("-" * 30)
    
    return float(ttm_eps)

# --- 主程序执行 ---
if __name__ == "__main__":
    target_ticker = "AAPL"  # 可以更换为其他美股标的，如 MSFT, NVDA
    
    try:
        # 获取最新股价
        price = get_latest_price(target_ticker)
        print(f"{target_ticker} 当前最新股价: ${price:.2f}")
        
        # 获取 TTM EPS
        eps = get_ttm_eps_from_edgar(target_ticker)
        
        # 计算本益比
        if eps > 0:
            pe_ratio = price / eps
            print("計算结果：")
            print(f"👉 {target_ticker} 的历史本益比 (Trailing P/E) 为: {pe_ratio:.2f} 倍")
        else:
            print(f"👉 {target_ticker} 过去 TTM EPS 为负数 (${eps:.2f})，无法计算常规本益比。")
            
    except Exception as e:
        print(f"计算执行失败，原因: {e}")