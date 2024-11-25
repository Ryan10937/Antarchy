import random
class entity():
  '''
  Class for ants and food to inherit from
  Where food can be prey instead of just fruit
  '''
  def __init__(self,position,map_size_x,map_size_y,display_character,ID):
    self.display_character = display_character
    self.ID = ID
    self.position = position
    self.health = 10
    self.damage = 0
    self.max_movement_speed = 1
    self.obs_range = 1
    self.obs = []
    self.is_alive = True

    self.map_size_x = map_size_x
    self.map_size_y = map_size_y

    self.wall_bumps = 0

    self.log_folder = './logs/log/'
    self.name = ''

  def get_stats(self):
    return {
      'health':self.health,
      'is_alive':self.is_alive,
      'ID':self.ID,
      'position':self.position,
      'obs_range':self.obs_range,
      }

  def move_one(self,direction):
    direction_dict = {
      0:[0,0],
      1:[1,0],
      2:[0,1],
      3:[-1,0],
      4:[0,-1],
      }
    potential_position = [
      self.position[0] + direction_dict[direction][0],
      self.position[1] + direction_dict[direction][1]
    ]
    if self.check_new_position(potential_position):
      self.position[0] = potential_position[0] 
      self.position[1] = potential_position[1]
      return True
    else:
      self.wall_bumps += 1
      return False
  def move(self,grid):
    '''
    Grid is the character array that represents the world
      If i can pass the actual world to this function, that might be better for encounters
    '''
    for _ in range(self.max_movement_speed):
      direction=self.decide_direction(grid)
      self.move_one(direction)
  def check_new_position(self,new_position):
    '''
    new_position: list of x,y coord
    obs: observation of the ant, must be at least range 1

    Placeholder method to be filled out more once I've built the Spot and World Classes
    Check if the spot the entity is attempting to move to is a valid spot to move to
    Cant move to a wall or out of bounds
      walls are defined as |
    '''
    if new_position[0] < 0 or new_position[1] < 0 or new_position[0] >= self.map_size_x or new_position[1] >= self.map_size_y:
      return False
    else:
      return True
  def decide_direction(self,grid):
    '''
    Method to decide which way an entity should move
    For now, this is a random selection, to be replaced with an 
      agent-like decision maker later 
    '''
    return random.randint(0,4)
  def log(self,message):
    with open(self.log_folder+'log.log','a') as f:
      f.write(message+'\n')