num = 1 
try:
    print("你输入的是：", num)
except ValueError:
    print("输入无效，请输入整数")
finally:   
	print("无论输入正确还是报错，都会执行")