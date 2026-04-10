import numpy as np
from src.physics.geometry import RadarGeometry
from src.physics.radar_core import RadarCore
from src.physics.rcs_models import RCSModels
from src.physics.noise import NoiseModel

class RadarEntity:
    def __init__(self, radar_id, pos, azimuth_speed=1.0, opening_angle=30.0, range_max=8000.0):
        self.id = radar_id
        self.pos = np.array(pos, dtype=float)
        self.azimuth_speed = azimuth_speed  # Degrees per step
        self.opening_angle = opening_angle  # Total cone width in degrees
        self.range_max = range_max
        self.current_azimuth = 0.0 # Initial rotation
        
        # Tools
        self.radar_physics = RadarCore()
        self.noise_engine = NoiseModel()

    def update_scan(self, dt=1.0):
        """ Rotates the radar beam over time """
        self.current_azimuth = (self.current_azimuth + self.azimuth_speed * dt) % 360

    def get_direction_vector(self):
        """ Converts current azimuth angle to a 3D unit vector """
        rad = np.radians(self.current_azimuth)
        return np.array([np.cos(rad), np.sin(rad), 0.0])

    def detect(self, agent, world):
        """ Full detection pipeline: Range -> Cone -> LoS -> Physics -> Pd """
        # 1. Geometry Check (Is the agent even in the ballpark?)
        dist = RadarGeometry.get_distance(self.pos, agent.pos)
        if dist > self.range_max: return False, 0.0
        
        # 2. Cone Check (Is the agent inside the radar beam?)
        radar_dir = self.get_direction_vector()
        if not RadarGeometry.is_inside_cone(agent.pos, self.pos, radar_dir, self.opening_angle):
            return False, 0.0
            
        # 3. Line of Sight Check (Is there a mountain in between?)
        if not world.check_los(self.pos, agent.pos):
            return False, 0.0
            
        # 4. Physics Calculation (Pr -> SNR -> Pd)
        wavelength = self.radar_physics.get_wavelength(8e9) # X-band
        rcs = agent.get_current_rcs(self.pos)
        
        pr = self.radar_physics.calculate_pr(rcs, dist, wavelength)
        snr_lin, _ = self.radar_physics.calculate_snr(pr)
        pd = self.radar_physics.calculate_pd(snr_lin)
        
        # 5. Stochastic Decision
        is_detected = self.radar_physics.check_detection(pd)
        return is_detected, pd

    def get_viz_data(self):
        """ Returns data for 3D visualization (Position and Beam Direction) """
        return {
            "pos": self.pos,
            "dir": self.get_direction_vector(),
            "angle": self.opening_angle,
            "range": self.range_max
        }

class AgentEntity:
    def __init__(self, agent_id, pos, velocity=np.array([20.0, 0.0, 0.0])):
        self.id = agent_id
        self.pos = np.array(pos, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.is_alive = True
        self.rcs_engine = RCSModels()

    def update_position(self, dt=1.0):
        """ Moves the agent in 3D space """
        if self.is_alive:
            self.pos += self.velocity * dt

    def get_current_rcs(self, radar_pos):
        """ Calculates RCS based on relative geometry to the radar """
        # Get relative spherical coordinates
        r, azimuth, elevation = RadarGeometry.cartesian_to_spherical(self.pos, radar_pos)
        # Get stealth RCS from the butterfly model
        return self.rcs_engine.calculate_stealth_rcs(azimuth, elevation)

    def get_viz_data(self):
        """ Returns data needed to draw the agent in 3D """
        return {
            "pos": self.pos,
            "alive": self.is_alive,
            "velocity": self.velocity
        }