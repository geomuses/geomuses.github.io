---
layout: post
title: quant Bayesian optimization
date: 2026-04-22 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - quant
  - python
---

**贝叶斯优化 (Bayesian Optimization)** 是一种专门针对**黑盒函数 (Black-box functions)** 进行全局优化的强大算法。它非常适合那些评估成本极高、没有解析表达式、或者无法计算导数的场景

|**方法**|**优点**|**缺点**|
|---|---|---|
|**网格搜索**|简单、全面|存在“维度灾难”，非常耗时|
|**随机搜索**|比网格搜索快，易并行|纯靠运气，没有利用历史信息|
|**贝叶斯优化**|**样本效率极高**，迭代次数少|序列化进行（难以并行），单次计算有开销|

```bash
pip install bayesian-optimization
```

# 优化一个复杂的数学函数

假设我们要寻找函数 $f(x,y)=−x^2−(y−1)^2+1$ 的最大值

```python
from bayes_opt import BayesianOptimization

# 1. 定义我们要优化的目标函数
def black_box_function(x, y):
    return -x ** 2 - (y - 1) ** 2 + 1

# 2. 确定参数的搜索范围 (Bounds)
pbounds = {'x': (-2, 2), 'y': (-3, 3)}

# 3. 初始化优化器
optimizer = BayesianOptimization(
    f=black_box_function,
    pbounds=pbounds,
    random_state=1,
)

# 4. 执行优化
# init_points: 初始随机搜索点数
# n_iter: 迭代次数（贝叶斯引导的搜索）
optimizer.maximize(
    init_points=2,
    n_iter=10,
)

# 5. 输出结果
print("最佳参数:", optimizer.max['params'])
print("最大值:", optimizer.max['target'])
```

# 进阶库推荐

除了上面的库，如果你的目标是**深度学习或复杂的机器学习管道**，可以考虑以下更强大的工具：

1. **Optuna (推荐)**: 目前工业界最火。支持异步并行、剪枝（提前停止不希望的实验），语法非常灵活。
    
2. **Hyperopt**: 基于 TPE 算法，适合大规模搜索空间。
    
3. **Scikit-Optimize (skopt)**: 与 Scikit-learn 兼容性极佳