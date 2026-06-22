---
layout: post
title:  python decorator
date:   2026-06-22 09:01:00 +0800
image: 04.jpg
tags: 
    - python
---

语法糖

```python
#!bin/python3
def disabled(f):
    def wrapper(*args, **kwargs):
        # 内部什么都不做，直接跳过原函数的执行
        pass
    return wrapper
    
@disabled
def my_function():
    print("This function can no longer be called...")

if __name__ == '__main__':
    my_function()
```

会拒绝访问`my function`

```python
#!bin/python3
def disabled(f):
    def wrapper(*args, **kwargs):
        # 核心改动：在这里真正调用原函数 f，并把它的结果返回
        return f(*args, **kwargs) 
    return wrapper
    
@disabled
def my_function():
    print("This function can no longer be called...")

if __name__ == '__main__':
    my_function()
```

建立`class`的语法糖

```python
class Decorator(object):
	"""Simple decorator class."""
	def __init__(self, func):
		self.func = func
		
	def __call__(self, *args, **kwargs):
		print('Before the function call.')
		res = self.func(*args, **kwargs)
		print('After the function call.')
		return res
		
@Decorator
def testfunc():
	print('Inside the function.')

testfunc()
# Before the function call.
# Inside the function.
# After the function call.
```