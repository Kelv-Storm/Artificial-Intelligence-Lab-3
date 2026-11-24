import random
from itertools import permutations


LOCATIONS = ["A", "B", "C", "D", "E", "F", "G"]
DIST = {
    "A": {"A": 0, "B": 4, "C": 8, "D": 6, "E": 7, "F": 9, "G": 5},
    "B": {"A": 4, "B": 0, "C": 5, "D": 7, "E": 3, "F": 8, "G": 6},
    "C": {"A": 8, "B": 5, "C": 0, "D": 4, "E": 6, "F": 3, "G": 7},
    "D": {"A": 6, "B": 7, "C": 4, "D": 0, "E": 5, "F": 6, "G": 8},
    "E": {"A": 7, "B": 3, "C": 6, "D": 5, "E": 0, "F": 4, "G": 6},
    "F": {"A": 9, "B": 8, "C": 3, "D": 6, "E": 4, "F": 0, "G": 5},
    "G": {"A": 5, "B": 6, "C": 7, "D": 8, "E": 6, "F": 5, "G": 0},
}
DEPOT = "A"
STOPS = [loc for loc in LOCATIONS if loc != DEPOT]      # B, C, D, E, F, G


SEED = 42              
POPULATION_SIZE = 30
GENERATIONS = 100      
TOURNAMENT_SIZE = 3
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.2
ELITE_COUNT = 2        



def route_distance(chromosome):
    """Total distance of depot -> chromosome -> depot (includes the return trip)."""
    full_route = [DEPOT] + chromosome + [DEPOT]
    return sum(DIST[full_route[i]][full_route[i + 1]] for i in range(len(full_route) - 1))


def create_random_route():
    """One valid chromosome: a random order of B..G, each used exactly once."""
    route = STOPS[:]
    random.shuffle(route)
    return route


def create_initial_population(size):
    return [create_random_route() for _ in range(size)]


def tournament_selection(population):
    """Pick a few random routes and return the one with the shortest distance."""
    contenders = random.sample(population, TOURNAMENT_SIZE)
    return min(contenders, key=route_distance)


def order_crossover(parent1, parent2):
    """
    Order Crossover (OX): copy a slice from parent 1, then fill the remaining
    positions with the missing locations in the order they appear in parent 2.
    Result: a valid route with no repeated or missing location.
    """
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[start:end + 1] = parent1[start:end + 1]            
    fill = [loc for loc in parent2 if loc not in child]     
    position = 0
    for i in range(size):
        if child[i] is None:
            child[i] = fill[position]
            position += 1
    return child


def swap_mutation(route):
    """Swap two locations: a small change that keeps the route valid."""
    mutated = route[:]
    i, j = random.sample(range(len(mutated)), 2)
    mutated[i], mutated[j] = mutated[j], mutated[i]
    return mutated


def run_ga():
    random.seed(SEED)
    population = create_initial_population(POPULATION_SIZE)
    best_route = min(population, key=route_distance)
    print(f"Seed = {SEED}, population = {POPULATION_SIZE}, generations = {GENERATIONS}")
    print(f"{'Gen':>4} | {'Best distance (km)':>18} | Best route")

    for generation in range(1, GENERATIONS + 1):
        population.sort(key=route_distance)                

        next_population = [route[:] for route in population[:ELITE_COUNT]]

      
        while len(next_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            if random.random() < CROSSOVER_RATE:
                child = order_crossover(parent1, parent2)
            else:
                child = parent1[:]
            if random.random() < MUTATION_RATE:
                child = swap_mutation(child)
            next_population.append(child)

        population = next_population
        generation_best = min(population, key=route_distance)
        if route_distance(generation_best) < route_distance(best_route):
            best_route = generation_best[:]

        if generation == 1 or generation % 10 == 0:
            shown = [DEPOT] + generation_best + [DEPOT]
            print(f"{generation:>4} | {route_distance(generation_best):>18} | {' -> '.join(shown)}")

    return best_route


if __name__ == "__main__":
    best = run_ga()
    best_full = [DEPOT] + best + [DEPOT]
    print("\n=== RESULT ===")
    print("Best route     :", " -> ".join(best_full))
    print("Total distance :", route_distance(best), "km")


    optimum = min(permutations(STOPS), key=lambda r: route_distance(list(r)))
    print("\n(Check) Brute-force optimum:", " -> ".join([DEPOT] + list(optimum) + [DEPOT]),
          "=", route_distance(list(optimum)), "km")
