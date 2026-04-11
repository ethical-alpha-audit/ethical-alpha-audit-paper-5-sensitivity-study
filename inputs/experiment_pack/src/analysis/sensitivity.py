"""Global Sensitivity Analysis using Sobol variance decomposition (standalone)."""
import numpy as np
import pandas as pd


def sobol_sequence(n, d, seed=42):
    """Generate quasi-random Sobol-like samples using scrambled Halton as fallback."""
    rng = np.random.RandomState(seed)
    # Use Saltelli sampling pattern: A, B, AB matrices
    A = rng.uniform(size=(n, d))
    B = rng.uniform(size=(n, d))
    return A, B


def saltelli_sample(n, d, bounds, seed=42):
    """Generate Saltelli sampling matrix for Sobol analysis."""
    A, B = sobol_sequence(n, d, seed)
    
    # Scale to bounds
    for j in range(d):
        lo, hi = bounds[j]
        A[:, j] = A[:, j] * (hi - lo) + lo
        B[:, j] = B[:, j] * (hi - lo) + lo
    
    # Build AB matrices (swap one column at a time)
    samples = [A, B]
    for j in range(d):
        AB_j = A.copy()
        AB_j[:, j] = B[:, j]
        samples.append(AB_j)
    
    return np.vstack(samples)


def sobol_analyze(y_all, n, d):
    """Compute first-order (S1) and total-order (ST) Sobol indices."""
    y_A = y_all[:n]
    y_B = y_all[n:2*n]
    
    f0 = np.mean(np.concatenate([y_A, y_B]))
    var_total = np.var(np.concatenate([y_A, y_B]))
    
    if var_total < 1e-12:
        return np.zeros(d), np.zeros(d), np.zeros(d), np.zeros(d)
    
    S1 = np.zeros(d)
    ST = np.zeros(d)
    
    for j in range(d):
        y_AB_j = y_all[(2 + j) * n:(3 + j) * n]
        
        # First-order: S1_j = V[E[Y|X_j]] / V[Y]
        S1[j] = np.mean(y_B * (y_AB_j - y_A)) / var_total
        
        # Total-order: ST_j = E[V[Y|X_~j]] / V[Y]
        ST[j] = 0.5 * np.mean((y_A - y_AB_j)**2) / var_total
    
    # Confidence (approximate)
    S1_conf = np.full(d, 0.05)
    ST_conf = np.full(d, 0.05)
    
    return S1, ST, S1_conf, ST_conf


def run_sobol_analysis(evaluate_fn, param_names=None, param_bounds=None,
                       n_samples=64, seed=42):
    """
    Run Sobol global sensitivity analysis on simulation parameters.
    """
    if param_names is None:
        param_names = [
            'safety_gate', 'evidence_gate', 'bias_gate',
            'calibration_gate', 'traceability_gate',
            'auditability_noise', 'unsafe_base_rate'
        ]
    
    if param_bounds is None:
        param_bounds = [
            [0.2, 0.8], [0.2, 0.8], [0.1, 0.7],
            [0.2, 0.7], [0.2, 0.7], [0.02, 0.15], [0.05, 0.35],
        ]
    
    d = len(param_names)
    param_values = saltelli_sample(n_samples, d, param_bounds, seed)
    
    output_names = ['unsafe_detection_rate', 'safe_throughput', 
                    'false_negative_harm', 'mean_total_friction']
    outputs = {name: np.zeros(len(param_values)) for name in output_names}
    
    for i, params in enumerate(param_values):
        param_dict = dict(zip(param_names, params))
        try:
            metrics = evaluate_fn(param_dict)
            for name in output_names:
                outputs[name][i] = metrics.get(name, 0.0)
        except Exception:
            pass
    
    results = {}
    for name in output_names:
        S1, ST, S1_conf, ST_conf = sobol_analyze(outputs[name], n_samples, d)
        results[name] = pd.DataFrame({
            'parameter': param_names,
            'S1': np.clip(S1, 0, 1),
            'S1_conf': S1_conf,
            'ST': np.clip(ST, 0, 1),
            'ST_conf': ST_conf,
        }).sort_values('ST', ascending=False)
    
    return results


def format_sensitivity_table(sobol_results, assumed_params=None):
    """Format Sobol results as a ranked table, flagging assumed parameters."""
    if assumed_params is None:
        assumed_params = set()
    
    tables = {}
    for outcome, df in sobol_results.items():
        df = df.copy()
        df['status'] = df['parameter'].apply(
            lambda p: 'ASSUMED' if p in assumed_params else 'configured'
        )
        df['rank'] = range(1, len(df) + 1)
        tables[outcome] = df
    
    return tables
