"""Extreme Tail Risk Module: catastrophic AI failures using Generalized Pareto Distribution."""
import numpy as np
from scipy import stats


def model_extreme_risks(df, extreme_config, rng=None):
    """
    Model catastrophic failure events using extreme value theory (GPD).
    """
    if rng is None:
        rng = np.random.RandomState(0)
    
    n = len(df)
    tail_index = extreme_config.get('tail_index', 0.3)
    threshold_q = extreme_config.get('threshold_quantile', 0.95)
    scale = extreme_config.get('scale', 0.1)
    
    # Base harm distribution
    harm_vals = df['realised_harm_t0'].values
    threshold = np.percentile(harm_vals, threshold_q * 100)
    
    # Identify systems exceeding threshold
    exceedances_mask = harm_vals > threshold
    n_exceed = np.sum(exceedances_mask)
    
    # Generate GPD tail for exceedances
    if n_exceed > 0:
        gpd_samples = stats.genpareto.rvs(
            c=tail_index, scale=scale, size=n_exceed, random_state=rng
        )
        # Add tail excess to existing harm
        catastrophic_harm = np.zeros(n)
        catastrophic_harm[exceedances_mask] = threshold + gpd_samples
    else:
        catastrophic_harm = np.zeros(n)
    
    df['catastrophic_harm'] = catastrophic_harm
    df['is_catastrophic'] = exceedances_mask.astype(int)
    
    # Goodness-of-fit diagnostics
    gof_results = {}
    if n_exceed > 5:
        exceedances = harm_vals[exceedances_mask] - threshold
        exceedances = exceedances[exceedances > 0]
        if len(exceedances) > 5:
            # Fit GPD to exceedances
            try:
                fit_params = stats.genpareto.fit(exceedances, floc=0)
                # KS test
                ks_stat, ks_p = stats.kstest(exceedances, 'genpareto', fit_params)
                gof_results = {
                    'fitted_shape': float(fit_params[0]),
                    'fitted_scale': float(fit_params[2]),
                    'ks_statistic': float(ks_stat),
                    'ks_p_value': float(ks_p),
                    'n_exceedances': int(len(exceedances)),
                    'configured_tail_index': tail_index,
                    'gof_pass': ks_p > 0.05,
                }
            except Exception:
                gof_results = {'error': 'GPD fit failed', 'n_exceedances': int(len(exceedances))}
    
    return df, gof_results
