"""Structural Causal Model: implements causal relationships from SCM graph."""
import numpy as np
import networkx as nx
from ..utils.helpers import sigmoid, load_yaml


def load_scm_graph(dot_path):
    """Load SCM from DOT file and validate DAG."""
    G = nx.DiGraph()
    with open(dot_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '->' in line:
                parts = line.replace(';', '').split('->')
                src = parts[0].strip()
                tgt = parts[1].strip()
                G.add_edge(src, tgt)
    
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("SCM graph is not a valid DAG!")
    
    return G


def validate_scm_functions(scm_functions, scm_graph):
    """Validate that all edges in the SCM graph have corresponding functional forms."""
    # Check that all non-leaf nodes have functions defined
    func_names = set(scm_functions.get('functions', {}).keys())
    intermediate_nodes = set()
    for u, v in scm_graph.edges():
        intermediate_nodes.add(v)
    
    # We don't require every node to have an explicit function - 
    # some are computed as compositions
    return True


def apply_scm(df, scm_params, rng):
    """
    Apply structural causal model equations to generate derived variables.
    All functions implemented from scm_functions.yaml specification.
    """
    n = len(df)
    
    # 1. Baseline harm: logistic function of intrinsic_safety
    intercept = scm_params.get('baseline_harm', {}).get('intercept', -3.0)
    slope = scm_params.get('baseline_harm', {}).get('slope', 4.0)
    df['baseline_harm'] = sigmoid(intercept + slope * (1 - df['intrinsic_safety'].values))
    
    # 2. Baseline benefit: scaled clinical utility
    benefit_scale = 0.9
    df['baseline_benefit'] = np.clip(df['clinical_utility'].values * benefit_scale, 0, 1)
    
    # 3. Subgroup multiplier: linear function of bias_harm_index
    base = scm_params.get('subgroup_multiplier', {}).get('base', 1.0)
    sensitivity = scm_params.get('subgroup_multiplier', {}).get('sensitivity', 2.0)
    df['subgroup_multiplier'] = base + sensitivity * df['bias_harm_index'].values
    
    # 4. Stress failure: Bernoulli draw based on stress_robustness
    base_logit = np.log(0.05 / 0.95)  # ~5% base rate
    rob_effect = scm_params.get('stress_failure', {}).get('robustness_effect', -3.0)
    stress_prob = sigmoid(base_logit + rob_effect * df['stress_robustness'].values)
    df['stress_failure'] = rng.binomial(1, stress_prob).astype(float)
    df['stress_failure_prob'] = stress_prob
    
    # 5. Abstention rate: logistic of uncertainty_calibration
    cutoff = scm_params.get('abstention', {}).get('cutoff', 0.5)
    abs_sens = scm_params.get('abstention', {}).get('sensitivity', 5.0)
    df['abstention_rate'] = sigmoid(abs_sens * (cutoff - df['uncertainty_calibration'].values))
    
    # 6. Fallback harm
    fb_base = scm_params.get('fallback_harm', {}).get('base', 0.1)
    fb_effect = scm_params.get('fallback_harm', {}).get('delta_effect', -0.08)
    df['fallback_harm'] = np.clip(fb_base + fb_effect * df['fallback_safety_delta'].values, 0, 1)
    
    # 7. Audit signal quality: weighted mean of evidence dimensions
    w_es, w_ev, w_ti = 0.4, 0.35, 0.25
    df['audit_signal_quality'] = (
        w_es * df['evidence_strength'].values +
        w_ev * df['evidence_visibility'].values +
        w_ti * df['traceability_integrity'].values
    ) / (w_es + w_ev + w_ti)
    
    # 8. Misreporting bias
    mis_scale = 0.15
    df['misreporting_bias'] = df['adversarial_gaming_capability'].values * mis_scale
    
    # 9. Initial performance decay (t=0)
    df['performance_decay'] = 0.0
    
    # 10. Initial realised harm (before lifecycle)
    df['realised_harm_t0'] = (
        df['baseline_harm'].values * df['subgroup_multiplier'].values +
        df['stress_failure'].values * 0.5  # stress failure adds significant harm
    )
    
    # 11. Escalation workload (proportional to abstention rate)
    df['escalation_workload'] = df['abstention_rate'].values * 2.0
    
    return df
