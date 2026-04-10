"""Decision Curve Analysis for policy selection."""
import numpy as np


def compute_net_benefit(truly_unsafe, approved, threshold_prob):
    """
    Compute net benefit at a given threshold probability.
    
    Net benefit = (TP/n) - (FP/n) * (pt / (1 - pt))
    where pt is the threshold probability.
    """
    n = len(truly_unsafe)
    tp = np.sum((truly_unsafe == 1) & (approved == 0))  # correctly rejected unsafe
    fp = np.sum((truly_unsafe == 0) & (approved == 0))  # incorrectly rejected safe
    
    if threshold_prob >= 1 or threshold_prob <= 0:
        return 0.0
    
    weight = threshold_prob / (1 - threshold_prob)
    nb = (tp / n) - (fp / n) * weight
    return float(nb)


def run_dca(df, policy_results_dict, threshold_range=None):
    """
    Run Decision Curve Analysis across multiple policies.
    
    Args:
        df: DataFrame with truly_unsafe column
        policy_results_dict: {policy_name: policy_results_df}
        threshold_range: array of threshold probabilities
    
    Returns:
        dca_results dict with thresholds and net benefits per policy
    """
    if threshold_range is None:
        threshold_range = np.linspace(0.01, 0.99, 50)
    
    truly_unsafe = df['truly_unsafe'].values
    
    policies = {}
    for policy_name, policy_results in policy_results_dict.items():
        approved = policy_results['approved'].values
        net_benefits = []
        for pt in threshold_range:
            nb = compute_net_benefit(truly_unsafe, approved, pt)
            net_benefits.append(nb)
        policies[policy_name] = net_benefits
    
    # Add "treat all" and "treat none" reference policies
    n = len(truly_unsafe)
    prevalence = np.mean(truly_unsafe)
    treat_all = []
    for pt in threshold_range:
        if pt >= 1:
            treat_all.append(0)
        else:
            nb = prevalence - (1 - prevalence) * pt / (1 - pt)
            treat_all.append(nb)
    policies['Reject all (reference)'] = treat_all
    policies['Approve all (reference)'] = [0.0] * len(threshold_range)
    
    return {
        'thresholds': threshold_range.tolist(),
        'policies': policies,
        'prevalence': float(prevalence),
    }
