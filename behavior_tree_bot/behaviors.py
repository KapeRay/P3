import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from math import inf


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def spread_to_strongest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    strongest_neutral_planet = max(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not weakest_planet or not strongest_neutral_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, weakest_planet.ID, strongest_neutral_planet.ID, weakest_planet.num_ships / 2)

def defend(state):
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return

    def strength(p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)

    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    strong_planets = [planet for planet in my_planets if strength(planet) > avg]

    if (not weak_planets) or (not strong_planets):
        return

    weak_planets = iter(sorted(weak_planets, key=strength))
    strong_planets = iter(sorted(strong_planets, key=strength, reverse=True))

    try:
        weak_planet = next(weak_planets)
        strong_planet = next(strong_planets)
        while True:
            need = int(avg - strength(weak_planet))
            have = int(strength(strong_planet) - avg)

            if have >= need > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, need)
                weak_planet = next(weak_planets)
            elif have > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, have)
                strong_planet = next(strong_planets)
            else:
                strong_planet = next(strong_planets)

    except StopIteration:
        return

#Steal behavior
def steal(state):
    # Create list of of owned planets sorted by descending order
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    enemy_fleet = [fleet for fleet in state.enemy_fleets()
                      if not any(my_fleet.destination_planet == fleet.destination_planet for my_fleet in state.my_fleets())]
    enemy_fleet = iter(sorted(enemy_fleet, key=lambda p: p.num_ships, reverse=True))

    try:
        my_planet = next(my_planets)
        target_fleet = next(enemy_fleet)
        while True:
            required_ships = target_fleet.num_ships + 1

            if my_planet.num_ships > required_ships:
                return issue_order(state, my_planet.ID, target_fleet.destination_planet, required_ships)
            else:
                target_fleet = next(enemy_fleet)

    except StopIteration:
        return False

#spread to capturable neutral planets
def spread(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)


    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            if target_planet.owner == 0:
                required_ships = target_planet.num_ships + 1
            else:
                required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                target_planet = next(target_planets)

    except StopIteration:
        return

def newAttack(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)
    target_planets = iter(enemy_planets)

    #success = False

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                #success = True
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return

def kamikaze(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    enemy_fleet = [fleet for fleet in state.enemy_fleets()
                      if not any(my_fleet.destination_planet == fleet.destination_planet for my_fleet in state.my_fleets())]
    enemy_fleet = iter(sorted(enemy_fleet, key=lambda p: p.num_ships, reverse=True))

    try:
        my_planet = next(my_planets)
        target_fleet = next(enemy_fleet)
        while True:
            enemy_required_ships = target_fleet.num_ships + 1

            if my_planet.num_ships < enemy_required_ships:
                return issue_order(state, my_planet.ID, target_fleet.destination_planet, my_planet.num_ships)
            else:
                target_fleet = next(enemy_fleet)

    except StopIteration:
        return False
    
def ditch(state):
    activated = False
    ascnd_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    for planet in state.my_planets():
        for enemy in state.enemy_fleets():
            if enemy.destination_planet == planet.ID and \
               enemy.num_ships > planet.num_ships:
               #enemy.turns_remaining <= 1:
                if planet.num_ships <= 1:
                    continue
                else:
                    issue_order(state, planet.ID, ascnd_planets[0].ID, planet.num_ships - 1)
                    activated = True
            else:
                continue

    return activated

