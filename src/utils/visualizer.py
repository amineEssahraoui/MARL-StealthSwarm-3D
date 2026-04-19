import matplotlib.pyplot as plt
import numpy as np

class StealthVisualizer:
    def __init__(self, env):
        self.env = env
        plt.ion()
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')

    def draw_frame(self):
        # Clear the previous frame
        self.ax.clear()
        
        # Draw the Terrain (3D Surface)
        x = np.linspace(0, self.env.world.width, self.env.world.nx)
        y = np.linspace(0, self.env.world.length, self.env.world.ny)
        X, Y = np.meshgrid(x, y, indexing='ij')
        Z = self.env.world.terrain_map
        self.ax.plot_surface(X, Y, Z, cmap='terrain', alpha=0.6)
        
        # Draw the Radars (Red Triangles)
        for radar in self.env.radars:
            self.ax.scatter(radar.pos[0], radar.pos[1], radar.pos[2], 
                            color='red', marker='^', s=100, label=f'Radar {radar.id}')
            
        # Draw the Agents (Blue Circles = Alive, Black X = Dead)
        for agent in self.env.agents.values():
            if agent.is_alive:
                self.ax.scatter(agent.pos[0], agent.pos[1], agent.pos[2], color='blue', marker='o', s=50)
            else:
                self.ax.scatter(agent.pos[0], agent.pos[1], agent.pos[2], color='black', marker='x', s=50)
        
        # Set axis limits and labels to match the world boundaries
        self.ax.set_xlim([0, self.env.world.width])
        self.ax.set_ylim([0, self.env.world.length])
        self.ax.set_zlim([0, self.env.world.max_height])
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Altitude (Z) (m)')
        self.ax.set_title(f"Stealth Swarm Simulation - Step {self.env.current_step}")
        
        # Pause briefly so the plot has time to draw on the screen
        plt.pause(0.01)

    def show(self):
        # Turn off interactive mode and keep the final plot open
        plt.ioff()
        plt.show()