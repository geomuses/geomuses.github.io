from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUMY)
ret, data = trd_ctx.accinfo_query()
if ret == RET_OK:
    print("可用资金: ", data['us_avl_withdrawal_cash'][0]) 
else:
    print('accinfo_query error: ', data)
    
trd_ctx.close()  # 关闭当条连接