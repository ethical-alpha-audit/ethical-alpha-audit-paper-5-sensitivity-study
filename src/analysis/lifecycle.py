"""Lifecycle Simulation: time dynamics including decay, drift, re-audit."""
import numpy as np
import pandas as pd


def simulate_lifecycle(df, scm_params, n_timesteps=12, drift_regime='medium', rng=None):
    """
    Simulate time dynamics for approved systems over n_timesteps periods.
    
    Models: performance_decay, harm_over_time, drift detection, re-audit events.
    """
    if rng is None:
        rng = np.random.RandomState(0)
    
    n = len(df)
    rate_mult = scm_params.get('performance_decay', {}).get('rate_multiplier', 0.02)
    monitor_red = scm_params.get('performance_decay', {}).get('monitoring_reduction', 0.5)
    
    drift_multipliers = {'low': 0.5, 'medium': 1.0, 'high': 2.0}
    drift_mult = drift_multipliers.get(drift_regime, 1.0)
    
    drift_susc = df['drift_susceptibility'].values
    data_shift = df['data_shift_rate'].values
    baseline_harm = df['baseline_harm'].values
    subgroup_mult = df['subgroup_multiplier'].values
    
    # Time series storage
    performance_decay_ts = np.zeros((n, n_timesteps))
    harm_ts = np.zeros((n, n_timesteps))
    re_audit_triggered = np.zeros((n, n_timesteps), dtype=int)
    monitoring_active = np.ones(n, dtype=bool)
    
    cumulative_decay = np.zeros(n)
    
    for t in range(n_timesteps):
        # Performance decay increment
        increment = (rate_mult * drift_susc * data_shift * drift_mult *
                     (1 - monitor_red * monitoring_active.astype(float)))
        # Add noise
        increment += rng.normal(0, 0.005, n) * drift_mult
        increment = np.maximum(increment, 0)
        
        cumulative_decay += increment
        performance_decay_ts[:, t] = cumulative_decay
        
        # Harm over time
        harm_t = baseline_harm * subgroup_mult * (1 + cumulative_decay)
        harm_ts[:, t] = np.clip(harm_t, 0, 5)
        
        # Re-audit trigger: if decay exceeds threshold
        drift_threshold = 0.1
        re_audit_triggered[:, t] = (cumulative_decay > drift_threshold * (t + 1) / n_timesteps).astype(int)
        
        # If re-audit triggered, monitoring resets decay partially
        reset_mask = re_audit_triggered[:, t] == 1
        cumulative_decay[reset_mask] *= 0.5
    
    # Summary statistics
    final_decay = performance_decay_ts[:, -1]
    total_harm = np.sum(harm_ts, axis=1)
    any_reaudit = np.any(re_audit_triggered, axis=1).astype(int)
    n_reaudits = np.sum(re_audit_triggered, axis=1)
    
    lifecycle_results = {
        'performance_decay_ts': performance_decay_ts,
        'harm_ts': harm_ts,
        're_audit_triggered': re_audit_triggered,
        'final_decay': final_decay,
        'total_harm_over_time': total_harm,
        'mean_final_decay': float(np.mean(final_decay)),
        'mean_total_harm': float(np.mean(total_harm)),
        're_audit_rate': float(np.mean(any_reaudit)),
        'mean_n_reaudits': float(np.mean(n_reaudits)),
    }
    
    return lifecycle_results
