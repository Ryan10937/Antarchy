
from entities.world import world
import time
import os
def run_episode(grid_world: world,episode,config):
  print('Starting Episode',episode)
    
  for step in range(config['num_timesteps']):
    grid_world.render()
    grid_world.entity_turns()
    grid_world.log_state(episode,step,step==config['num_timesteps']-1)
    time.sleep(0.3)

  waiting_count=0
  waiting_timeout=10
  while len(os.listdir(grid_world.state_log_folder)) > 1:
    grid_world.log(f'waiting for godot to read and delete files {waiting_count}')
    if waiting_count >= waiting_timeout:
      grid_world.log('Breaking wait, timeout reached')
      break
    waiting_count+=1
    time.sleep(1)
  grid_world.clean_state_logs()

    
