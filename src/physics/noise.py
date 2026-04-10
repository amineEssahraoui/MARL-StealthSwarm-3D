import numpy as np
from .constants import SIGMA_NOISE

class NoiseModel:
    def __init__(self):
        """
        Initializes the noise model based on the thermal noise power.
        """
        # Noise floor power (N) in Watts, where N = sigma^2
        self.noise_floor = SIGMA_NOISE**2

    def generate_gaussian_noise(self, size=1):
        """
        Generates Additive White Gaussian Noise (AWGN) samples.
        The noise follows a Normal (Gaussian) distribution: Mean = 0, Std Dev = SIGMA_NOISE.
        """
        return np.random.normal(0, SIGMA_NOISE, size)

    def apply_noise_to_signal(self, pr_linear):
        """
        Adds a random noise sample to the received power (Pr).
        Formula: Y = Pr + Noise
        This represents the total power processed by the radar receiver.
        """
        # Generate one random noise sample
        noise_sample = self.generate_gaussian_noise()[0]
        return pr_linear + noise_sample

    def get_noise_floor_dbm(self):
        """
        Returns the constant noise floor in dBm (decibel-milliwatts).
        Formula: dBm = 10 * log10(Power / 1mW)
        Used for SNR analysis and visualization.
        """
        if self.noise_floor <= 0:
            return -np.inf
        return 10 * np.log10(self.noise_floor / 1e-3)