from entities.ant import ant
import numpy as np
class runner(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID,config=None):
    self.damage = 20
    self.max_health = 100
    self.health = 100
    self.max_movement_speed = 2
    self.spawn_rate = 3
    self.name = 'runner'
    self.display_character='9'
    self.model_path = 'brains/runner/novice.keras'
    self.history_path = 'history/runner/'
    self.obs_range = 3
    self.intelligence = 1
    self.food_eaten_last_turn = 0
    self.walls_bumped_last_turn = 0
    super().__init__(position,map_size_x,map_size_y,self.display_character,ID,self.intelligence,self.obs_range,config)
    

  def get_species_reward(self,obs,action=None):
    def get_distance(obs,coords):
      #if @ is in center, then use that, else look for @
      if obs[obs.shape[0]//2,obs.shape[1]//2] == ord('@'):
        self_obs_pos = [obs.shape[0]//2,obs.shape[1]//2]
      else:
        for i,row in enumerate(obs):
          for j,char in enumerate(row):
            if char == ord('@'):
              self_obs_pos = [i,j]
      return np.sqrt((self_obs_pos[0]-coords[0])**2 + (self_obs_pos[1]-coords[1])**2) 

    obs = np.array(obs)
    reward = 0
    for i,row in enumerate(obs):
      for j,char in enumerate(row):
        if char in [ord('#')]:
          reward -= 5 * 1/get_distance(obs,[i,j])**2
        if char in [ord('%')]:
          reward += 10 * 1/get_distance(obs,[i,j])**2
    # return reward + 10*self.get_food_eaten_this_turn() if self.is_alive else -100
    # return reward + 10*self.get_food_eaten_this_turn()
    return reward 


  def get_food_eaten_this_turn(self):
    food_eaten_this_turn = self.food_eaten - self.food_eaten_last_turn
    self.food_eaten_last_turn = self.food_eaten
    return food_eaten_this_turn
  