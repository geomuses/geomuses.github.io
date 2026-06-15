---
layout: post
title: 量化金融 投资组合 Ledoit-Wolf 收缩(Shrinkage)技术
date: 2026-06-17 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - python
---
当投资组合中的**资产数量 N 逐渐增加**，或者我们缩短历史观测窗口 T（导致 N 接近甚至大于 T）时，传统的样本协方差矩阵（Sample Covariance Matrix）会陷入所谓的“维数灾难”

在这种情况下，矩阵求逆会变得极其不稳定，极易放大噪声，导致马氏距离失效，而马科维茨优化模型计算出的资产权重也会出现极端扭曲（比如对某些资产严重做空或全仓买入）

**Ledoit-Wolf 收缩（Shrinkage）技术**正是为了解决这个量化金融的核心痛点而诞生的。它的本质是在“低偏差、高方差”**的样本协方差矩阵与**“高偏差、低方差”的结构化目标矩阵之间寻找一个完美的统计学平衡

...

https://gemini.google.com/app/cc8583373dfe2022