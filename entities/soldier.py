from entities.ant import ant
import numpy as np
class soldier(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID,config=None):
    self.damage = 40
    self.max_health = 300
    self.health = 300
    self.max_movement_speed = 2
    self.spawn_rate = 3
    self.name = 'soldier'
    self.display_character='0'
    self.model_path = 'brains/soldier/novice.keras'
    self.history_path = 'history/soldier/'
    self.obs_range = 2
    self.intelligence = 1
    self.ants_eaten_last_turn = 0
    self.walls_bumped_last_turn = 0
    super().__init__(position,map_size_x,map_size_y,self.display_character,ID,self.intelligence,self.obs_range,config)

  def get_species_reward(self,obs,action):
    obs = np.array(obs)
    reward = 0
    for row in obs:
      for char in row:
        if char in [ord('#')]:
          reward -= 1
        if char in [ord('X'),ord('|'),ord('9')]:
          reward += 10
    # return reward + 10*self.get_ants_eaten_this_turn() if self.is_alive else -100
    return reward + 10*self.get_ants_eaten_this_turn() 
  
  def get_ants_eaten_this_turn(self):
    ants_eaten_this_turn = self.ants_eaten - self.ants_eaten_last_turn
    self.ants_eaten_last_turn = self.ants_eaten
    return ants_eaten_this_turn
    
    