from entities.ant import ant
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
    
  def get_species_reward(self,obs,action):
    food_eaten_this_turn = self.get_food_eaten_this_turn()
    walls_bumped_this_turn = self.get_walls_bumped_this_turn()
    return food_eaten_this_turn - walls_bumped_this_turn

  def get_food_eaten_this_turn(self):
    food_eaten_this_turn = self.food_eaten - self.food_eaten_last_turn
    self.food_eaten_last_turn = self.food_eaten
    return food_eaten_this_turn*10
  
  def get_walls_bumped_this_turn(self):
    walls_bumped_this_turn = self.wall_bumps - self.walls_bumped_last_turn
    self.walls_bumped_last_turn = self.wall_bumps
    return walls_bumped_this_turn
    