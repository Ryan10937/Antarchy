from entities.ant import ant
class runner(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID,control):
    self.damage = 10
    self.max_health = 100
    self.health = 100
    self.max_movement_speed = 2
    self.spawn_rate = 6
    self.name = 'runner'
    self.display_character='9'
    self.model_path = 'brains/runner/novice.keras'
    self.history_path = 'history/runner/history.csv'
    self.obs_range = 3
    self.intelligence = 1
    super().__init__(position,map_size_x,map_size_y,self.display_character,ID,self.intelligence,control)
    
  def get_species_reward(self,obs,action):
    return self.food_eaten #this might be confusing because its total food eaten, not food eaten this turn
    