import numpy as np
import random
from entities.ant import ant
from entities.food import food
import copy
class spot():
  def __init__(self,position):
    self.position = position
    self.character = ' '
    self.entities = []
  def __repr__(self):
    return self.character
  def add_entity(self,new_entity):
    self.entities.append(new_entity)
    self.update_display_char()
  def remove_entity(self,entity_to_remove):
    for idx,ent in enumerate(self.entities):
      if ent.ID == entity_to_remove.ID:
        self.entities.pop(idx)
    self.update_display_char()
    
  def update_display_char(self):
    if len(self.entities) == 0:
      self.character = ' '
    elif len(self.entities) == 1:
      self.character = self.entities[0].display_character
    else:
      self.character = 'X'

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
    self.graveyard = []
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

  # def resolve_conflicts(self):
  #   for x in range(self.size[0]):
  #     for y in range(self.size[1]):
  #       if len(self.grid[x,y].entities) > 1:
  #         self._ant_conflict(self.grid[x,y])


  # def _ant_conflict(self,arena:spot):
  #   for ant in arena.entities:
  #     if ant.health <= 0:
  #       #dead ants cant move
  #       continue
  #     if ant.is_food:
  #       #food doesnt get a turn, its food
  #       continue
  #     ant.fight([ants for ants in arena.entities if ant.ID != ants.ID])
  def cleanup(self):
    for x in range(self.size[0]):
      for y in range(self.size[1]):
        for ant in self.grid[x,y].entities:
          if ant.is_alive == False:
            self.graveyard.append(ant)
            self.grid[x,y].remove_entity(ant)

  def entity_turns(self):
    for ant in self.ants:
      if ant.health <= 0:
        self.grid[ant.position[0],ant.position[1]].remove_entity(ant)
        continue
      prev_position_x = ant.position[0]
      prev_position_y = ant.position[1]
      ant.act(self.grid)
      self.grid[prev_position_x,prev_position_y].remove_entity(ant)
      self.grid[ant.position[0],ant.position[1]].add_entity(ant)
    self.cleanup()




