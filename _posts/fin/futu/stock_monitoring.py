from futu import *

# 1. 建立连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 2. 获取英伟达的市场快照
# US.NVDA 是英伟达在 Futu/Moomoo 中的代码
ret, data = quote_ctx.get_market_snapshot(['US.NVDA'])

if ret == RET_OK:
    # 提取 EPS 字段
    # eps: 每股收益 (通常指 TTM)
    nvda_eps = data['eps'][0]
    print(f"英伟达当前 EPS (TTM): {nvda_eps}")
else:
    print('获取数据失败: ', data)

# 3. 关闭连接
quote_ctx.close()