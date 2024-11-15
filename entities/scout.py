from entities.ant import ant
class scout(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 15
    self.max_health = 150
    self.health = 150
    self.max_movement_speed = 2
    self.spawn_rate = 5
    self.name = 'scout'
    