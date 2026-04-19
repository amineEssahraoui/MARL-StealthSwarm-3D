import matplotlib.pyplot as plt
import numpy as np

class StealthVisualizer:
    def __init__(self, env):
        self.env = env
        plt.ion()
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')

    