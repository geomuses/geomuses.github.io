import pandas as pd
import requests
import yfinance as yf
import os

def get_sp500_tickers():
    """从维基百科安全抓取标普 500 代码"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {"User-Agent": "Mozilla/5.0"} # 伪装浏览器，破解 403
    
    response = requests.get(url, headers=headers)
    # 明确指定只抓取 id 为 constituents 的那个表格
    df = pd.read_html(response.text, attrs={'id': 'constituents'})[0]
    
    # 格式化代码（将 BRK.B 转为 BRK-B 以兼容 yfinance）
    tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
    return tickers

def batch_download_to_csv(tickers, folder="sp500_data"):
    """批量下载日线数据"""
    if not os.path.exists(folder):
        os.makedirs(folder)

    print(f"开始批量下载 {len(tickers)} 只股票的数据...")
    
    # threads=True 开启多线程加速
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', threads=True)

    for ticker in tickers:
        try:
            # 解决 MultiIndex 导致的 ValueError
            stock_df = data[ticker].copy()
            stock_df.dropna(how='all', inplace=True) # 去除空行
            
            if not stock_df.empty:
                stock_df.to_csv(f"{folder}/{ticker}.csv")
        except Exception as e:
            print(f"跳过 {ticker}: {e}")

if __name__ == "__main__":
    symbols = get_sp500_tickers()
    # 先打印前 5 个确认一下
    print("代码示例:", symbols[:5]) 
    
    # 执行下载
    # batch_download_to_csv(symbols)