from futu import *

# 1. 建立连接 (默认监听本地 11111 端口)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 2. 获取美股苹果 (AAPL) 的实时快照
ret, data = quote_ctx.get_market_snapshot(['US.AAPL'])

if ret == RET_OK:
    # 打印当前的股价、涨跌幅、市盈率等
    print(data[['code', 'last_price', 'pe_ratio', 'update_time']])
else:
    print('错误:', data)

# 3. 养成好习惯，关闭连接
quote_ctx.close()