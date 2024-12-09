from entities.ant import ant
class soldier(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    self.damage = 20
    self.max_health = 300
    self.health = 300
    self.max_movement_speed = 2
    self.spawn_rate = 2
    self.name = 'soldier'
    self.display_character='0'
    self.model_path = 'brains/soldier/novice.keras'
    self.history_path = 'history/soldier/history.csv'
    self.obs_range = 2
    super().__init__(position,map_size_x,map_size_y,display_character,ID)

  def get_species_reward(self,obs,action):
    return self.ants_eaten
    
    