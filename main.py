
import argparse
import yaml
from scripts.run_episode import run_episode
from entities.world import world
import tensorflow as tf
import numpy as np
import random
import scripts.plot_episode_stats as pes
if __name__ == '__main__':

  print(tf.config.list_physical_devices('GPU'))
  parser = argparse.ArgumentParser()
  parser.add_argument('--config',type=str)
  parser.add_argument('--seed',type=int, required=False,default=-1)
  parser.add_argument('--control',type=bool, required=False,default=False)
  args = parser.parse_args()

  if args.seed != -1:
    print('Using seed: ',args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)

  with open(args.config,'r') as f:
    config = yaml.safe_load(f)

  episode_stats = []
  control_stats = []
  for episode in range(config['episodes']):
    if args.seed == -1:
      run_seed = random.random()
    else:
      run_seed = args.seed
    if args.control == True:
      try:  
        grid_world = world(
                    x_size=config['grid_size_x'],
                    y_size=config['grid_size_y'],
                    num_ants=config['ants'],
                    num_food=config['food'],
                    config=config,
                    seed=run_seed,
                    control=True
                    )
        control_stats.append(run_episode(grid_world,episode,config))
      except Exception as e:
        print(e)
    try:
      grid_world = world(
                  x_size=config['grid_size_x'],
                  y_size=config['grid_size_y'],
                  num_ants=config['ants'],
                  num_food=config['food'],
                  config=config,
                  seed=run_seed,
                  control=False
                  )
      episode_stats.append(run_episode(grid_world,episode,config))
    except Exception as e:
      print(e)
    print(f'Episode {episode} Concluded')

  #plot stats
  if args.control==True:
    [print(ep) for ep in control_stats]
  [print(ep) for ep in episode_stats]


  pes.plot(control_stats,episode_stats)

