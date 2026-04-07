import numpy as np

class RadarGeometry: 
    @staticmethod
    def get_distance(pos1, pos2): 
        """
        Calculates the Euclidean distance between two points in 3D.
        """
        return np.linalg.norm(np.array(pos1) - np.array(pos2))
    
    @staticmethod
    def cartesian_to_spherical(target_pos, radar_pos):
        """
        Converts Cartesian coordinates to Spherical (R, Azimuth, Elevation).
        Azimuth (theta): Angle in the XY plane (-pi to pi).
        Elevation (phi): Angle from the XY plane to the target (-pi/2 to pi/2).
        """
        target_pos = np.array(target_pos)
        radar_pos = np.array(radar_pos)
        
        # Relative vector
        rel_pos = target_pos - radar_pos
        x, y, z = rel_pos
        
        # Range (Distance)
        R = np.linalg.norm(rel_pos)
        
        if R < 1e-6: # Avoid division by zero if target is ON the radar
            return 0.0, 0.0, 0.0
            
        # Azimuth (theta) using arctan2 for all 4 quadrants
        theta = np.arctan2(y, x)
        
        # Elevation (phi) - angle from horizontal plane
        phi = np.arcsin(z / R)
        
        return R, theta, phi
    
    @staticmethod
    def is_inside_cone(agent_pos, radar_pos, radar_direction, opening_angle_deg) -> bool: 
        """
        Checks if the agent is within the radar's detection cone.
        Uses the Dot Product between the normalized vectors.
        """
        agent_pos = np.array(agent_pos)
        radar_pos = np.array(radar_pos)
        radar_direction = np.array(radar_direction)

        # Vector from radar to agent
        agent_radar_vec = agent_pos - radar_pos
        dist = np.linalg.norm(agent_radar_vec)
        
        if dist < 1e-6: return True # Agent is on top of the radar
        
        # Normalize vectors for Dot Product
        unit_agent_radar = agent_radar_vec / dist
        unit_radar_dir = radar_direction / np.linalg.norm(radar_direction)
        
        # Calculate cosine of the angle between them
        # cos(alpha) = A . B (since vectors are normalized)
        cos_alpha = np.dot(unit_agent_radar, unit_radar_dir)
        
        # Calculate threshold (Opening angle is half-angle of the cone)
        # Convert to radians first
        threshold_rad = np.radians(opening_angle_deg / 2)
        cos_threshold = np.cos(threshold_rad)
        
        # LOGIC: Smaller angle means LARGER cosine
        # If cos_alpha >= cos_threshold, the agent is INSIDE
        return cos_alpha >= cos_threshold