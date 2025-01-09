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
class queen():
  def __init__(self,species_name,max_sequence_length,control):
    self.species_name = species_name
    self.max_sequence_length = max_sequence_length
    self.example_ant = {
      'soldier':soldier([-1,-1],-1,-1,'-1',-1),
      'runner':runner([-1,-1],-1,-1,'-1',-1),
      'scout':scout([-1,-1],-1,-1,'-1',-1),
                       }[species_name]
 
    # self.max_sequence_length = 15
    self.eps = 1.0 if control else 0.2 
    self.number_of_dreams = 0
    self.discount_factor = 0.9
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
        tf.keras.layers.InputLayer(shape=(self.max_sequence_length,self.max_input_size*self.max_input_size),dtype=int),
        # tf.keras.layers.InputLayer(shape=(None,self.max_input_size*self.max_input_size),dtype=int),
        tf.keras.layers.SimpleRNN(64, return_sequences=True),
        tf.keras.layers.SimpleRNN(64, return_sequences=False),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(rate=0.25),
        tf.keras.layers.Dense(self.action_space,activation='relu')  # Output Q-values for each action
      ])
      opt = tf.keras.optimizers.Adam(learning_rate=0.01)
      self.model.compile(optimizer=opt, loss='mse')

  def train_model(self):
    X = []
    y = []
    for file in os.listdir(self.example_ant.history_path):
      #using the last n recorded observation states, train a batch
      with jsonlines.open(os.path.join(self.example_ant.history_path,file), mode='r') as f:#needs changed
        ant_history = [obj for obj in f]
        #transform history from [obs,action,reward] -> [[obs],action with reward @ argmax] 
        # ant_X = np.array([[y for x in dct['obs'] for y in x] for dct in ant_history])
        ant_y = np.array([[dct['reward'] if i == np.argmax(dct['action']) else a for i,a in enumerate(range(self.action_space))] for dct in ant_history]) 
      
      padded_history = self.pad_ant_obs_list(obs=None,history=ant_history)
      X.append(tf.reshape(padded_history,(self.max_sequence_length,self.max_input_size*self.max_input_size)))
      y.append(sum(ant_y))
    
    print(self.example_ant.name,'training')
    
    for x in X:
      if len(x) != self.max_sequence_length:
        print('len(X)', len(X))
        print('[len(x) for x in X]', [len(x) for x in X])
        print('len(x)', len(x))
        print(x)
    self.model.fit(np.array(X),
                  np.array(y),
                  epochs=15,
                  validation_split=0.25,
                  callbacks = tf.keras.callbacks.EarlyStopping(monitor='val_loss',    
                                                                patience=5,           
                                                                verbose=0, 
                                                                restore_best_weights=True),
                  verbose=0
                                                        
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
        print('here, dreaming :D')
        if i==0:
          new_obs_list,new_actions,new_rewards = self.infer_next_states(obs_list,actions)
        else:
          new_obs_list,new_actions,new_rewards = self.infer_next_states(new_obs_list,new_actions)
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
  
  def infer_next_states(self,obs_list,pred_actions):
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
      new_rewards.append(get_obs_reward(obs,position))
      obs_list[i][position[0]][position[1]]==ord(self.ant_self_character)
      get_new_reward_end=time.time()

    get_new_actions_start=time.time()
    #infer on those observations, get new actions, and get rewards
    new_predicted_rewards,_ = self.infer(obs_list,dreaming=True)
    new_actions = [np.argmax(x) for x in new_predicted_rewards]
    get_new_actions_end=time.time()


    #print time analysis
    # print('time_spent_moving_one:',sum(time_spent_moving_one))
    # print('time_spent_finding_self:',sum(time_spent_finding_self))
    # print('time_spent_getting_actions:',get_new_actions_end-get_new_actions_start)
    # print('time_spent_getting_reward:',get_new_reward_end-get_new_reward_start)

    #return new observations, actions, rewards, and new_positions
    return obs_list,new_actions,new_rewards
  

  def pad_ant_obs_list(self,obs,history):
    def history_obs_to_obs(history):
      # print([len(h['obs']) for h in history])
      # print([len(h['obs'][0]) for h in history])
      return [h['obs'] for h in history]
    hist_obs = history_obs_to_obs(history)
    # print('len(hist_obs)',len(hist_obs))
    # print('len(hist_obs)',[len(h) for h in hist_obs])

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
    assert hist_obs_np.shape[0] == self.max_sequence_length
    assert hist_obs_np.shape[1] == self.max_input_size
    assert hist_obs_np.shape[2] == self.max_input_size
      # print('hist_obs_np shape is',hist_obs_np.shape)
      
    return hist_obs_np 
  
  
