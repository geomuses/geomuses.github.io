import numpy as np
from scipy.optimize import minimize

def nss_model(t, b0, b1, b2, b3, tau1, tau2):
    """Calculates the yield for maturity t using NSS parameters."""
    # Handle the t=0 case to avoid division by zero
    t = np.where(t == 0, 1e-6, t)
    
    term1 = b1 * (1 - np.exp(-t/tau1)) / (t/tau1)
    term2 = b2 * ((1 - np.exp(-t/tau1)) / (t/tau1) - np.exp(-t/tau1))
    term3 = b3 * ((1 - np.exp(-t/tau2)) / (t/tau2) - np.exp(-t/tau2))
    
    return b0 + term1 + term2 + term3

def objective_function(params, t_market, y_market):
    """Residual sum of squares to minimize."""
    y_pred = nss_model(t_market, *params)
    return np.sum((y_market - y_pred)**2)

# Market data: Maturities (years) and corresponding Yields (%)
maturities = np.array([0.25, 0.5, 1, 2, 3, 5, 10, 30])
yields = np.array([0.051, 0.052, 0.050, 0.048, 0.045, 0.042, 0.040, 0.043])

# Initial guesses [b0, b1, b2, b3, tau1, tau2]
initial_guess = [0.04, -0.01, 0.01, 0.01, 1.0, 5.0]

result = minimize(objective_function, initial_guess, args=(maturities, yields))
best_params = result.x

print(f"Optimized Parameters:\nB0: {best_params[0]:.4f} (Level)\nB1: {best_params[1]:.4f} (Slope)\n"
      f"B2: {best_params[2]:.4f} (Hump 1)\nB3: {best_params[3]:.4f} (Hump 2)")

# print(best_params)

y_pred = nss_model(maturities, *best_params)
# print(y_pred)

import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

plt.plot(maturities, yields, 'o', label='Market Data')
plt.plot(maturities, y_pred, '-', label='Fitted Curve')
plt.legend()
plt.show()