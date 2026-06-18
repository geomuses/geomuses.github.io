---
layout: post
title: 量化金融 投资组合 python模型
date: 2026-06-19 09:01:00 +0800
image: 21.jpg
tags:
  - financial
  - python
---

```python
import numpy as np
import pandas as pd
from .base_model import BaseModel
```

```python
class MinVolatilityModel(BaseModel):
    name  = "Min Volatility"
    code  = "MV"
    color = "#2ecc71"

    def compute_weights(self, returns_window: pd.DataFrame) -> np.ndarray:
        n = returns_window.shape[1]
        mean_ret = returns_window.mean() * 252
        cov_mat  = returns_window.cov()  * 252

        def objective(w, mu, cov, rf=None):
            return np.sqrt(np.dot(w.T, np.dot(cov.values, w)))

        constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(n))
        x0 = np.full(n, 1.0 / n)

        res = minimize(objective, x0,
                       args=(mean_ret, cov_mat),
                       method="SLSQP", bounds=bounds,
                       constraints=constraints,
                       options={"ftol": 1e-9, "maxiter": 1000})
        return res.x if res.success else x0

```


```python
class MaxSharpeModel(BaseModel):
    name  = "Max Sharpe"
    code  = "MSR"
    color = "#e74c3c"

    def __init__(self, rf: float = RISK_FREE_RATE):
        self.rf = rf

    def compute_weights(self, returns_window: pd.DataFrame) -> np.ndarray:
        n = returns_window.shape[1]
        mean_ret = returns_window.mean() * 252
        cov_mat  = returns_window.cov()  * 252

        def neg_sharpe(w, mu, cov, rf):
            p_ret = np.sum(mu * w)
            p_std = np.sqrt(np.dot(w.T, np.dot(cov.values, w)))
            return -(p_ret - rf) / p_std if p_std > 1e-8 else 0

        constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(n))
        x0 = np.full(n, 1.0 / n)

        res = minimize(neg_sharpe, x0,
                       args=(mean_ret, cov_mat, self.rf),
                       method="SLSQP", bounds=bounds,
                       constraints=constraints,
                       options={"ftol": 1e-9, "maxiter": 1000})
        return res.x if res.success else x0
```

```python
DEFAULT_P = np.array([
    [1, -1, 0, 0],   # 观点1：资产0 跑赢 资产1 +2%
    [0,  0, 1, 0],   # 观点2：资产2 绝对收益 +10%
])
DEFAULT_Q   = np.array([0.02, 0.10])
DEFAULT_TAU = 0.05


class BlackLittermanModel(BaseModel):
    name  = "Black-Litterman"
    code  = "BL"
    color = "#3498db"

    def __init__(self,
                 P:   np.ndarray = DEFAULT_P,
                 Q:   np.ndarray = DEFAULT_Q,
                 tau: float      = DEFAULT_TAU):
        self.P   = P
        self.Q   = Q
        self.tau = tau

    def compute_weights(self, returns_window: pd.DataFrame) -> np.ndarray:
        n        = returns_window.shape[1]
        cov_mat  = returns_window.cov().values * 252
        mkt_w    = np.full(n, 1.0 / n)

        market_var = mkt_w @ cov_mat @ mkt_w
        delta      = max(0.08 / market_var, 0.1)
        pi         = delta * (cov_mat @ mkt_w)

        omega      = np.diag(np.diag(self.P @ (self.tau * cov_mat) @ self.P.T))
        term1_inv  = np.linalg.inv(self.tau * cov_mat)
        term2_inv  = self.P.T @ np.linalg.inv(omega) @ self.P

        mu_bl = np.linalg.inv(term1_inv + term2_inv) @ (
            term1_inv @ pi + self.P.T @ np.linalg.inv(omega) @ self.Q
        )

        raw_w = np.linalg.inv(delta * cov_mat) @ mu_bl
        raw_w = np.maximum(raw_w, 0)
        total = raw_w.sum()
        return raw_w / total if total > 1e-8 else mkt_w
```

```python
class EqualWeightModel(BaseModel):
    name  = "Equal Weight"
    code  = "EW"
    color = "#888888"

    def compute_weights(self, returns_window: pd.DataFrame) -> np.ndarray:
        n = returns_window.shape[1]
        return np.full(n, 1.0 / n)

```