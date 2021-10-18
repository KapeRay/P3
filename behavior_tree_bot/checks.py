

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def if_enemy_has_more_planets(state):
  return len(state.enemy_planets()) >= len(state.my_planets())

def enemy_fleet_enroute(state):
  return any(state.enemy_fleets())



