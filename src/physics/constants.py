# Constants for Radar and Physics
import numpy as np

# --- Physical Constants ---
C = 3e8                # Speed of light in vacuum (m/s)
K_BOLTZMANN = 1.38e-23 # Boltzmann constant (J/K)

# --- Radar Specifications ---
F_RADAR = 8e9          # Operating frequency in X-band (8 GHz)
BANDWIDTH = 5e6        # Radar signal bandwidth (5 MHz)
P_TRANSMITTED = 5e4    # Peak transmitted power (50 kW)
ANTENNA_GAIN = 2000    # Linear power gain of the antenna
# Standard deviation of the thermal noise (Sigma Noise)
# Calculated as sqrt(k * T * B) where T = 290K
SIGMA_NOISE = np.sqrt(K_BOLTZMANN * 290 * BANDWIDTH) 

# --- Simulation Parameters ---
PFA = 1e-5             # Target Probability of False Alarm