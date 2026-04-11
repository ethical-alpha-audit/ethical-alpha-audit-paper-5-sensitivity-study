"""Unit tests for the governance friction simulation."""
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.helpers import sigmoid, derive_seed, build_correlation_matrix, load_yaml
from src.generators.system_generator import generate_systems, classify_systems
from src.scm.causal_model import load_scm_graph, apply_scm
from src.generators.observation_model import apply_observation_model
from src.policy.governance_engine import GovernancePolicyEngine, evaluate_policy_outcomes
from src.metrics.friction_model import compute_friction


def test_sigmoid():
    """Test sigmoid function."""
    assert abs(sigmoid(0) - 0.5) < 1e-6
    assert sigmoid(10) > 0.99
    assert sigmoid(-10) < 0.01
    # Vectorized
    x = np.array([-10, 0, 10])
    y = sigmoid(x)
    assert len(y) == 3
    print("  PASS: test_sigmoid")


def test_derive_seed():
    """Test deterministic seed derivation."""
    s1 = derive_seed(42, 'a', 1)
    s2 = derive_seed(42, 'a', 1)
    s3 = derive_seed(42, 'b', 1)
    assert s1 == s2, "Same inputs must produce same seed"
    assert s1 != s3, "Different inputs should produce different seeds"
    print("  PASS: test_derive_seed")


def test_system_generator():
    """Test system generation."""
    config = load_yaml(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parameters.yaml'))
    df = generate_systems(config, 1000, seed=42)
    
    assert len(df) == 1000
    assert 'intrinsic_safety' in df.columns
    assert 'clinical_utility' in df.columns
    
    # Check bounds
    for col in ['intrinsic_safety', 'clinical_utility', 'bias_harm_index']:
        assert df[col].min() >= 0, f"{col} has values below 0"
        assert df[col].max() <= 1, f"{col} has values above 1"
    
    print("  PASS: test_system_generator")


def test_classify_systems():
    """Test system classification."""
    config = load_yaml(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parameters.yaml'))
    df = generate_systems(config, 1000, seed=42)
    df = classify_systems(df, config, unsafe_base_rate=0.20)
    
    assert 'truly_unsafe' in df.columns
    unsafe_rate = df['truly_unsafe'].mean()
    assert 0.15 <= unsafe_rate <= 0.25, f"Unsafe rate {unsafe_rate} outside expected range"
    print("  PASS: test_classify_systems")


def test_scm():
    """Test SCM application."""
    config = load_yaml(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parameters.yaml'))
    df = generate_systems(config, 500, seed=42)
    df = classify_systems(df, config)
    rng = np.random.RandomState(42)
    df = apply_scm(df, config.get('scm', {}), rng)
    
    assert 'baseline_harm' in df.columns
    assert 'subgroup_multiplier' in df.columns
    assert 'abstention_rate' in df.columns
    assert df['baseline_harm'].min() >= 0
    assert df['baseline_harm'].max() <= 1
    print("  PASS: test_scm")


def test_observation_model():
    """Test observation model."""
    config = load_yaml(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parameters.yaml'))
    df = generate_systems(config, 500, seed=42)
    df = classify_systems(df, config)
    rng = np.random.RandomState(42)
    df = apply_scm(df, config.get('scm', {}), rng)
    df = apply_observation_model(df, config.get('observation', {}), rng=rng)
    
    assert 'observed_intrinsic_safety' in df.columns
    # Observed values should be noisy versions of true values
    corr = np.corrcoef(df['intrinsic_safety'], df['observed_intrinsic_safety'])[0, 1]
    assert corr > 0.8, f"Observation correlation too low: {corr}"
    print("  PASS: test_observation_model")


def test_policy_engine():
    """Test governance policy engine."""
    config = load_yaml(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parameters.yaml'))
    df = generate_systems(config, 500, seed=42)
    df = classify_systems(df, config)
    rng = np.random.RandomState(42)
    df = apply_scm(df, config.get('scm', {}), rng)
    df = apply_observation_model(df, config.get('observation', {}), rng=rng)
    
    profile = {'safety_gate': 0.5, 'evidence_gate': 0.5, 'bias_gate': 0.5,
               'calibration_gate': 0.4, 'traceability_gate': 0.4}
    engine = GovernancePolicyEngine(profile)
    results = engine.evaluate(df)
    
    assert 'approved' in results.columns
    assert results['approved'].isin([0, 1]).all()
    
    outcomes = evaluate_policy_outcomes(df, results)
    assert 0 <= outcomes['unsafe_detection_rate'] <= 1
    assert 0 <= outcomes['safe_throughput'] <= 1
    print("  PASS: test_policy_engine")


def test_friction():
    """Test friction model."""
    config = load_yaml(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parameters.yaml'))
    df = generate_systems(config, 200, seed=42)
    df = classify_systems(df, config)
    rng = np.random.RandomState(42)
    df = apply_scm(df, config.get('scm', {}), rng)
    df = apply_observation_model(df, config.get('observation', {}), rng=rng)
    
    profile = {'safety_gate': 0.5, 'evidence_gate': 0.5, 'bias_gate': 0.5,
               'calibration_gate': 0.4, 'traceability_gate': 0.4}
    engine = GovernancePolicyEngine(profile)
    policy_results = engine.evaluate(df)
    
    friction = compute_friction(df, policy_results, config.get('friction', {}), profile)
    assert friction['mean_total_friction'] > 0
    print("  PASS: test_friction")


def test_scm_dag():
    """Test SCM graph is valid DAG."""
    graph_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'scm_graph.dot')
    G = load_scm_graph(graph_path)
    import networkx as nx
    assert nx.is_directed_acyclic_graph(G)
    print("  PASS: test_scm_dag")


def run_all_tests():
    """Run all unit tests."""
    print("Running unit tests...")
    test_sigmoid()
    test_derive_seed()
    test_system_generator()
    test_classify_systems()
    test_scm()
    test_observation_model()
    test_policy_engine()
    test_friction()
    test_scm_dag()
    print("\nAll unit tests PASSED!")


if __name__ == '__main__':
    run_all_tests()
