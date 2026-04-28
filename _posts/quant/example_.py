import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib import style
style.use('ggplot')

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


maturities = np.array([0.25,0.5,0.75,1,2,3,4,5,7,10])
yields = np.array([0.6840,0.8220,0.8870,0.9120,0.9920,1.1650,1.3230,1.4610,1.6390,1.7840])/100

# Initial guesses [b0, b1, b2, b3, tau1, tau2]
initial_guess = [0.04, -0.01, 0.01, 0.01, 1.0, 5.0]

result = minimize(objective_function, initial_guess, args=(maturities, yields))
best_params = result.x
y_pred = nss_model(maturities, *best_params)

plt.plot(maturities, yields, 'o-', label='Market Data')
plt.plot(maturities, y_pred, '--',label='Fitted Curve')
plt.legend()
plt.show()