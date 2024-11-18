from entities.ant import ant
class runner(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 10
    self.max_health = 100
    self.health = 100
    self.max_movement_speed = 2
    self.spawn_rate = 6
    self.name = 'runner'
    self.display_character='9'
    
    