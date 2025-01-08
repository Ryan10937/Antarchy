from entities.entity import entity
import tensorflow as tf
import os
import random
import pandas as pd
import numpy as np
import jsonlines
import time
class ant(entity):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID,intelligence,obs_range,control=False):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 10
    self.max_health = 200
    self.health = 200
    self.max_movement_speed = 3
    self.obs_range = obs_range
    self.is_food = False
    self.food_eaten = 0
    self.ants_eaten = 0
    self.action_space = 5 #5 action choices, cardinal directions and no movement
    self.eps = 1.0 if control else 0.2 
    self.control = control
    self.intelligence = intelligence
    self.number_of_dreams = 3
    self.discount_factor = 0.9
    self.self_character = '@'
    # self.gender = True
    # self.attractiveness_score = 0
    self.overwrite_history=False #eventually move this to config
    self.max_input_size = 13
    self.history = []
    self.inference_time_arr = []
    self.get_model()
    if self.overwrite_history == True and os.path.exists(self.history_path):
      os.remove(self.history_path)
  
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
    entity.log(f'{self.ID} attacking {entity.ID} for {entity.damage}')
    if entity.health <= 0:
      entity.display_character='#'
      entity.is_alive=False
      if entity.is_food==True:
        self.food_eaten+=1
      if entity.is_food==False:
        self.ants_eaten+=1

  def act(self,grid,action):
    if len(grid[self.position[0],self.position[1]].entities)>1:
      self.fight(grid[self.position[0],self.position[1]].entities)
    else:
      self.move(grid,action)


  def get_model(self):
    #if model exists at self.model_path exists, load it
    if os.path.exists(self.model_path):
      self.model = tf.keras.models.load_model(self.model_path)

    #if not, create it
    else:
      self.model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(shape=(self.max_input_size,self.max_input_size),dtype=int),
        tf.keras.layers.Flatten(),
        # tf.keras.layers.SimpleRNN(64, return_sequences=False),
        tf.keras.layers.Dense(16,activation=tf.keras.activations.sigmoid),
        tf.keras.layers.Dense(16,activation=tf.keras.activations.sigmoid),
        tf.keras.layers.Dense(16,activation=tf.keras.activations.sigmoid),
        tf.keras.layers.Dense(16,activation=tf.keras.activations.sigmoid),
        tf.keras.layers.Dense(16,activation=tf.keras.activations.sigmoid),
        tf.keras.layers.Dropout(rate=0.25),
        tf.keras.layers.Dense(self.action_space,activation='relu')  # Output Q-values for each action
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
    # self.model.fit(X,y,verbose=0)
    print(self.name,'training')
    self.model.fit(X,
                   y,
                   epochs=20,
                   validation_split=0.1,
                   callbacks = tf.keras.callbacks.EarlyStopping(monitor='val_loss',    
                                                                patience=5,           
                                                                verbose=0, 
                                                                restore_best_weights=True)
                  )

    self.model.save(self.model_path)


  def infer(self,obs_list,dreaming=False):
    obs_list = tf.reshape(obs_list,(-1,self.max_input_size,self.max_input_size))
    actions=[]
    #add epsilon randomness and decay
    if self.eps > random.random() :
      actions = [random.randint(0,self.action_space-1) for _ in obs_list]
    else:
      # print('here in ant.infer')
      #using observation, make a decision.
      infer_start_time=time.time()
      predicted_rewards = self.model.predict(obs_list,verbose=0)
      infer_end_time = time.time()
      self.inference_time_arr.append(infer_end_time-infer_start_time)
      
      actions = [np.argmax(pred_reward) for pred_reward in predicted_rewards]
    
    reward_arr = []
    if dreaming==False:
      #get predicted rewards
      dream_start_time=time.time()
      for i,dream in enumerate(range(self.number_of_dreams)):
        if i==0:
          new_obs_list,new_actions,new_rewards = self.infer_next_states(obs_list,actions)
        else:
          new_obs_list,new_actions,new_rewards = self.infer_next_states(new_obs_list,new_actions)
          reward_arr.append([r*(self.discount_factor**dream) for r in new_rewards])
      dream_end_time=time.time()
      # print('total dream time: ',dream_end_time-dream_start_time)
      
    
    rewards=[]
    for i,(obs,action) in enumerate(zip(obs_list,actions)):
      #store observation, decision, and reward for future training
      reward = self.get_reward(obs,action)
      reward += sum([r[i] for r in reward_arr])
      self.history.append({'obs':np.squeeze(obs.numpy()).tolist(),'action':int(action),'reward':float(reward)})#doing this every time might be too slow, maybe gather and save in batches?
      rewards.append(reward)
    return actions
  
  def infer_next_states(self,obs_list,pred_actions):
    def find_self_in_obs(obs): 
      obs = obs.numpy()
      self_character_ascii = ord(self.self_character)
      for i,row in enumerate(obs):
        for j,character in enumerate(row):
          if character == self_character_ascii:
            return [i,j]
      return None
    def check_position(position,obs):
      #stop if any of these conditions are met:
        #if at a wall (i really need to add a wall character)
        #if sharing a space with another species
        #if sharing a space with food
      spot_character = obs[position[0]][position[1]]
      # if spot_character in ['#','X','%']:
      if spot_character in [ord('X'),ord('%')]:#what if i let it dream out of bounds but punished it heavily for it
        return False
      elif position[0]<0 or position[1]<0 or position[0]>=len(obs) or position[1]>=len(obs[0]):
        print('Tried to dream out of obs bounds')
        return False
      else:
        return True
      
    def move_one_in_obs(obs,direction,position):
      potential_position = [
        position[0] + direction[0],
        position[1] + direction[1]
      ]
      if check_position(potential_position,obs):
        return potential_position,True
      else:
        return position,False
    def get_obs_reward(obs,new_position):
      #if new position in obs is food, give reward +10
      if obs[new_position[0]][new_position[1]] == ord('%'):
        return 10
      elif obs[new_position[0]][new_position[1]] == ord('#'):
        return -100
      elif obs[new_position[0]][new_position[1]] == ord('X'):
        return -1
      else:
        return 0
      

    #runtime analysis vars
    time_spent_moving_one = []
    time_spent_finding_self = []


    #using observations and predicted actions, create new obs_list
    directions = [self.direction_dict[x] for x in pred_actions]
    new_rewards=[]
    for i,(obs,direction) in enumerate(zip(obs_list,directions)):
      # print(obs.shape)
      finding_self_start=time.time()
      position = find_self_in_obs(obs)
      finding_self_end=time.time()
      time_spent_finding_self.append(finding_self_end-finding_self_start)

      obs[position[0],position[1]]==ord(' ')
      for _ in range(self.max_movement_speed):
        moving_one_start=time.time()
        position,stopped = move_one_in_obs(obs,direction,position)
        moving_one_end=time.time()
        time_spent_moving_one.append(moving_one_end-moving_one_start)
        if stopped:
          break
      get_new_reward_start=time.time()
      new_rewards.append(get_obs_reward(obs,position))
      obs_list[i][position[0]][position[1]]==ord(self.self_character)
      get_new_reward_end=time.time()

    get_new_actions_start=time.time()
    #infer on those observations, get new actions, and get rewards
    # new_predicted_rewards = self.model.predict(obs_list,verbose=0)
    new_predicted_rewards = self.infer(obs_list,dreaming=True)
    new_actions = [np.argmax(x) for x in new_predicted_rewards]
    get_new_actions_end=time.time()


    #print time analysis
    # print('time_spent_moving_one:',sum(time_spent_moving_one))
    # print('time_spent_finding_self:',sum(time_spent_finding_self))
    # print('time_spent_getting_actions:',get_new_actions_end-get_new_actions_start)
    # print('time_spent_getting_reward:',get_new_reward_end-get_new_reward_start)

    #return new observations, actions, rewards, and new_positions
    return obs_list,new_actions,new_rewards

  
  def save_history(self):
    for history_dict in self.history:
      if os.path.exists(self.history_path)==False:
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
    if self.health > 0: #until history is per-ant, this should be disabled
      reward +=-0.1
    reward += self.get_species_reward(obs,action)
    return reward
  # def decide_direction(self,grid,action):
  #   '''
  #   Method to decide which way an entity should move
  #   Uses self.model to decide action
  #   '''
  #   # direction = self.infer(self.get_observable_space(grid))
  #   return action

  def get_observable_space(self,grid):

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
    obs = add_padding_2d(obs, self.max_input_size, ord('#'))
    
    if len(obs) == 0:
      print('observable space is none')

    return tf.convert_to_tensor([obs], dtype=tf.int32)
  
    