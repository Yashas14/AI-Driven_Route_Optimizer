# SmartRoute Pro — TSP Solvers
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad
#
# Four route optimization algorithms, from fast heuristic to evolutionary:
#   1. Nearest Neighbor   — O(n²) greedy baseline
#   2. 2-Opt              — local search improvement
#   3. Simulated Annealing — temperature-based global search
#   4. Genetic Algorithm   — evolutionary population-based optimizer

import math
import random
from typing import List, Tuple

import numpy as np

from app.utils.geo import total_route_distance


def nearest_neighbor(dist_matrix: np.ndarray, start: int = 0) -> List[int]:
    """Greedy nearest-neighbor: start at a node, always visit the closest unvisited next."""
    n = dist_matrix.shape[0]
    visited = {start}
    route = [start]
    current = start

    for _ in range(n - 1):
        nearest = -1
        best_dist = float("inf")
        for j in range(n):
            if j not in visited and dist_matrix[current, j] < best_dist:
                best_dist = dist_matrix[current, j]
                nearest = j
        visited.add(nearest)
        route.append(nearest)
        current = nearest

    return route


def two_opt(
    route: List[int],
    dist_matrix: np.ndarray,
    max_iterations: int = 1000,
) -> Tuple[List[int], float]:
    """Improve a route by repeatedly reversing sub-segments that reduce total distance."""
    best = list(route)
    best_dist = total_route_distance(best, dist_matrix)
    improved = True
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                new_route = best[:i] + best[i : j + 1][::-1] + best[j + 1 :]
                new_dist = total_route_distance(new_route, dist_matrix)
                if new_dist < best_dist - 1e-10:
                    best = new_route
                    best_dist = new_dist
                    improved = True
                    break
            if improved:
                break

    return best, best_dist


def simulated_annealing(
    dist_matrix: np.ndarray,
    initial_temp: float = 10000.0,
    cooling_rate: float = 0.9995,
    min_temp: float = 1.0,
    seed: int = 42,
) -> Tuple[List[int], float]:
    """SA-based TSP: accept worse solutions with decreasing probability to escape local optima."""
    rng = random.Random(seed)
    n = dist_matrix.shape[0]

    current = nearest_neighbor(dist_matrix)
    current_dist = total_route_distance(current, dist_matrix)
    best = list(current)
    best_dist = current_dist
    temp = initial_temp

    while temp > min_temp:
        i, j = sorted(rng.sample(range(n), 2))
        candidate = current[:i] + current[i : j + 1][::-1] + current[j + 1 :]
        candidate_dist = total_route_distance(candidate, dist_matrix)
        delta = candidate_dist - current_dist

        if delta < 0 or rng.random() < math.exp(-delta / temp):
            current = candidate
            current_dist = candidate_dist
            if current_dist < best_dist:
                best = list(current)
                best_dist = current_dist

        temp *= cooling_rate

    return best, best_dist


def genetic_algorithm(
    dist_matrix: np.ndarray,
    population_size: int = 100,
    generations: int = 300,
    mutation_rate: float = 0.02,
    crossover_rate: float = 0.85,
    elitism: int = 5,
    seed: int = 42,
) -> Tuple[List[int], float]:
    """Genetic algorithm TSP: ordered crossover, swap mutation, tournament selection."""
    rng = random.Random(seed)
    n = dist_matrix.shape[0]

    if n <= 3:
        route = list(range(n))
        return route, total_route_distance(route, dist_matrix)

    def fitness(route: List[int]) -> float:
        return 1.0 / (total_route_distance(route, dist_matrix) + 1e-10)

    def create_individual() -> List[int]:
        ind = list(range(n))
        rng.shuffle(ind)
        return ind

    def tournament_select(pop: List[List[int]], fits: List[float], k: int = 5) -> List[int]:
        contestants = rng.sample(range(len(pop)), min(k, len(pop)))
        winner = max(contestants, key=lambda i: fits[i])
        return list(pop[winner])

    def ordered_crossover(p1: List[int], p2: List[int]) -> List[int]:
        size = len(p1)
        start, end = sorted(rng.sample(range(size), 2))
        child = [-1] * size
        child[start : end + 1] = p1[start : end + 1]
        inherited = set(child[start : end + 1])
        pos = (end + 1) % size
        for gene in p2:
            if gene not in inherited:
                child[pos] = gene
                pos = (pos + 1) % size
        return child

    def mutate(route: List[int]) -> List[int]:
        r = list(route)
        if rng.random() < mutation_rate:
            i, j = rng.sample(range(n), 2)
            r[i], r[j] = r[j], r[i]
        return r

    population = [create_individual() for _ in range(population_size - 1)]
    population.append(nearest_neighbor(dist_matrix))

    best_route: List[int] = []
    best_fitness = -1.0

    for _ in range(generations):
        fits = [fitness(ind) for ind in population]
        sorted_idx = sorted(range(len(population)), key=lambda i: fits[i], reverse=True)

        if fits[sorted_idx[0]] > best_fitness:
            best_fitness = fits[sorted_idx[0]]
            best_route = list(population[sorted_idx[0]])

        new_pop = [list(population[sorted_idx[i]]) for i in range(elitism)]
        while len(new_pop) < population_size:
            p1 = tournament_select(population, fits)
            p2 = tournament_select(population, fits)
            child = ordered_crossover(p1, p2) if rng.random() < crossover_rate else list(p1)
            child = mutate(child)
            new_pop.append(child)

        population = new_pop

    best_dist = total_route_distance(best_route, dist_matrix)
    return best_route, best_dist


ALGORITHMS = {
    "nearest_neighbor": "Nearest Neighbor (fast baseline)",
    "two_opt": "2-Opt Local Search",
    "simulated_annealing": "Simulated Annealing",
    "genetic_algorithm": "Genetic Algorithm (best quality)",
}


def solve_tsp(
    dist_matrix: np.ndarray,
    algorithm: str = "genetic_algorithm",
    **kwargs,
) -> Tuple[List[int], float]:
    """Solve TSP using the chosen algorithm. Returns (route, total_distance)."""
    if algorithm == "nearest_neighbor":
        route = nearest_neighbor(dist_matrix, **kwargs)
        return route, total_route_distance(route, dist_matrix)
    if algorithm == "two_opt":
        initial = nearest_neighbor(dist_matrix)
        return two_opt(initial, dist_matrix, **kwargs)
    if algorithm == "simulated_annealing":
        return simulated_annealing(dist_matrix, **kwargs)
    if algorithm == "genetic_algorithm":
        return genetic_algorithm(dist_matrix, **kwargs)
    raise ValueError(f"Unknown algorithm: {algorithm}. Choose from {list(ALGORITHMS.keys())}")
