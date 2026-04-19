import numpy as np

class StealthWorld:
    def __init__(self, width=10000, length=10000, height=2000, resolution=100):
        """
        Initializes the 3D world with a terrain heightmap.
        - width, length, height: World dimensions in meters.
        - resolution: Distance between grid points (meters).
        """
        self.width = width
        self.length = length
        self.max_height = height
        self.resolution = resolution
        
        # Grid dimensions
        self.nx = int(width // resolution)
        self.ny = int(length // resolution)
        
        # Initialize terrain map (Z-axis values)
        self.terrain_map = np.zeros((self.nx, self.ny))

    def generate_terrain(self, complexity=0.5):
        """
        Generates terrain using a sum of sine/cosine waves.
        Formula: Z(x,y) = sum( A_i * sin(f_x*x) * cos(f_y*y) )
        """
        x = np.linspace(0, self.width, self.nx)
        y = np.linspace(0, self.length, self.ny)
        X, Y = np.meshgrid(x, y, indexing='ij')

        # Adding multiple octaves of waves for realism
        # Octave 1: Large hills
        self.terrain_map = 0.5 * self.max_height * complexity * (
            np.sin(0.5e-3 * X) * np.cos(0.5e-3 * Y)
        )
        # Octave 2: Smaller peaks
        self.terrain_map += 0.2 * self.max_height * complexity * (
            np.sin(2e-3 * X) * np.sin(1.5e-3 * Y)
        )
        
        # Ensure terrain is non-negative and clipped at max_height
        self.terrain_map = np.clip(self.terrain_map, 0, self.max_height)

    def get_height_at(self, x, y):
        """
        Returns the terrain height Z at coordinates (x, y).
        Uses grid indexing: ix = x / resolution
        """
        ix = int(np.clip(x // self.resolution, 0, self.nx - 1))
        iy = int(np.clip(y // self.resolution, 0, self.ny - 1))
        return self.terrain_map[ix, iy]

    def is_out_of_bounds(self, pos):
        """
        Checks if position [x, y, z] is outside world boundaries.
        """
        x, y, z = pos
        return (x < 0 or x >= self.width or 
                y < 0 or y >= self.length or 
                z < 0 or z >= self.max_height)

    def check_los(self, start_pos, end_pos, sampling_step=50):
        """
        Checks Line-of-Sight between two points (e.g., Radar and Agent).
        Logic: Sample points along the ray and check if point_z < terrain_z.
        Formula: P(t) = P_start + t * (P_end - P_start) where t in [0, 1]
        """
        start_pos = np.array(start_pos)
        end_pos = np.array(end_pos)
        distance = np.linalg.norm(end_pos - start_pos)
        
        # Number of samples based on distance and step
        num_samples = int(distance / sampling_step)
        if num_samples < 2: return True

        # Linear interpolation between start and end
        t_values = np.linspace(0, 1, num_samples)
        for t in t_values:
            # Current point on the ray
            current_pt = start_pos + t * (end_pos - start_pos)
            
            # Check if this point's altitude is below the ground at its location
            ground_h = self.get_height_at(current_pt[0], current_pt[1])
            if current_pt[2] < ground_h:
                return False # LoS blocked by terrain
                
        return True # Path is clear