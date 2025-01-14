from entities.entity import entity

class food(entity):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 0
    self.health = 20
    self.max_movement_speed = 0
    self.is_food=True
    self.name='Food'
