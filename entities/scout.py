from entities.ant import ant
import numpy as np
class scout(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID,config=None):
    self.damage = 25
    self.max_health = 150
    self.health = 150
    self.max_movement_speed = 2
    self.spawn_rate = 3
    self.name = 'scout'
    self.display_character='|'
    self.model_path = 'brains/scout/novice.keras'
    self.history_path = 'history/scout/'
    self.obs_range = 7
    self.intelligence = 1
    self.food_eaten_last_turn = 0
    self.walls_bumped_last_turn = 0
    super().__init__(position,map_size_x,map_size_y,self.display_character,ID,self.intelligence,self.obs_range,config)


  def find_self(self,obs):
    self_obs_pos=None
    #if @ is in center, then use that, else look for @
    if obs[obs.shape[0]//2,obs.shape[1]//2] == ord('@'):
      self_obs_pos = [obs.shape[0]//2,obs.shape[1]//2]
    else:
      for i,row in enumerate(obs):
        for j,char in enumerate(row):
          if char == ord('@'):
            self_obs_pos = [i,j]
    if self_obs_pos is None:
      print(obs)
    return self_obs_pos
  def get_species_reward(self,obs):
    
    def get_distance(obs,coords,self_obs_pos):
      return np.sqrt((self_obs_pos[0]-coords[0])**2 + (self_obs_pos[1]-coords[1])**2) 

    obs = np.array(obs)
    reward = 0

    found_hash = 0
    found_space = 0
    found_food = 0
    
    self_obs_pos = self.find_self(obs)
    for i,row in enumerate(obs):
      for j,char in enumerate(row):
        if char in [ord('#')]:
          found_hash+=1
          reward -= 5 * (1/get_distance(obs,[i,j],self_obs_pos)**2)
        elif char in [ord(' ')]:
          found_space+=1
          reward += 2 * (1/get_distance(obs,[i,j],self_obs_pos)**2)
        elif char in [ord('%')]:
          found_food+=1
          reward += 10 * (1/get_distance(obs,[i,j],self_obs_pos)**2)
    # return reward + 10*self.get_food_eaten_this_turn() if self.is_alive else -100
    # return reward + 10*self.get_food_eaten_this_turn()
    
    return reward 


  def get_food_eaten_this_turn(self):
    food_eaten_this_turn = self.food_eaten - self.food_eaten_last_turn
    self.food_eaten_last_turn = self.food_eaten
    return food_eaten_this_turn
  