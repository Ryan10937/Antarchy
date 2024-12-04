from entities.entity import entity
import tensorflow as tf
import os
import random
import pandas as pd
import numpy as np
import csv
class ant(entity):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 10
    self.max_health = 200
    self.health = 200
    self.max_movement_speed = 3
    self.is_food = False
    self.food_eaten = 0
    self.ants_eaten = 0
    self.action_space = 5 #5 action choices, cardinal directions and no movement
    # self.gender = True
    # self.attractiveness_score = 0

    self.get_model()
  


  def get_stats(self):
    stats = super().get_stats()
    stats.update({
      'max_health':self.max_health,
      'food_eaten':self.food_eaten,
      'ants_eaten':self.ants_eaten,
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
    entity.log(f'{self.ID} attacking {entity.ID} for {entity.damage}')
    if entity.health <= 0:
      self.food_eaten+=1
      entity.display_character='#'
      entity.is_alive=False
      if entity.is_food==False:
        self.ants_eaten+=1

  def act(self,grid):
    if len(grid[self.position[0],self.position[1]].entities)>1:
      self.fight(grid[self.position[0],self.position[1]].entities)
    else:
      self.move(grid)


  def get_model(self):
    #if model exists at self.model_path exists, load it
    if os.path.exists(self.model_path):
      self.model = tf.keras.models.load_model(self.model_path)

    #if not, create it
    else:
      input_shape = (None, 1 , self.obs_range[0], self.obs_range[1],1)
      self.model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=input_shape[1:]),
        tf.keras.layers.SimpleRNN(64, return_sequences=False),
        tf.keras.layers.Dense(self.action_space)  # Output Q-values for each action
      ])
      opt = tf.keras.optimizers.Adam(learning_rate=0.01)
      self.model.compile(optimizer=opt, loss='mse')
      

  def train_model(self):
    #using the last n recorded observation states, train a batch
    with open(self.history_path, mode='r', newline='', encoding='utf-8') as csv_file:
      dump = csv.reader(csv_file)
      history = [row for row in dump] 
    pass
  def infer(self,obs):
    #using observation, make a decision.
    predicted_rewards = self.model.predict(obs)

    #add epsilon randomness and decay
    if random.random(0,1) < self.eps:
      action = random.randint(0,self.action_space)
    else:
      action = np.argmax(predicted_rewards)

    reward = self.get_reward(obs,action)
    #store observation, decision, and reward for future training
      #append to CSV within the model folder.
    self.save_history([obs,action,reward])#doing this every time might be too slow, maybe gather and save in batches?
  def save_history(self,list_of_history):
    if os.path.exists(self.history_path):
      self.history = pd.read_csv(self.history_path)
    else:
      with open(self.history_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(list_of_history)
  def get_reward(self,obs,action):
    #Get a small living reward 
      #based on timestep?
    #Get a large-ish negative reward for dying
    #Get a reward for food
    #Add some amount to it depending on species
      #in each species, define a "add species reward" method
    reward = 0
    if self.health > 0:
      reward +=1
    reward += self.get_species_reward(obs,action)
    