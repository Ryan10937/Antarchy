import numpy as np
import random
from entities.ant import ant
from entities.food import food

class spot():
  def __init__(self,position):
    self.position = position
    self.character = ' '
    self.entities = []
  def __repr__(self):
    return self.character
  def add_entity(self,new_entity):
    self.entities.append(new_entity)
    if len(self.entities) > 1:
      self.character = 'X'
    else:
      self.character = new_entity.display_character
  def remove_entity(self,ID):
    for idx,ent in enumerate(self.entities):
      if ent.ID == ID:
        self.entities.pop(idx)
    if len(self.entities) == 0:
      self.character = ' '
    elif len(self.entities) == 1:
      self.character = self.entities[0].display_character

class world():
  def __init__(self,x_size,y_size,num_ants,num_food):
    self.size = [x_size,y_size]
    self.grid = np.array([[spot([x,y]) for y in range(self.size[1])] for x in range(self.size[0])])
    self.ants = [ant(
      position=[random.randint(0,self.size[0]-1),random.randint(0,self.size[1]-1)],
      map_size_x=x_size,
      map_size_y=y_size,
      display_character='8',
      ID = ID,
                            ) 
                     for ID in range(num_ants)]
    self.food = [food(
      position=[random.randint(0,self.size[0]-1),random.randint(0,self.size[1]-1)],
      map_size_x=x_size,
      map_size_y=y_size,
      display_character='%',
      ID = ID+num_ants,
                            ) 
                     for ID in range(num_food)]
    self.place_ants()
    self.place_food()
  def render(self):
    print(self.grid)

  def place_ants(self):
    for at in self.ants:
      self.grid[at.position[0],at.position[1]].add_entity(at)
  def place_food(self):
    for fd in self.food:
      self.grid[fd.position[0],fd.position[1]].add_entity(fd)

  def resolve_conflicts(self):
    for x in range(self.size[0]):
      for y in range(self.size[1]):
        if len(self.grid[x,y].entities) > 1:
          self.ant_conflict(self.grid[x,y])
  def ant_conflict(self,arena:spot):
    for ant in arena.entities:
      if ant.is_food:
        #food doesnt get a turn, its food
        continue
      ant.fight([ants in arena.entities if ant.ID != ants.ID])


