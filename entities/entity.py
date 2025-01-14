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

    self.direction_dict = {
      0:[0,0],
      1:[1,0],
      2:[0,1],
      3:[-1,0],
      4:[0,-1],
      }

  def get_stats(self):
    return {
      'health':self.health,
      'is_alive':self.is_alive,
      'ID':self.ID,
      'position':self.position,
      'obs_range':self.obs_range,
      }

  def move_one(self,direction):
    
    potential_position = [
      self.position[0] + self.direction_dict[direction][0],
      self.position[1] + self.direction_dict[direction][1]
    ]
    if self.check_new_position(potential_position):
      self.position[0] = potential_position[0] 
      self.position[1] = potential_position[1]
      return True #unused return value
    else:
      self.wall_bumps += 1
      return False #unused return value
  def move(self,grid,action):
    '''
    Grid is the character array that represents the world
      If i can pass the actual world to this function, that might be better for encounters
    '''
    for _ in range(self.max_movement_speed):
      # direction=self.decide_direction(grid,action)
      self.move_one(action)
      # if on a non_space or species spot, break
      
      if self.check_to_stop(grid):
        break
  def check_to_stop(self,grid):
    #stop if there would be a fight/food
    grid_spot = grid[self.position[0],self.position[1]]
    if len([e for e in self.get_entities_in_range(grid) if e.name!=self.name])>0:
      return True
    elif grid_spot.character == self.display_character:
      #if same species, keep moving
      return False
    elif grid_spot.character == ' ':
      #if blank, keep moving
      return False
    elif grid_spot.character == 'X':#if there is more than one entity
      if all([x.display_character==self.display_character for x in grid_spot.entities]):
        #if all of these entities are the same species, move along
        return False
      else:
        #if any of them are non-self species, stop.
        return True
    else:
      return True

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
  # def decide_direction(self,grid):
  #   '''
  #   Method to decide which way an entity should move
  #   For now, this is a random selection, to be replaced with an 
  #     agent-like decision maker later 
  #   '''
  #   return random.randint(0,4)
  def log(self,message):
    with open(self.log_folder+'log.log','a') as f:
      f.write(message+'\n')