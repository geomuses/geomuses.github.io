from edgar import *
import polars as pl
# 必须设置身份：姓名 <邮箱>
set_identity("boonhong56505@gmail.com")

# 获取公司对象（支持 Ticker 或 CIK）
company = Company("AAPL")

# 获取最新的财务数据对象
financials = company.get_financials()

# 获取三大报表 (自动返回 Pandas DataFrame)
income_stmt = financials.income_statement()  # 利润表
balance_sheet = financials.balance_sheet()   # 资产负债表
cash_flow = financials.cash_flow_statement() # 现金流量表

# 先转为 Pandas，再转为 Polars
df_pl = pl.from_pandas(income_stmt.to_dataframe(), include_index=True)

print(df_pl)