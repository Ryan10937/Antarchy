import numpy as np
import random
import json
import os
import shutil
import time
from datetime import datetime

from entities.ant import ant
from entities.soldier import soldier
from entities.runner import runner
from entities.scout import scout
from entities.food import food
class spot():
  def __init__(self,position):
    self.position = position
    self.character = ' '
    self.entities = []
  def __repr__(self):
    return self.character
  def add_entity(self,new_entity):
    self.entities.append(new_entity)
    self.update_display_char()
  def remove_entity(self,entity_to_remove):
    for idx,ent in enumerate(self.entities):
      if ent.ID == entity_to_remove.ID:
        removed_item = self.entities.pop(idx)
        if removed_item.ID != ent.ID:
          print('Attempted to remove',removed_item,'but removed',ent,'instead')
    self.update_display_char()
    
  def update_display_char(self):
    if len(self.entities) == 0:
      self.character = ' '
    elif len(self.entities) == 1:
      self.character = self.entities[0].display_character
    elif len(self.entities) > 1 and all([ent.is_food for ent in self.entities]):
      self.character = '%'
    else:
      self.character = 'X'
      #sert cond if is_alive==F
      # found_dead_ant = False
      # for ent in self.entities:
      #   if ent.is_alive==False:
      #     print('Found dead ant on X space!',ent.ID)
class world():
  def __init__(self,x_size,y_size,num_ants,num_food,config,seed=None,control=False):
    self.config = config
    self.state_log_folder = './logs/state/'
    self.log_folder = './logs/log/'
    self.sleep_time = 1#seconds
    self.log_limit = 1000
    self.size = [x_size,y_size]
    self.control = control
    #set random seeds 
    if seed is not None:
      random.seed(seed)
      np.random.seed(seed)

    self.grid = np.array([[spot([x,y]) for y in range(self.size[1])] for x in range(self.size[0])])
    self.spawn_list = self.make_spawn_list({
      'position':[-1,-1],
      'map_size_x':-1,
      'map_size_y':-1,
      'display_character':'-1',
      'ID' : -1,
      'control' : control,
      })
    self.ants = [self.roll_for_species({
      'position':[random.randint(0,self.size[0]-1),random.randint(0,self.size[1]-1)],
      'map_size_x':x_size,
      'map_size_y':y_size,
      'display_character':'8',
      'ID' : ID,
      'control' : control,
      }
                            ) 
                     for ID in range(num_ants)]
    self.food = [food(
      position=[random.randint(0,self.size[0]-1),random.randint(0,self.size[1]-1)],
      map_size_x=x_size,
      map_size_y=y_size,
      display_character='%',
      ID = ID+num_ants,
                            ) 
                     for ID in range(num_food)]
    self.graveyard = []
    self.num_ant_teams = len(config['species'])
    self.species_to_class = {
      'soldier':[ant for ant in self.ants if ant.name=='soldier'][0],
      'runner':[ant for ant in self.ants if ant.name=='runner'][0],
      'scout':[ant for ant in self.ants if ant.name=='scout'][0],
      }

    self.same_team_count = 0
    self.timestep = 0
    self.place_ants()
    self.place_food()

  def make_spawn_list(self,attributes:dict):#change this to "make_spawn_list"? and then use the spawn list to roll for species
    #make species name to class dictionary
    name_to_class = {
      'soldier':soldier,
      'scout':scout,
      'runner':runner,
      }
    possible_species = self.config['species']
    #get probability for each species
    spawn_rates = {}
    for name,class_type in name_to_class.items():
      tmp = class_type(**attributes)
      spawn_rates[name] = tmp.spawn_rate

    #make spawn_list
    spawn_list=[]
    for name,rate in spawn_rates.items():
      if name not in possible_species:
        continue
      for i in range(rate):
        spawn_list.append(name)
    return spawn_list
  def roll_for_species(self,attributes:dict):
    name_to_class = {
      'soldier':soldier,
      'scout':scout,
      'runner':runner,
      }
    name = self.spawn_list[random.randint(0,len(self.spawn_list)-1)]
    return name_to_class[name](**attributes)
  def render(self):
    print(self.timestep)
    print(self.grid)

  def place_ants(self):
    for at in self.ants:
      self.grid[at.position[0],at.position[1]].add_entity(at)
  def place_food(self):
    for fd in self.food:
      self.grid[fd.position[0],fd.position[1]].add_entity(fd)

  def log_state(self,episode,step,is_last_step):
    '''
    log state as json file for godot to read when ready

    due to lag-time of 2d/3d rendering, this function will also sleep until there are less than n files
    '''
    #create state dictionary
    entity_dict={
      'episode':episode,
      'step':step,
      'is_last_step':is_last_step,
      'grid_size':self.size,
      }
    entity_dict['entities'] = [ent.get_stats() for ent in self.ants]
    entity_dict['food'] = [ent.get_stats() for ent in self.food]

    time_string = datetime.now().strftime('%d_%H_%M_%S_%f')
    with open(f'{self.state_log_folder}state_at_{time_string}.json','w') as f:
      json.dump(entity_dict,f)
    # if len(os.listdir(self.state_log_folder))>=self.log_limit:
    #   time.sleep(self.sleep_time)
  def clean_state_logs(self):
    shutil.rmtree(self.state_log_folder)
    os.makedirs(self.state_log_folder) 

    shutil.rmtree(self.log_folder)
    os.makedirs(self.log_folder) 



  def cleanup(self):
    for x in range(self.size[0]):
      for y in range(self.size[1]):
        for ant in self.grid[x,y].entities:
          if ant.is_alive == False:
            self.graveyard.append(ant)
            self.grid[x,y].remove_entity(ant)

  def entity_turns(self):
    self.timestep+=1
    actions = self.get_entity_decisions()
    for i,ant in enumerate(self.ants):
      if ant.health <= 0:
        self.grid[ant.position[0],ant.position[1]].remove_entity(ant)
        continue
      prev_position_x = ant.position[0]
      prev_position_y = ant.position[1]
      ant.act(self.grid,actions[i])
      self.grid[prev_position_x,prev_position_y].remove_entity(ant)
      self.grid[ant.position[0],ant.position[1]].add_entity(ant)
    self.cleanup()

  def get_entity_decisions(self):
    #get observations for all ants
    observations = [ant.get_observable_space(self.grid) for ant in self.ants] 
    actions = [-1 for obs in observations]
    for species in self.config['species']:#per species
      #make a mask per species
      species_mask = [1 if ant.name==species else 0 for ant in self.ants]

      #call each model with obs x mask
      species_obs = [obs for i,obs in enumerate(observations) if species_mask[i]==1]
      #store action results at new_list x mask
      species_actions = self.species_to_class[species].infer(species_obs)#use species-specific model on batch of species_obs
      
      # actions = [species_obs if species_mask[i]==1 else for a in actions]
      count = 0
      for i,action in enumerate(actions):
        if species_mask[i]==1:
          actions[i]=species_actions[count]
          count+=1
    return actions
  def log(self,message):
    with open(self.log_folder+'log.log','a') as f:
      f.write(message+'\n')


  def train_models(self):
    unique_species_names = []
    unique_species = []
    for ant in self.ants:
      if ant.name not in unique_species_names:
        unique_species_names.append(ant.name)
        unique_species.append(ant)
    for species in unique_species:
      species.train_model()#this method covers loading, training, and saving model to appropriate path
  def save_history(self):
    for ant in self.ants:
      ant.save_history()

  def check_for_end_conditions(self):
    alive_ants = [ant.name for ant in self.ants if ant.is_alive]
    unique_species_alive,unique_species_alive_counts = np.unique(alive_ants,return_counts=True)
    self.previous_num_ant_teams = self.num_ant_teams
    self.num_ant_teams = len(unique_species_alive)

    if self.previous_num_ant_teams == self.num_ant_teams:
      self.same_team_count+=1
    else:
      self.same_team_count = 0
    
    if self.same_team_count > 10 and len(alive_ants)<5:

      print('Reached Stalemate End Condition')
      # print([[str(y),int(x)] for x,y in zip(unique_species_alive_counts,unique_species_alive)])
      # print(alive_ants)
      return True

    if len(unique_species_alive)>1:
      return False
    else:
      print('Reached Dominance End Condition')
      return True

  def get_stats(self):
    '''
    Returns a dictionary of stats about the episode:
      timesteps: int
      met_end_conditions: bool
      mean_ant_inference_time: float
      range_ant_inference_time: (float,float)
      food_eaten: dict[species]:int
      ants_eaten: dict[species]:int

    '''

    episode_stats = {
      'timesteps':self.timestep,
      'ants_eaten':{k:[] for k in self.config['species']},
      'food_eaten':{k:[] for k in self.config['species']},
      'inference_time_mean':[],
      'inference_time_range':[],
      } 
    for ant in self.ants:

      ant_stats = ant.get_stats()
      episode_stats['ants_eaten'][ant.name].append(ant_stats['ants_eaten'])
      episode_stats['food_eaten'][ant.name].append(ant_stats['food_eaten'])
      if len(ant_stats['inference_time_arr']) > 0:
        episode_stats['inference_time_mean'].append(np.mean(ant_stats['inference_time_arr']))
        episode_stats['inference_time_range'].append([np.min(ant_stats['inference_time_arr']),np.max(ant_stats['inference_time_arr'])])

    episode_stats['ants_eaten'] = {k:int(np.mean(v)) for k,v in episode_stats['ants_eaten'].items()}
    episode_stats['food_eaten'] = {k:int(np.mean(v)) for k,v in episode_stats['food_eaten'].items()}
    episode_stats['inference_time_mean'] = np.mean(episode_stats['inference_time_mean'])
    episode_stats['inference_time_range'] = [np.min(np.array(episode_stats['ants_eaten']).flatten()),np.max(np.array(episode_stats['ants_eaten']).flatten())]
    episode_stats['num_ants_alive'] = sum([1 if ant.is_alive==True else 0 for ant in self.ants])
    return episode_stats







