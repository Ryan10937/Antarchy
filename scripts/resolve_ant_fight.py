import numpy as np
def ant_fight(entities:list,max_fight_duration=100):
  #im going to make this assuming the ants have the same range
  #in the future, if/when they dont here is what im thinking:
    #pass grid, look for all ants within largest_ant_range
    #if any of them are in range, add them to the fight.
    #when attacking, check for being in range first. If not, move them one step closer
    #to that target instead.
  fight_resolved = False
  for _ in range(max_fight_duration):
    for ant in entities:
      if ant.name == 'Food':
        continue
      if ant.is_alive == False:
        continue
      attackable_ants = [oant for oant in entities if oant.name != ant.name and oant.is_alive]
      # print("len(attackable_ants)",len(attackable_ants))
      # print("attackable_ants",attackable_ants)
      # print("attackable_ants alive",[a.is_alive for a in attackable_ants])
      if len(attackable_ants) == 0:
        fight_resolved = True
        break
      ant.fight(attackable_ants)
    if fight_resolved:
      break


    species = [ant.name for ant in entities if ant.is_alive]
    if len(np.unique(species)) <= 1:
      break