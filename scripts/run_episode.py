
from entities.world import world
import time
import os
import numpy as np
def run_episode(grid_world: world,episode,config):
  print('Starting Episode',episode)
  timestep_times=[]
  for step in range(config['num_timesteps']):
    timestep_start = time.time()
    if grid_world.check_for_end_conditions():
      break
    grid_world.render()
    grid_world.entity_turns()#step to next state
    # time.sleep(0.25)

    # grid_world.log_state(episode,step,step==config['num_timesteps']-1)
    timestep_end = time.time()
    timestep_times.append(timestep_end-timestep_start)
    
  print('Average timestep (s)',np.mean(timestep_times))
  grid_world.save_history()
  grid_world.train_models(epochs=20)
  episode_stats = grid_world.get_stats() 
  return episode_stats
  # waiting_count=0
  # waiting_timeout=10
  # while len(os.listdir(grid_world.state_log_folder)) > 1:
  #   grid_world.log(f'waiting for godot to read and delete files {waiting_count}')
  #   if waiting_count >= waiting_timeout:
  #     grid_world.log('Breaking wait, timeout reached')
  #     break
  #   waiting_count+=1
  #   # time.sleep(1)
  # # grid_world.clean_state_logs()

    
