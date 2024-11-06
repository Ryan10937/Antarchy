
from entities.world import world

def run_episode(grid_world: world,episode,config):
  print('Starting Episode',episode)
    
  for step in range(config['num_timesteps']):
    grid_world.render()
    grid_world.entity_turns()
    grid_world.resolve_conflicts()


    
