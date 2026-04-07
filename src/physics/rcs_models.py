import numpy as np
from .constants import F_RADAR, C

class RCSModels:
    def __init__(self):
        """
        Initializes the RCS model with physical constants from the radar.
        """
        self.wavelength = C / F_RADAR
        self.k = (2 * np.pi) / self.wavelength # Wave number

    @staticmethod
    def get_static_rcs(base_rcs=0.1):
        """
        Simple constant RCS for baseline testing.
        Value in square meters (m^2).
        """
        return base_rcs

    def calculate_stealth_rcs(self, azimuth, elevation, length=2.0, width=0.5):
        """
        Calculates a physics-based Stealth RCS using a 'Butterfly' pattern.
        - Low RCS at front (0 rad) and back (pi rad).
        - High RCS at sides (pi/2 and 3pi/2 rad).
        
        Formula: sigma = sigma_max * |sinc(k * L * cos(theta)/pi)|^2 * |sin(phi)|
        """
        # Calculate Maximum RCS (Peak reflection of a flat plate)
        surface_area = length * width
        sigma_max = (4 * np.pi * (surface_area**2)) / (self.wavelength**2)

        # Azimuth Dependency (The Stealth Butterfly Effect)
        # We use cos(azimuth) because sinc(0)=1. 
        # When azimuth = pi/2 (90 deg), cos = 0 -> Peak RCS.
        # We divide by pi because np.sinc(x) calculates sin(pi*x)/(pi*x).
        az_arg = (self.k * length * np.cos(azimuth)) / np.pi
        az_factor = np.abs(np.sinc(az_arg))**2

        # Elevation Dependency
        # Looking from top (phi = pi/2) gives max surface area.
        # Looking from the side (phi = 0) gives minimum thickness.
        el_factor = np.abs(np.sin(elevation))

        # Final RCS calculation with a floor value
        # Floor value (1e-4) ensures the agent is never 100% invisible
        sigma_total = sigma_max * az_factor * el_factor
        
        return max(sigma_total, 1e-4)

    def get_dynamic_rcs(self, azimuth, elevation, agent_type="stealth"):
        """
        A wrapper to select between different RCS models.
        """
        if agent_type == "static":
            return self.get_static_rcs()
        elif agent_type == "stealth":
            return self.calculate_stealth_rcs(azimuth, elevation)
        else:
            # Default to a small constant value
            return 0.1