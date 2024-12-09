from entities.entity import entity
import tensorflow as tf
import os
import random
import pandas as pd
import numpy as np
import jsonlines
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
    self.eps = 0.5
    # self.gender = True
    # self.attractiveness_score = 0
    self.overwrite_history=False #eventually move this to config
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
      input_shape = (None,self.obs_range+2,self.obs_range+2)
      self.model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=input_shape[1:]),
        tf.keras.layers.Flatten(),
        # tf.keras.layers.SimpleRNN(64, return_sequences=False),
        tf.keras.layers.Dense(64),#i dont need an RNN because the training isnt sequential, its for all ants
        tf.keras.layers.Dense(self.action_space)  # Output Q-values for each action
      ])
      opt = tf.keras.optimizers.Adam(learning_rate=0.01)
      self.model.compile(optimizer=opt, loss='mse')

  def train_model(self):
    #using the last n recorded observation states, train a batch
    with jsonlines.open(self.history_path, mode='r') as f:
      history = [obj for obj in f]

    #transform history 
      #from [obs,action,reward] -> [[obs],action with reward @ argmax] 
    y = np.array([[dct['reward'] if i == np.argmax(dct['action']) else a for i,a in enumerate(range(self.action_space))] for dct in history]) 
    X = np.array([dct['obs'] for dct in history])
    X=np.squeeze(X, axis=0)
    self.model.fit(X,y,verbose=0)

    self.model.save(self.model_path)


  def infer(self,obs):
    #using observation, make a decision.
    predicted_rewards = self.model.predict(obs,verbose=0)

    #add epsilon randomness and decay
    if random.random() < self.eps:
      action = random.randint(0,self.action_space-1)
    else:
      action = np.argmax(predicted_rewards)

    reward = self.get_reward(obs,action)
    #store observation, decision, and reward for future training
      #append to CSV within the model folder.
    self.save_history({'obs':obs.tolist(),'action':int(action),'reward':float(reward)})#doing this every time might be too slow, maybe gather and save in batches?
    return action
  def save_history(self,history_dict):
    if os.path.exists(self.history_path) or self.overwrite_history==True:
      with jsonlines.open(self.history_path, mode='w') as f:
        f.write(history_dict)
    else:
      with jsonlines.open(self.history_path, mode='a') as f:
        f.write(history_dict)
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
    return reward
  def decide_direction(self,grid):
    '''
    Method to decide which way an entity should move
    Uses self.model to decide action
    '''
    direction = self.infer(self.get_observable_space(grid))
    return direction

  def get_observable_space(self,grid):
    xlow = self.position[0]-self.obs_range
    xhigh = self.position[0]+self.obs_range

    ylow = self.position[1]-self.obs_range
    yhigh = self.position[1]+self.obs_range

    #somehow rectify observable space if its outside the range of the map
      #maybe instead of getting a slice of the map, "query" the map at each spot to fill
      #a predefined matrix
      #and have a special wall character to denote it being at a wall
    obs = np.array([[-1 for y in range(self.obs_range+2)] for x in range(self.obs_range+2)])
    for i,x in enumerate(range(xlow,xhigh+1)):
      for j,y in enumerate(range(ylow,yhigh+1)):
        if x>=len(grid) or y>=len(grid[0]) or x<0 or y<0:
          obs[i,j] = ord('#')
        else:
          obs[i,j] = ord(grid[x,y].character)
    if len(obs) == 0:
      print('observable space is none')
    return np.array([obs])
  
    