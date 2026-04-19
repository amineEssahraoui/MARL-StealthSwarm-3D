import numpy as np
from src.env.world import StealthWorld
from src.env.entities import AgentEntity, RadarEntity

class StealthEngine:
    def __init__(self, num_agents=6, num_radars=2, max_steps=1000, failure_threshold=0.5):
        self.num_agents = num_agents
        self.num_radars = num_radars
        self.max_steps = max_steps
        self.current_step = 0
        self.dt = 1.0  # Time step resolution
        
        # Percentage of dead agents that triggers the end of the episode (e.g., 0.5 = 50%)
        self.failure_threshold = failure_threshold 

        # Initialize the terrain orchestrator
        self.world = StealthWorld()
        
        # Using a dictionary for agents makes it easier to match actions to agent IDs
        self.agents = {} 
        self.radars = []

    def reset(self):
        """
        Resets the simulation to step 0, generates a new map, and respawns entities.
        """
        self.current_step = 0
        
        # Regenerate terrain for variety
        self.world.generate_terrain()

        # Spawn Radars at fixed locations BUT ON TOP of the terrain
        self.radars = []
        for i in range(self.num_radars):
            # Spread radars apart (e.g., Radar 0 at X=2000, Radar 1 at X=6000)
            x = 2000 + (i * 4000)
            y = 2000 + (i * 4000)
            
            # Fetch the terrain height at (x, y) so the radar doesn't spawn underground
            z = self.world.get_height_at(x, y)
            
            spawn_pos = [x, y, z]
            self.radars.append(RadarEntity(radar_id=i, pos=spawn_pos))

        # Spawn Agents at random locations in the sky
        self.agents = {}
        for i in range(self.num_agents):
            random_pos = [
                np.random.uniform(0, self.world.width),       # Random X
                np.random.uniform(0, self.world.length),      # Random Y
                np.random.uniform(1000, self.world.max_height) # Random altitude (Z)
            ]
            self.agents[i] = AgentEntity(agent_id=i, pos=random_pos)

        # Return initial observations
        return self._get_observations()

    def step(self, actions):
        """
        Advances the world by one tick. 
        actions expected format: {agent_id: new_velocity_vector}
        """
        self.current_step += 1
        
        # Move Agents
        for agent_id, new_velocity in actions.items():
            if agent_id in self.agents and self.agents[agent_id].is_alive:
                self.agents[agent_id].velocity = new_velocity
                self.agents[agent_id].update_position(dt=self.dt)
        
        # Spin Radars
        for radar in self.radars:
            radar.update_scan(dt=self.dt)
            
        # Check Detections & Calculate Rewards
        rewards = {}
        dones = {}
        dead_count = 0  # Counter to track how many agents are dead
        
        for agent_id, agent in self.agents.items():
            # If agent is already dead, skip logic
            if not agent.is_alive:
                dones[agent_id] = True
                rewards[agent_id] = 0.0
                dead_count += 1
                continue
            
            # Assume survival for now
            dones[agent_id] = False
            rewards[agent_id] = 0.1  # Small reward for surviving this step
            
            # Check against all radars
            for radar in self.radars:
                is_detected, pd = radar.detect(agent, self.world)
                
                if is_detected:
                    agent.is_alive = False
                    dones[agent_id] = True
                    rewards[agent_id] = -100.0  # Massive penalty for detection
                    dead_count += 1
                    print(f"Agent {agent_id} detected by Radar {radar.id} !!")
                    break  # Skip checking other radars, agent is already dead
        
        # Check if the simulation is over
        # Did we exceed the failure threshold? (EX: 50% of the swarm is dead)
        swarm_failure = (dead_count / self.num_agents) >= self.failure_threshold
        # Did we reach the max time limit?
        max_time_reached = self.current_step >= self.max_steps
        
        env_done = swarm_failure or max_time_reached
        
        return self._get_observations(), rewards, dones, env_done

    def _get_observations(self):
        """
        Collects what each alive agent knows about itself.
        """
        obs = {}
        for agent_id, agent in self.agents.items():
            if agent.is_alive:
                obs[agent_id] = {
                    "pos": agent.pos.copy(),
                    "velocity": agent.velocity.copy()
                }
        return obs