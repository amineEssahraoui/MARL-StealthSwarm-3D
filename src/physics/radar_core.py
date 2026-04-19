import numpy as np
from scipy.special import chndtr  # Non-central chi-square cumulative distribution function
from .constants import C, P_TRANSMITTED, ANTENNA_GAIN, SIGMA_NOISE, PFA

class RadarCore:
    @staticmethod
    def get_wavelength(frequency):
        """
        Calculates wavelength (lambda) from frequency.
        Formula: lambda = c / f
        """
        return C / frequency

    @staticmethod
    def calculate_pr(rcs, distance, wavelength):
        """
        The Radar Range Equation.
        Formula: Pr = (Pt * G^2 * lambda^2 * sigma) / ((4 * pi)^3 * R^4)
        """
        # Pt and G are from constants.py
        numerator = P_TRANSMITTED * (ANTENNA_GAIN**2) * (wavelength**2) * rcs
        denominator = ((4 * np.pi)**3) * (distance**4)
        
        # Avoid division by zero if distance is extremely small
        return numerator / (denominator + 1e-10)

    @staticmethod
    def calculate_snr(pr):
        """
        Calculate Signal-to-Noise Ratio (SNR).
        Note: SIGMA_NOISE in constants.py is sqrt(N).
        """
        noise_power = SIGMA_NOISE**2
        snr_linear = pr / noise_power
        
        # SNR in dB for logging/analysis
        snr_db = 10 * np.log10(snr_linear + 1e-20)
        return snr_linear, snr_db

    @staticmethod
    def calculate_pd(snr_linear, pfa=PFA):
        """
        Calculates Probability of Detection (Pd) using the Marcum Q-function.
        For a steady target (Swerling 0), Pd = Q1(sqrt(2*SNR), sqrt(-2*ln(Pfa))).
        We use the relation: Q1(a, b) = 1 - ncx2.cdf(b^2, df=2, nc=a^2)
        """
        if snr_linear <= 0:
            return 0.0
        
        # Threshold calculation based on Pfa
        v_threshold = np.sqrt(-2 * np.log(pfa))
        
        # Marcum Q-function parameters
        a = np.sqrt(2 * snr_linear)
        b = v_threshold
        
        # Using scipy.special.chndtr (Non-central chi-square) 
        # to compute 1 - MarcumQ
        # chndtr(x, df, nc) -> x = b^2, df = 2, nc = a^2
        pd = 1 - chndtr(b**2, 2, a**2)
        
        return np.clip(pd, 0, 1)

    @staticmethod
    def check_detection(pd):
        """
        Probabilistic check to see if the radar detects the agent.
        """
        return np.random.random() < pd