---
tags:
  - decks
---
## 什么是 CAPM 模型的系统性风险？

在资本资产定价模型中，系统性风险用 **Beta ($\beta$)** 表示。
它衡量的是单只资产相对于整个市场的波动敏感度。

## 如何用 Python Polars 创建 DataFrame？

```python
import polars as pl
df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
```

## CAPM 中 Beta 大于 1 代表什么？

Beta > 1 表示该资产的波动幅度**高于**市场平均水平；Beta < 1 则低于市场。

## Polars 与 Pandas 的主要区别是什么？

Polars 基于 Rust 实现，默认使用惰性求值（LazyFrame）与列式存储，在大数据集上通常比 Pandas 更快、内存效率更高。

## 概念速查

| 概念 | 说明 |
| --- | --- |
| 系统性风险 | 无法通过分散投资消除的市场整体风险 |
| Beta ($\beta$) | 资产收益对市场收益变动的敏感度 |
| `pl.DataFrame` | Polars 中存储表格数据的核心结构 |
| 对数收益率 | $\ln(P_t / P_{t-1})$，便于时间序列加总与统计建模 |

## 填空：CAPM 公式

资本资产定价模型的期望收益公式为 $E(R_i) = R_f + \beta_i \cdot (E(R_m) - R_f)$，其中 $R_f$ 是 ==无风险利率==，$E(R_m)$ 是 ==市场期望收益率==。

## 填空：Polars 读取 CSV

使用 `pl.==read_csv==("data.csv")` 从 CSV 文件读取数据。
