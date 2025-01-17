
import argparse
import yaml
from scripts.run_episode import run_episode
from entities.world import world
import tensorflow as tf
import numpy as np
import random
import os
import shutil
import matplotlib.pyplot as plt
import scripts.plot_episode_stats as pes
if __name__ == '__main__':

  print(tf.config.list_physical_devices('GPU'))
  parser = argparse.ArgumentParser()
  parser.add_argument('--config',type=str)
  parser.add_argument('--seed',type=int, required=False,default=-1)
  parser.add_argument('--control_run',type=bool, required=False,default=False)
  parser.add_argument('--model_run',type=bool, required=False,default=False)
  parser.add_argument('--reset_models',type=bool, required=False,default=False)
  parser.add_argument('--reset_training_data',type=bool, required=False,default=False)
  args = parser.parse_args()

  if args.seed != -1:
    print('Using seed: ',args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)

  if args.reset_models==True:
    print('Deleting existing models')
    file_list = [
      'brains/runner/novice.keras',
      'brains/scout/novice.keras',
      'brains/soldier/novice.keras',
    ]
    for file in file_list:
      try:
        os.remove(file)
      except Exception as e:
        print(e)
        
  if args.reset_training_data==True:
    print('Deleting existing training data')
    folder_list = [
      'history/runner',
      'history/scout',
      'history/soldier',
    ]
    for folder in folder_list:
      try:
        shutil.rmtree(folder)
        os.mkdir(folder)
      except Exception as e:
        print(e)
        

  with open(args.config,'r') as f:
    config = yaml.safe_load(f)


  #train models prior to runs
  # training_grid_world = world(
  #                 x_size=config['grid_size_x'],
  #                 y_size=config['grid_size_y'],
  #                 num_ants=config['ants'],
  #                 num_food=config['food'],
  #                 config=config,
  #                 seed=0,
  #                 control=False,
  #                 episode=-1,
  #                 )
  # models_train_history = training_grid_world.train_models(epochs=1000)
  # for species,train_history in models_train_history:
  #   plt.figure()
  #   plt.plot(train_history.history['loss'], label='Train Loss')
  #   plt.plot(train_history.history['val_loss'], label='Validation Loss')
  #   plt.title('Model Loss')
  #   plt.xlabel('Epoch')
  #   plt.ylabel('Loss')
  #   plt.legend(loc='upper right')
  #   plt.savefig(f'figures/{species}_training_history.png')

  episode_stats = []
  control_stats = []


  for episode in range(config['episodes']):
    if args.seed == -1:
      run_seed = random.random()
    else:
      run_seed = args.seed
    if args.control_run == True:
      control_grid_world = world(
                  x_size=config['grid_size_x'],
                  y_size=config['grid_size_y'],
                  num_ants=config['ants'],
                  num_food=config['food'],
                  config=config,
                  seed=run_seed,
                  control=True,
                  episode=episode,
                  )
      control_stats.append(run_episode(control_grid_world,episode,config))
  
    if args.model_run == True:
      model_grid_world = world(
                  x_size=config['grid_size_x'],
                  y_size=config['grid_size_y'],
                  num_ants=config['ants'],
                  num_food=config['food'],
                  config=config,
                  seed=run_seed,
                  control=False,
                  episode=episode,
                  )
      episode_stats.append(run_episode(model_grid_world,episode,config))

    print(f'Episode {episode} Concluded')

  #plot stats
  if args.control_run==True:
    [print(ep) for ep in control_stats]
  [print(ep) for ep in episode_stats]


  pes.plot(control_stats,episode_stats)

