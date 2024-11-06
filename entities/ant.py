from entities.entity import entity
import random
class ant(entity):
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    super().__init__(position,map_size_x,map_size_y,display_character,ID)
    self.damage = 10
    self.max_health = 200
    self.health = 200
    self.max_movement_speed = 3
    self.is_food = False
    self.food_eaten = 0
    self.ants_eaten = 0
    # self.gender = True
    # self.attractiveness_score = 0

  def fight(self,entity_list):
    #this isnt great, it will attack food or the other entity with equal chance
    #it will do for now but i would like to change it later
    random_target = random.randint(0,len(entity_list)-1)
    self.attack(entity_list[random_target])
    
  def attack(self,entity):
    entity.health -= self.damage
    if entity.health < 0:
      self.food_eaten+=1
      if entity.is_food==False:
        self.ants_eaten+=1
        entity.is_alive=False

  def act(self,grid):
    self.move(grid)
