##class to handle models per ant species
  # in the future, the queen might be an entity on the board. For now, she is "underground" 

import tensorflow as tf
import os
import random
import pandas as pd
import numpy as np
import jsonlines
import time 
from entities.soldier import soldier
from entities.runner import runner
from entities.scout import scout
import copy
class queen():
  def __init__(self,species_name,max_sequence_length,control):
    self.species_name = species_name
    self.example_ant = {
      'soldier':soldier([-1,-1],-1,-1,'-1',-1),
      'runner':runner([-1,-1],-1,-1,'-1',-1),
      'scout':scout([-1,-1],-1,-1,'-1',-1),
                       }[species_name]
 
    # self.max_sequence_length = 15
    self.eps = 1.0 if control else 0.25 
    self.control = control
    self.number_of_dreams = 3
    self.discount_factor = 0.9
    self.max_sequence_length = max_sequence_length + self.number_of_dreams
    self.max_input_size = 13
    self.action_space = 5 #5 action choices, cardinal directions and no movement
    self.direction_dict = {
      0:[0,0],
      1:[1,0],
      2:[0,1],
      3:[-1,0],
      4:[0,-1],
      }
    self.ant_self_character = '@'
    self.inference_time_arr = []
    self.get_model()

  def get_model(self):
    #if model exists at self.model_path exists, load it
    if os.path.exists(self.example_ant.model_path):
      self.model = tf.keras.models.load_model(self.example_ant.model_path)

    #if not, create it
    else:
      self.model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(shape=(self.max_sequence_length,self.max_input_size*self.max_input_size),dtype=float),
        # tf.keras.layers.Masking(mask_value=ord('?')),  # Mask fog of war values
        tf.keras.layers.Masking(mask_value=0),  # Mask padded values (0.0)
        # tf.keras.layers.InputLayer(shape=(None,self.max_input_size*self.max_input_size),dtype=int),
        tf.keras.layers.LSTM(64*8, return_sequences=True),
        # tf.keras.layers.SimpleRNN(64, return_sequences=True),
        # tf.keras.layers.SimpleRNN(64, return_sequences=True),
        # tf.keras.layers.SimpleRNN(64, return_sequences=True),
        tf.keras.layers.Dropout(rate=0.25),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(rate=0.25),
        tf.keras.layers.Dense(64,activation='relu'),  # Output Q-values for each action
        tf.keras.layers.Dropout(rate=0.25),
        tf.keras.layers.Dense(self.action_space,activation='sigmoid')  # Output Q-values for each action
      ])
      
      # lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
      #     initial_learning_rate=0.01,
      #     decay_steps=1000,
      #     decay_rate=0.9
      # )
      opt = tf.keras.optimizers.Adam(learning_rate=0.00001)
      # opt = tf.keras.optimizers.RMSprop(learning_rate=0.001)
      # opt = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
      # self.model.compile(optimizer=opt, loss='mse')#mae?
      self.model.compile(optimizer=opt, loss='mae')#mae?

      

  def train_model(self,episode):
    if self.control:
      return
    X = []
    y = []
    
    #randomly select n files for training
    limit = 10000 
    file_list = os.listdir(self.example_ant.history_path)
    rand_indecies = [random.randint(0,len(file_list)-1) for _ in range(limit)]
    file_list = [file_list[ind] for ind in rand_indecies]
    for file in file_list:
      #using the last n recorded observation states, train a batch
      with jsonlines.open(os.path.join(self.example_ant.history_path,file), mode='r') as f:#needs changed
        ant_history = [obj for obj in f]

      #limit history randomly
      random_limit = random.randint(1,len(ant_history))
      
      #X
      ant_history = ant_history[:random_limit]
      padded_history = self.pad_ant_obs_list(obs=None,history=ant_history)
      X.append(tf.reshape(padded_history,(self.max_sequence_length,self.max_input_size*self.max_input_size)))
      

      #y
      ant_y = np.array([[dct['reward'] if i == dct['action'] else 
                         a for i,a in enumerate(range(self.action_space))] 
                         for dct in ant_history]) 
      # ant_y = (ant_y - np.mean(ant_y))/np.std(ant_y)
      ant_y = (ant_y - np.min(ant_y))/(np.max(ant_y) - np.min(ant_y))
      y.append(sum(ant_y[:random_limit]))
    
    print(self.example_ant.name,'training',' episode ',episode)

    val_loss_early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',    
                                                                patience=3,           
                                                                verbose=0, 
                                                                restore_best_weights=True)
    train_loss_early_stopping = tf.keras.callbacks.EarlyStopping(monitor='loss',    
                                                                patience=5,           
                                                                verbose=0, 
                                                                restore_best_weights=True)
    self.model.fit(np.array(X),
                  np.array(y),
                  # epochs=5,
                  epochs=100,
                  validation_split=0.1,
                  callbacks = [val_loss_early_stopping,train_loss_early_stopping],
                  # verbose=0,
                  batch_size = 1048
                  )

    self.model.save(self.example_ant.model_path)


  def infer(self,obs_list,ant_history,dreaming=False):
    # obs_list = tf.reshape(obs_list,(-1,self.max_sequence_length,self.max_input_size,self.max_input_size))
    actions=[]
    #add epsilon randomness and decay
    if self.eps > random.random():
      actions = [random.randint(0,self.action_space-1) for _ in obs_list]
    else:
      #using observation, make a decision.
      infer_start_time=time.time()
      obs_list_for_prediction = np.array([self.pad_ant_obs_list(ob,hist) for ob,hist in zip(obs_list,ant_history)])
      try:
        tmp = obs_list_for_prediction.shape[1]
      except:
        print('obs_list_for_prediction.shape:',obs_list_for_prediction.shape)
        print('obs_list_for_prediction:',obs_list_for_prediction)
      if obs_list_for_prediction.shape[1] != self.max_sequence_length:
        print('obs_list_for_prediction before reshape is wrong',obs_list_for_prediction.shape[1])
      obs_list_for_prediction = tf.reshape(obs_list_for_prediction,
                                           (-1,self.max_sequence_length,self.max_input_size*self.max_input_size))
      if obs_list_for_prediction.shape[1] != self.max_sequence_length:
        print('obs_list_for_prediction after reshape is wrong',obs_list_for_prediction.shape[1])
      predicted_rewards = self.model.predict(obs_list_for_prediction,verbose=0)
      infer_end_time = time.time()
      self.inference_time_arr.append(infer_end_time-infer_start_time)
      
      actions = [np.argmax(pred_reward) for pred_reward in predicted_rewards]
    
    reward_arr = []
    if dreaming==False:
      #get predicted rewards
      dream_start_time=time.time()
      for i,dream in enumerate(range(self.number_of_dreams)):
        if i==0:
          new_obs_list,new_actions,new_rewards,new_history = self.infer_next_states(obs_list,actions,copy.deepcopy(ant_history))
        else:
          new_obs_list,new_actions,new_rewards,new_history = self.infer_next_states(new_obs_list,new_actions,new_history)
          reward_arr.append([r*(self.discount_factor**dream) for r in new_rewards])
      dream_end_time=time.time()
      # print('total dream time: ',dream_end_time-dream_start_time)
      
    
    history = []
    for i,(obs,action) in enumerate(zip(obs_list,actions)):
      #store observation, decision, and reward for future training
      reward = self.example_ant.get_reward(obs,action)
      reward += sum([r[i] for r in reward_arr])
      history.append({'obs':np.squeeze(obs.numpy()).tolist(),'action':int(action),'reward':float(reward)})#doing this every time might be too slow, maybe gather and save in batches?
    return actions,history
  
  def infer_next_states(self,obs_list,pred_actions,history_list):
    def find_self_in_obs(obs): 
      obs = obs.numpy()
      self_character_ascii = ord(self.ant_self_character)
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
      for _ in range(self.example_ant.max_movement_speed):
        moving_one_start=time.time()
        position,stopped = move_one_in_obs(obs,direction,position)
        moving_one_end=time.time()
        time_spent_moving_one.append(moving_one_end-moving_one_start)
        if stopped:
          break
      get_new_reward_start=time.time()
      # new_rewards.append(get_obs_reward(obs,position))
      new_rewards.append(self.example_ant.get_species_reward(obs))
      obs_list[i][position[0]][position[1]]==ord(self.ant_self_character)
      history_list[i].append({'obs':np.squeeze(obs.numpy()).tolist(),'action':int(pred_actions[i]),'reward':float(new_rewards[-1])})#doing this every time might be too slow, maybe gather and save in batches?

      
      get_new_reward_end=time.time()

    get_new_actions_start=time.time()
    #infer on those observations, get new actions, and get rewards
    new_predicted_rewards,_ = self.infer(obs_list,history_list,dreaming=True)
    new_actions = [np.argmax(x) for x in new_predicted_rewards]
    get_new_actions_end=time.time()


    #print time analysis
    # print('time_spent_moving_one:',sum(time_spent_moving_one))
    # print('time_spent_finding_self:',sum(time_spent_finding_self))
    # print('time_spent_getting_actions:',get_new_actions_end-get_new_actions_start)
    # print('time_spent_getting_reward:',get_new_reward_end-get_new_reward_start)

    #return new observations, actions, rewards, and new_positions
    return obs_list,new_actions,new_rewards,history_list
  

  def pad_ant_obs_list(self,obs,history):
    def history_obs_to_obs(history):
      # print([len(h['obs']) for h in history])
      # print([len(h['obs'][0]) for h in history])
      return [h['obs'] for h in history]
    # if len(history)>0:
    #   if type(history[0]) == dict:
    #     hist_obs = history_obs_to_obs(history)
    #   else:
    #     hist_obs = history
    # else:
    #     hist_obs = history
    hist_obs = history_obs_to_obs(history)

    if obs != None:
      hist_obs.append(obs)
    num_padding = self.max_sequence_length-len(hist_obs)
    num_padding = 0 if num_padding < 0 else num_padding
    for _ in range(num_padding):
      padded_arr = np.zeros((len(hist_obs[0]),len(hist_obs[0][0])),dtype=np.int32)
      hist_obs.append(padded_arr)
    # print('num_padding',num_padding)
    # print('len(hist_obs)',len(hist_obs))
    # print('len(hist_obs)',[len(h) for h in hist_obs])
    # print(hist_obs[0])
    hist_obs_np = np.array(hist_obs)
    shape_0_match = hist_obs_np.shape[0] == self.max_sequence_length
    shape_1_match = hist_obs_np.shape[1] == self.max_input_size
    shape_2_match = hist_obs_np.shape[2] == self.max_input_size
    if shape_0_match and shape_1_match and shape_2_match:
      pass
    else:
      print('hist_obs_np.shape: ',hist_obs_np.shape)
    assert shape_0_match
    assert shape_1_match
    assert shape_2_match
      # print('hist_obs_np shape is',hist_obs_np.shape)
      
    return hist_obs_np 
  
  
