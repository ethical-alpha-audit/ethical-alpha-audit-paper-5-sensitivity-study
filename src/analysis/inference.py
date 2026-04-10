"""Statistical Inference: bootstrap tests, dominance tests, Bayesian intervals."""
import numpy as np
from scipy import stats


def bootstrap_ci(data, statistic_fn=np.mean, n_bootstrap=1000, ci=0.95, seed=42):
    """Compute bootstrap confidence interval for a statistic."""
    rng = np.random.RandomState(seed)
    boot_stats = np.zeros(n_bootstrap)
    n = len(data)
    for i in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        boot_stats[i] = statistic_fn(sample)
    
    alpha = (1 - ci) / 2
    lower = np.percentile(boot_stats, alpha * 100)
    upper = np.percentile(boot_stats, (1 - alpha) * 100)
    return float(lower), float(upper), boot_stats


def bootstrap_difference_test(data_a, data_b, statistic_fn=np.mean, 
                               n_bootstrap=1000, seed=42):
    """
    Bootstrap test for difference between two groups.
    Returns: observed difference, CI, p-value (two-sided).
    """
    rng = np.random.RandomState(seed)
    obs_diff = statistic_fn(data_a) - statistic_fn(data_b)
    
    # Permutation-style bootstrap under H0
    combined = np.concatenate([data_a, data_b])
    n_a = len(data_a)
    boot_diffs = np.zeros(n_bootstrap)
    
    for i in range(n_bootstrap):
        perm = rng.permutation(combined)
        boot_a = perm[:n_a]
        boot_b = perm[n_a:]
        boot_diffs[i] = statistic_fn(boot_a) - statistic_fn(boot_b)
    
    p_value = np.mean(np.abs(boot_diffs) >= np.abs(obs_diff))
    ci_lower = np.percentile(boot_diffs, 2.5)
    ci_upper = np.percentile(boot_diffs, 97.5)
    
    return {
        'observed_difference': float(obs_diff),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
        'p_value': float(p_value),
    }


def policy_dominance_test(metrics_a, metrics_b, n_bootstrap=1000, seed=42):
    """
    Test whether policy A dominates policy B.
    Dominance: A >= B on detection and throughput, A <= B on harm and friction,
    with at least one strict improvement.
    
    Returns probability of dominance via bootstrap.
    """
    rng = np.random.RandomState(seed)
    
    detection_a = np.array(metrics_a['detection_samples'])
    detection_b = np.array(metrics_b['detection_samples'])
    throughput_a = np.array(metrics_a['throughput_samples'])
    throughput_b = np.array(metrics_b['throughput_samples'])
    harm_a = np.array(metrics_a['harm_samples'])
    harm_b = np.array(metrics_b['harm_samples'])
    friction_a = np.array(metrics_a['friction_samples'])
    friction_b = np.array(metrics_b['friction_samples'])
    
    n = min(len(detection_a), len(detection_b), n_bootstrap)
    dominance_count = 0
    
    for i in range(n):
        idx_a = rng.randint(len(detection_a))
        idx_b = rng.randint(len(detection_b))
        
        better_or_equal = (
            detection_a[idx_a] >= detection_b[idx_b] and
            throughput_a[idx_a] >= throughput_b[idx_b] and
            harm_a[idx_a] <= harm_b[idx_b] and
            friction_a[idx_a] <= friction_b[idx_b]
        )
        strictly_better = (
            detection_a[idx_a] > detection_b[idx_b] or
            throughput_a[idx_a] > throughput_b[idx_b] or
            harm_a[idx_a] < harm_b[idx_b] or
            friction_a[idx_a] < friction_b[idx_b]
        )
        
        if better_or_equal and strictly_better:
            dominance_count += 1
    
    return float(dominance_count / n)


def bayesian_rate_interval(successes, total, alpha0=1.0, beta0=1.0, ci=0.95):
    """
    Compute Bayesian credible interval for a rate using Beta posterior.
    Beta(alpha0, beta0) prior.
    """
    alpha_post = alpha0 + successes
    beta_post = beta0 + (total - successes)
    
    tail = (1 - ci) / 2
    lower = stats.beta.ppf(tail, alpha_post, beta_post)
    upper = stats.beta.ppf(1 - tail, alpha_post, beta_post)
    mean = alpha_post / (alpha_post + beta_post)
    
    return {
        'posterior_mean': float(mean),
        'ci_lower': float(lower),
        'ci_upper': float(upper),
        'alpha_posterior': float(alpha_post),
        'beta_posterior': float(beta_post),
    }


def run_inference(replicate_results, n_bootstrap=1000, seed=42):
    """
    Run full inference suite on replicate results.
    
    Args:
        replicate_results: list of dicts with metrics from each replicate
    
    Returns:
        inference_results dict
    """
    results = {}
    
    # Extract metric arrays across replicates
    detection_rates = np.array([r['unsafe_detection_rate'] for r in replicate_results])
    throughputs = np.array([r['safe_throughput'] for r in replicate_results])
    harms = np.array([r['false_negative_harm'] for r in replicate_results])
    frictions = np.array([r['mean_total_friction'] for r in replicate_results])
    
    # Bootstrap CIs for each metric
    for name, data in [('detection', detection_rates), ('throughput', throughputs),
                       ('harm', harms), ('friction', frictions)]:
        lo, hi, _ = bootstrap_ci(data, n_bootstrap=n_bootstrap, seed=seed)
        results[f'{name}_mean'] = float(np.mean(data))
        results[f'{name}_ci_lower'] = lo
        results[f'{name}_ci_upper'] = hi
        results[f'{name}_std'] = float(np.std(data))
    
    # Bayesian rate intervals for detection and throughput
    for name, rates in [('detection', detection_rates), ('throughput', throughputs)]:
        mean_rate = np.mean(rates)
        n_eff = len(rates) * 1000  # effective sample size approximation
        successes = int(mean_rate * n_eff)
        bay = bayesian_rate_interval(successes, n_eff)
        results[f'{name}_bayesian'] = bay
    
    return results
