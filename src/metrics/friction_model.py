"""Governance Friction Model: compute audit, delay, monitoring, escalation, documentation costs."""
import numpy as np


def compute_friction(df, policy_results, friction_config, threshold_profile):
    """
    Compute governance friction components for each system.
    Returns friction cost breakdown.
    """
    n = len(df)
    approved = policy_results['approved'].values
    
    # Base costs from config
    C_audit_base = friction_config.get('C_audit_base', 1.0)
    C_delay_per = friction_config.get('C_delay_per_unit', 0.5)
    C_monitor_base = friction_config.get('C_monitor_base', 0.3)
    C_escalation_base = friction_config.get('C_escalation_base', 2.0)
    C_doc_base = friction_config.get('C_documentation_base', 0.4)
    C_max = friction_config.get('C_max', 50.0)
    
    # Stringency multiplier based on thresholds
    thresh_vals = [v for k, v in threshold_profile.items() 
                   if isinstance(v, (int, float)) and k != 'description']
    stringency = np.mean(thresh_vals) if thresh_vals else 0.5
    
    # Audit cost: scales with stringency and evidence demands
    C_audit = np.full(n, C_audit_base * (1 + stringency))
    
    # Delay cost: rejected systems incur delay
    C_delay = np.where(approved == 0, C_delay_per * (1 + stringency), 0)
    
    # Monitoring cost: approved systems need ongoing monitoring
    drift_susc = df.get('drift_susceptibility', np.zeros(n))
    if hasattr(drift_susc, 'values'):
        drift_susc = drift_susc.values
    C_monitor = np.where(approved == 1, C_monitor_base * (1 + drift_susc), 0)
    
    # Escalation cost: systems near threshold boundaries
    abstention = df.get('abstention_rate', np.zeros(n))
    if hasattr(abstention, 'values'):
        abstention = abstention.values
    C_escalation = C_escalation_base * abstention
    
    # Documentation cost: all systems
    C_documentation = np.full(n, C_doc_base * (1 + 0.5 * stringency))
    
    # Total friction per system
    total_friction = C_audit + C_delay + C_monitor + C_escalation + C_documentation
    
    # Resource constraint
    cumulative = np.cumsum(C_audit)
    capacity_exceeded = cumulative > C_max * n / 100  # normalize
    
    return {
        'C_audit': C_audit,
        'C_delay': C_delay,
        'C_monitor': C_monitor,
        'C_escalation': C_escalation,
        'C_documentation': C_documentation,
        'total_friction': total_friction,
        'mean_total_friction': float(np.mean(total_friction)),
        'total_system_friction': float(np.sum(total_friction)),
        'capacity_exceeded_pct': float(np.mean(capacity_exceeded) * 100),
    }
