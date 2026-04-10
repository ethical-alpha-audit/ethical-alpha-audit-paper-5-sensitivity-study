"""Validation tests: must pass before paper mode."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.helpers import load_yaml
from src.generators.system_generator import generate_systems, classify_systems
from src.scm.causal_model import apply_scm
from src.generators.observation_model import apply_observation_model
from src.validation.validation_suite import ValidationSuite


def run_validation_tests():
    """Run full validation suite."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parameters.yaml')
    config = load_yaml(config_path)
    
    rng = np.random.RandomState(42)
    df = generate_systems(config, 5000, seed=42)
    df = classify_systems(df, config, unsafe_base_rate=0.20)
    df = apply_scm(df, config.get('scm', {}), rng)
    df = apply_observation_model(df, config.get('observation', {}), rng=rng)
    
    validator = ValidationSuite()
    passed = validator.run_all(df, config.get('scm', {}), config.get('observation', {}))
    report = validator.get_report()
    
    print(f"\nValidation Results: {report['n_passed']}/{report['n_tests']} tests passed")
    for name, result in report['details'].items():
        status = "PASS" if result['passed'] else "FAIL"
        print(f"  [{status}] {name}: {result['reason']}")
    
    if not passed:
        print("\nWARNING: Validation suite FAILED")
        sys.exit(1)
    else:
        print("\nValidation suite PASSED")


if __name__ == '__main__':
    run_validation_tests()
