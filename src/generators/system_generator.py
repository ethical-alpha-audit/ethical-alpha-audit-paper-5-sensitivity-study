"""System Generator: Generate synthetic AI systems using Gaussian copula."""
import numpy as np
import pandas as pd
from scipy import stats
from ..utils.helpers import build_correlation_matrix, sigmoid


def generate_systems(config, n_systems, seed=42):
    """
    Generate n_systems synthetic AI systems using Gaussian copula with
    marginal distributions and correlation matrix from config.
    
    Returns a DataFrame with all latent traits.
    """
    rng = np.random.RandomState(seed)
    marginals = config['marginals']
    
    # Build correlation matrix
    corr_mat, corr_vars = build_correlation_matrix(config)
    
    # Generate correlated uniform samples via Gaussian copula
    n_corr = len(corr_vars)
    L = np.linalg.cholesky(corr_mat)
    z = rng.randn(n_systems, n_corr)
    z_corr = z @ L.T
    u_corr = stats.norm.cdf(z_corr)
    
    # Map to marginal distributions
    systems = {}
    for i, var_name in enumerate(corr_vars):
        m = marginals[var_name]
        systems[var_name] = _inverse_marginal(u_corr[:, i], m)
    
    # Generate uncorrelated variables
    uncorrelated_vars = [
        'deployment_volume', 'harm_severity', 'data_shift_rate',
        'claimed_performance', 'fallback_safety_delta'
    ]
    for var_name in uncorrelated_vars:
        if var_name not in systems and var_name in marginals:
            m = marginals[var_name]
            u = rng.uniform(size=n_systems)
            systems[var_name] = _inverse_marginal(u, m)
    
    df = pd.DataFrame(systems)
    df['system_id'] = np.arange(n_systems)
    
    return df


def _inverse_marginal(u, marginal_spec):
    """Map uniform [0,1] samples to the specified marginal distribution."""
    dist = marginal_spec['distribution']
    params = marginal_spec['params']
    
    # Clip to avoid boundary issues
    u = np.clip(u, 1e-8, 1 - 1e-8)
    
    if dist == 'beta':
        return stats.beta.ppf(u, params['a'], params['b'])
    elif dist == 'lognormal':
        return stats.lognorm.ppf(u, s=params['sigma'], scale=np.exp(params['mean']))
    elif dist == 'normal':
        return stats.norm.ppf(u, loc=params.get('mean', 0), scale=params.get('std', 1))
    elif dist == 'uniform':
        return stats.uniform.ppf(u, loc=params.get('low', 0),
                                  scale=params.get('high', 1) - params.get('low', 0))
    else:
        raise ValueError(f"Unknown distribution: {dist}")


def classify_systems(df, config, unsafe_base_rate=0.20):
    """
    Classify systems as truly safe or unsafe based on latent traits.
    Uses intrinsic_safety as the primary determinant with the specified base rate.
    """
    # Sort by intrinsic safety and mark bottom fraction as unsafe
    safety_scores = df['intrinsic_safety'].values
    threshold = np.percentile(safety_scores, unsafe_base_rate * 100)
    df['truly_unsafe'] = (safety_scores <= threshold).astype(int)
    
    return df
