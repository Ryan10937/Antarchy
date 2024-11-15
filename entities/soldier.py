from entities.ant import ant
class soldier(ant):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 20
    self.max_health = 300
    self.health = 300
    self.max_movement_speed = 2
    self.spawn_rate = 2
    self.name = 'soldier'
    
    