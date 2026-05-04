### 第一阶段：风险溢价与非线性相关性（第 1 - 10 天）

_目标：打破正态分布假设，解决 BL 模型在极端行情下的失效问题。_

- **Day 1-2：** 深入研究 **Hierarchical Risk Parity (HRP)**。使用 Python 的 `SciPy` 进行层次聚类，观察它在不依赖协变矩阵逆运算的情况下如何分配权重。
    
- **Day 3-4：** 引入 **Tail Risk** 建模。计算并对比 VaR 与 **CVaR**，理解在左侧尾部风险爆发时，组合的真实表现。
    
- **Day 5-6：** 学习 **Copula Functions**。在 Python 中实现对资产间非线性相关性的描述（如 Gumbel 或 Clayton Copula），解决“大难临头各自飞”的相关性失效问题。
    
- **Day 7-8：** 实践 **Factor-based Asset Allocation**。不再按资产名分配，而是按 Macro、Carry、Value 等因子分配风险预算。
    
- **Day 9-10：** **阶段复盘**。在 **Obsidian** 中整理这 10 天的逻辑，用 O'Reilly 风格的黑白对比图表记录不同模型在历史波动期的表现差异。
### 第二阶段：因子工程与 Barra 风险体系（第 11 - 20 天）

_目标：像机构投资者一样剖析组合的收益来源（Attribution）。_

- **Day 11-12：** 构建 **Barra 风格因子库**。手动实现 Size, Momentum, Volatility 的因子值计算。
    
- **Day 13-14：** 运行 **Cross-sectional Regression**。学习如何将组合收益拆解为因子暴露（Exposure）与特异性收益（Idiosyncratic Return）。
    
- **Day 15-16：** 解决**因子拥挤度 (Factor Crowding)**。研究如何通过因子间的相关性变化，预判因子的失效或逆转。
    
- **Day 17-18：** 探索 **Cointegration (协整)**。在美股或 Crypto 市场寻找具有长线回归特性的资产对，编写 **Pairs Trading** 策略。
    
- **Day 19-20：** **工程化优化**。利用 `asyncio` 优化数据抓取效率，确保你的因子库更新速度能支撑后续的动态调仓。
### 第三阶段：贝叶斯进阶与机器学习实战（第 21 - 30 天）

_目标：将 Black-Litterman 中的“主观观点”自动化，构建自适应系统。_

- **Day 21-22：** **ML-Driven BL Model**。尝试用简单的随机森林或 LSTM 预测收益率，并将其作为 BL 模型中的 $Q$（View 向量）输入。
    
- **Day 23-24：** 学习 **Bayesian Linear Regression**。利用贝叶斯推断动态更新策略参数，而不是使用死板的固定系数。
    
- **Day 25-26：** 实践 **Walk-forward Analysis**。放弃简单的 Train/Test 分割，改用前进分析法验证策略在时间序列上的鲁棒性。
    
- **Day 27-28：** **Reinforcement Learning (RL) 雏形**。研究基于 Sharpe Ratio 为奖励函数的简单 Agent，观察它在调仓时的决策逻辑。