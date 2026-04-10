"""Multi-objective Policy Optimisation using NSGA-II (standalone implementation)."""
import numpy as np


def fast_non_dominated_sort(objectives):
    """Perform fast non-dominated sorting."""
    n = len(objectives)
    domination_count = np.zeros(n, dtype=int)
    dominated_set = [[] for _ in range(n)]
    rank = np.zeros(n, dtype=int)
    fronts = [[]]
    
    for i in range(n):
        for j in range(i + 1, n):
            if _dominates(objectives[i], objectives[j]):
                dominated_set[i].append(j)
                domination_count[j] += 1
            elif _dominates(objectives[j], objectives[i]):
                dominated_set[j].append(i)
                domination_count[i] += 1
        
        if domination_count[i] == 0:
            rank[i] = 0
            fronts[0].append(i)
    
    front_idx = 0
    while fronts[front_idx]:
        next_front = []
        for i in fronts[front_idx]:
            for j in dominated_set[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    rank[j] = front_idx + 1
                    next_front.append(j)
        front_idx += 1
        fronts.append(next_front)
    
    return fronts[:-1], rank


def _dominates(obj_a, obj_b):
    """Check if solution a dominates solution b (all objectives minimised)."""
    return np.all(obj_a <= obj_b) and np.any(obj_a < obj_b)


def crowding_distance(objectives, front):
    """Compute crowding distance for solutions in a front."""
    n = len(front)
    if n <= 2:
        return np.full(n, np.inf)
    
    distances = np.zeros(n)
    n_obj = objectives.shape[1]
    
    for m in range(n_obj):
        sorted_idx = np.argsort(objectives[front, m])
        distances[sorted_idx[0]] = np.inf
        distances[sorted_idx[-1]] = np.inf
        
        obj_range = objectives[front[sorted_idx[-1]], m] - objectives[front[sorted_idx[0]], m]
        if obj_range > 0:
            for i in range(1, n - 1):
                distances[sorted_idx[i]] += (
                    objectives[front[sorted_idx[i + 1]], m] -
                    objectives[front[sorted_idx[i - 1]], m]
                ) / obj_range
    
    return distances


def run_nsga2(evaluate_fn, n_gen=30, pop_size=60, seed=42):
    """
    Run NSGA-II optimisation to find Pareto-optimal threshold profiles.
    Standalone implementation.
    """
    rng = np.random.RandomState(seed)
    n_var = 5
    xl = np.array([0.1, 0.1, 0.1, 0.1, 0.1])
    xu = np.array([0.9, 0.9, 0.9, 0.9, 0.9])
    
    population = rng.uniform(size=(pop_size, n_var)) * (xu - xl) + xl
    
    def evaluate_pop(pop):
        F = np.zeros((len(pop), 4))
        for i, x in enumerate(pop):
            profile = {
                'safety_gate': float(x[0]),
                'evidence_gate': float(x[1]),
                'bias_gate': float(x[2]),
                'calibration_gate': float(x[3]),
                'traceability_gate': float(x[4]),
            }
            try:
                metrics = evaluate_fn(profile)
                F[i, 0] = -metrics.get('unsafe_detection_rate', 0)
                F[i, 1] = -metrics.get('safe_throughput', 0)
                F[i, 2] = metrics.get('false_negative_harm', 0)
                F[i, 3] = metrics.get('mean_total_friction', 0)
            except Exception:
                F[i] = [0, 0, 1e6, 1e6]
        return F
    
    objectives = evaluate_pop(population)
    
    for gen in range(n_gen):
        offspring = np.zeros_like(population)
        for i in range(0, pop_size, 2):
            p1, p2 = rng.choice(pop_size, 2, replace=False)
            beta = rng.uniform(size=n_var)
            offspring[i] = beta * population[p1] + (1 - beta) * population[p2]
            if i + 1 < pop_size:
                offspring[i + 1] = (1 - beta) * population[p1] + beta * population[p2]
        
        for i in range(pop_size):
            for j in range(n_var):
                if rng.random() < 0.2:
                    offspring[i, j] += rng.normal(0, 0.1)
        
        offspring = np.clip(offspring, xl, xu)
        offspring_obj = evaluate_pop(offspring)
        
        combined_pop = np.vstack([population, offspring])
        combined_obj = np.vstack([objectives, offspring_obj])
        
        fronts, ranks = fast_non_dominated_sort(combined_obj)
        
        next_pop = []
        for front in fronts:
            if len(next_pop) + len(front) <= pop_size:
                next_pop.extend(front)
            else:
                cd = crowding_distance(combined_obj, front)
                remaining = pop_size - len(next_pop)
                sorted_by_cd = np.argsort(-cd)
                next_pop.extend([front[i] for i in sorted_by_cd[:remaining]])
                break
        
        if len(next_pop) == 0:
            break
            
        population = combined_pop[next_pop]
        objectives = combined_obj[next_pop]
    
    fronts, ranks = fast_non_dominated_sort(objectives)
    pareto_idx = fronts[0] if fronts else list(range(min(10, len(population))))
    
    pareto_profiles = []
    for idx in pareto_idx:
        x = population[idx]
        profile = {
            'safety_gate': float(x[0]),
            'evidence_gate': float(x[1]),
            'bias_gate': float(x[2]),
            'calibration_gate': float(x[3]),
            'traceability_gate': float(x[4]),
        }
        pareto_profiles.append(profile)
    
    pareto_objectives = objectives[pareto_idx].copy()
    pareto_objectives[:, 0] *= -1
    pareto_objectives[:, 1] *= -1
    
    return pareto_profiles, pareto_objectives


def identify_sweet_spot(pareto_profiles, pareto_objectives,
                        min_detection=0.7, min_throughput=0.5):
    """Identify policies meeting minimum detection and throughput constraints."""
    if len(pareto_objectives) == 0:
        return [], np.array([])
    
    mask = (
        (pareto_objectives[:, 0] >= min_detection) &
        (pareto_objectives[:, 1] >= min_throughput)
    )
    
    sweet_profiles = [p for p, m in zip(pareto_profiles, mask) if m]
    sweet_objectives = pareto_objectives[mask]
    
    return sweet_profiles, sweet_objectives
