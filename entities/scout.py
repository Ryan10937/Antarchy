from entities.ant import ant
class scout(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    self.damage = 15
    self.max_health = 150
    self.health = 150
    self.max_movement_speed = 2
    self.spawn_rate = 5
    self.name = 'scout'
    self.display_character='|'
    self.model_path = 'brains/scout/novice.keras'
    self.history_path = 'history/scout/history.csv'
    self.obs_range = 5
    super().__init__(position,map_size_x,map_size_y,display_character,ID)

  def get_species_reward(self,obs,action):
    return self.food_eaten #this might be confusing because its total food eaten, not food eaten this turn