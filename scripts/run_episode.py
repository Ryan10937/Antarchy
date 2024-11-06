
from entities.world import world

def run_episode(grid_world: world,episode,config):
  print('Starting Episode',episode)
  grid_world.place_food()
  grid_world.place_ants()
    
  for step in config['num_timesteps']:
    grid_world.render()

    grid_world.resolve_conflicts()

    
