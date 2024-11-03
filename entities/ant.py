from entities.entity import entity

class ant(entity):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 10
    self.health = 200
    self.max_movement_speed = 3

    # self.gender = True
    # self.attractiveness_score = 0

  def attack(self,entity):
    pass