import sys
import os
import numpy as np

# Add the root directory to sys.path so Python can find the 'src' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.env.engine import StealthEngine

def run_random_test():
    print("--- Starting Stealth Engine Sanity Check ---\n")
    
    # Initialize the Engine
    # We use 50 steps just for a quick test
    env = StealthEngine(num_agents=6, num_radars=2, max_steps=50, failure_threshold=0.5)
    
    # 2. Reset the environment (Generate terrain, spawn entities)
    obs = env.reset()
    print("Environment Reset Successfully!")
    print(f"Spawned {len(env.agents)} Agents and {len(env.radars)} Radars.\n")
    
    # Start the Simulation Loop
    for step in range(env.max_steps):
        
        # Create random actions (velocities) for each alive agent
        actions = {}
        for agent_id, agent in env.agents.items():
            if agent.is_alive:
                # Random velocity: [vx, vy, vz] between -50 and 50 m/s
                random_vel = np.random.uniform(-50, 50, size=3)
                actions[agent_id] = random_vel
                
        # Advance the environment by one step
        obs, rewards, dones, env_done = env.step(actions)
        
        # Check if the episode ended early (e.g., swarm failure)
        if env_done:
            print(f"\n[!] Episode finished early at Step {env.current_step}!")
            print("Reason: Maximum steps reached OR Failure threshold exceeded.")
            break
            
    # Final Status Report
    print("\n--- Final Swarm Status ---")
    alive_count = sum(1 for a in env.agents.values() if a.is_alive)
    print(f"Agents Survived: {alive_count} / {env.num_agents}")

if __name__ == "__main__":
    run_random_test()