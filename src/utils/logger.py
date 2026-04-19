import os
import csv

class TrainingLogger:
    def __init__(self, filepath="logs/training_data.csv"):
        self.filepath = filepath
        
        # Create the logs directory if it does not exist
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        
        # Open the CSV file in write mode ('w') and write the header row
        with open(self.filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Episode', 'Total_Reward', 'Survived_Agents', 'Steps', 'Success'])

    def log_episode(self, episode, total_reward, survived_agents, steps, success):
        """
        Appends the results of a single training episode to the CSV file.
        """
        with open(self.filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([episode, total_reward, survived_agents, steps, success])