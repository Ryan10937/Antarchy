import tensorflow as tf
from entities.entity import entity
import os
import random
import pandas as pd
import numpy as np
import jsonlines
import time
class ant(entity):
  # def __init__(self,position,map_size_x,map_size_y,display_character,ID,intelligence,obs_range,control=False):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID,intelligence,obs_range,config=None):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 10
    self.max_health = 200
    self.range=1
    self.health = 200
    self.max_movement_speed = 3
    self.obs_range = obs_range
    self.is_food = False
    self.willing_to_fight = False
    self.intelligence = intelligence
    self.food_eaten = 0
    self.ants_eaten = 0
    self.max_sequence_length = None if config==None else config['num_timesteps']
    self.self_character = '@'
    self.fog_of_war_character = '?'
    # self.gender = True
    # self.attractiveness_score = 0
    self.overwrite_history=False #eventually move this to config
    self.history = []
    self.inference_time_arr = []
    # self.get_model()
    if self.overwrite_history == True and os.path.exists(self.history_path):
      os.rmdir(self.history_path)
      os.mkdir(self.history_path)
  
  def get_stats(self):
    stats = super().get_stats()
    stats.update({
      'max_health':self.max_health,
      'food_eaten':self.food_eaten,
      'ants_eaten':self.ants_eaten,
      'inference_time_arr':self.inference_time_arr,
    })
    return stats

  def fight(self,entity_list):
    #this isnt great, it will attack food or the other entity with equal chance
    #it will do for now but i would like to change it later
    if len(entity_list)>1:
      random_target = random.randint(0,len(entity_list)-1)
    else:
      random_target=0
    self.attack(entity_list[random_target])
    
  def attack(self,entity):
    entity.health -= self.damage
    # entity.log(f'{self.ID} attacking {entity.ID} for {entity.damage}')
    # print(f'{self.ID} attacking {entity.ID} for {self.damage}')
    if entity.health <= 0:
      entity.display_character='~'
      entity.is_alive=False
      if entity.is_food==True:
        self.food_eaten+=1
      if entity.is_food==False:
        self.ants_eaten+=1

  def act(self,grid,action):
    if len(self.get_entities_in_range(grid))>1:
      self.willing_to_fight = True
    else:
      self.willing_to_fight = False

    self.move(grid,action)
  def get_entities_in_range(self,grid):
    #get entities in the 4 adjacent spots and self
    spots = [grid[i,j] for i,j in 
             [
               [self.position[0],self.position[1]],
               [self.position[0]-1,self.position[1]],
               [self.position[0],self.position[1]-1],
               [self.position[0]+1,self.position[1]],
               [self.position[0],self.position[1]+1],
             ]
             if i<len(grid) and j<len(grid[0])
      ] 
    entities=[]
    for spot in spots:
      for ent in spot.entities:
        entities.append(ent)
    return entities

  
  def save_history(self,ant_ID,ant_name):
    num_history_files = len(os.listdir(self.history_path))
    for history_dict in self.history:
      if os.path.exists(self.history_path)==False:
        with jsonlines.open(f'{self.history_path}_{ant_name}_{ant_ID}_{num_history_files}.csv', mode='w') as f:
          f.write(history_dict)
      else:
        with jsonlines.open(f'{self.history_path}_{ant_name}_{ant_ID}_{num_history_files}.csv', mode='a') as f:
          f.write(history_dict)
  def get_reward(self,obs):
    #Get a small living reward 
      #based on timestep?
    #Get a large-ish negative reward for dying
    #Get a reward for food
    #Add some amount to it depending on species
      #in each species, define a "add species reward" method
    reward = 0
    if self.health > 0: #until history is per-ant, this should be disabled
      reward +=-0.1
    reward += self.get_species_reward(obs)
    return reward

  def get_observable_space(self,grid,max_input_size):

    def add_padding_2d(array, desired_len, padding_value=0):
      n = desired_len//2 - array.shape[0]//2
      padded_array = [[padding_value]*(len(array[0])+n*2) for i in range(n)]
      for row in array:
        tmp=([padding_value]*n)+row.tolist()+([padding_value]*n)
        padded_array.append(tmp)
      for i in range(n):
        padded_array.append([padding_value]*(len(array[0])+n*2))
      padded_array = np.array(padded_array)
      return padded_array

    xlow = self.position[0]-self.obs_range
    xhigh = self.position[0]+self.obs_range

    ylow = self.position[1]-self.obs_range
    yhigh = self.position[1]+self.obs_range
    #somehow rectify observable space if its outside the range of the map
      #maybe instead of getting a slice of the map, "query" the map at each spot to fill
      #a predefined matrix
      #and have a special wall character to denote it being at a wall
    obs = np.array([[-1 for y in range(self.obs_range*2+1)] for x in range(self.obs_range*2+1)])
    for i,x in enumerate(range(xlow,xhigh+1)):
      for j,y in enumerate(range(ylow,yhigh+1)):
        # if (x>=len(grid)-1) or (y>=len(grid[0])-1) or x<0 or y<0:
        if (x>=len(grid)) or (y>=len(grid[0])) or x<0 or y<0:
          obs[i,j] = ord('#')
        elif x==self.position[0] and y==self.position[1]:
          obs[i,j] = ord(self.self_character)
        else:
          obs[i,j] = ord(grid[x,y].character)
    obs = add_padding_2d(obs, max_input_size, ord(self.fog_of_war_character))
    
    if len(obs) == 0:
      print('observable space is none')
    return tf.convert_to_tensor(obs, dtype=tf.int32)
  
  