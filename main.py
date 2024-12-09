
import argparse
import yaml
from scripts.run_episode import run_episode
from entities.world import world
import tensorflow as tf
if __name__ == '__main__':

  print(tf.config.list_physical_devices('GPU'))
  tf.config.run_functions_eagerly(True)
  parser = argparse.ArgumentParser()
  parser.add_argument('--config',type=str)
  args = parser.parse_args()

  with open(args.config,'r') as f:
    config = yaml.safe_load(f)


  grid_world = world(
    x_size=config['grid_size_x'],
    y_size=config['grid_size_y'],
    num_ants=config['ants'],
    num_food=config['food'],
    config=config
    )
  
  for episode in range(config['episodes']):
    run_episode(grid_world,episode,config)


