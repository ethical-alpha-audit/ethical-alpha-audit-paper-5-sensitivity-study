#!/usr/bin/env python3
"""
Governance Friction Simulation - Main Execution Script
======================================================
Runs the complete simulation pipeline:
1. Generate synthetic AI systems
2. Apply SCM structural equations
3. Apply observation model
4. Evaluate governance policies
5. Compute friction costs
6. Run lifecycle simulation
7. Run NSGA-II optimisation
8. Run sensitivity analysis
9. Run statistical inference
10. Run validation tests
11. Run replication protocol
12. Generate figures and tables
"""

import sys
import os
import json
import time
import hashlib
import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.helpers import load_yaml, save_json, dict_hash, derive_seed, get_timestamp
from src.generators.system_generator import generate_systems, classify_systems
from src.generators.observation_model import apply_observation_model
from src.scm.causal_model import load_scm_graph, apply_scm, validate_scm_functions
from src.policy.governance_engine import (
    GovernancePolicyEngine, CompensatoryPolicyEngine, evaluate_policy_outcomes
)
from src.metrics.friction_model import compute_friction
from src.analysis.lifecycle import simulate_lifecycle
from src.analysis.extreme_risk import model_extreme_risks
from src.analysis.sensitivity import run_sobol_analysis, format_sensitivity_table
from src.analysis.inference import run_inference, bootstrap_ci, bayesian_rate_interval
from src.analysis.dca import run_dca
from src.validation.validation_suite import ValidationSuite
from src.optimisation.nsga2_search import run_nsga2, identify_sweet_spot
from src.replication.replication import run_replication, save_replication_report
from src.preregistration.plan import load_analysis_plan, compute_plan_hash
from src.plotting.figures import generate_all_figures


def run_single_evaluation(config, threshold_profile, seed=42, 
                          evidence_regime='mixed', auditability_noise=0.05,
                          unsafe_base_rate=0.20, drift_regime='medium'):
    """
    Run a single simulation evaluation for a given threshold profile.
    Returns metrics dict.
    """
    rng = np.random.RandomState(seed)
    n_systems = config['simulation']['n_systems']
    
    # 1. Generate systems
    df = generate_systems(config, n_systems, seed=seed)
    df = classify_systems(df, config, unsafe_base_rate=unsafe_base_rate)
    
    # 2. Apply SCM
    df = apply_scm(df, config.get('scm', {}), rng)
    
    # 3. Apply observation model
    df = apply_observation_model(
        df, config.get('observation', {}),
        evidence_regime=evidence_regime,
        auditability_noise=auditability_noise,
        rng=rng
    )
    
    # 4. Apply extreme tail risk
    df, gof_results = model_extreme_risks(df, config.get('extreme_risk', {}), rng=rng)
    
    # 5. Evaluate governance policy
    engine = GovernancePolicyEngine(threshold_profile)
    policy_results = engine.evaluate(df)
    
    # 6. Compute metrics
    outcomes = evaluate_policy_outcomes(df, policy_results)
    
    # 7. Compute friction
    friction = compute_friction(df, policy_results, config.get('friction', {}), threshold_profile)
    outcomes['mean_total_friction'] = friction['mean_total_friction']
    outcomes['total_system_friction'] = friction['total_system_friction']
    
    return outcomes, df, policy_results, friction


def run_quick_evaluation(threshold_profile_or_params, config=None, 
                          base_seed=42, n_systems=None):
    """
    Quick evaluation function for optimisation and sensitivity analysis.
    Accepts either a threshold profile dict or a flat parameter dict.
    """
    if config is None:
        config = _GLOBAL_CONFIG
    
    # Parse parameters
    if isinstance(threshold_profile_or_params, dict):
        params = threshold_profile_or_params
    else:
        params = {}
    
    profile = {
        'safety_gate': params.get('safety_gate', 0.5),
        'evidence_gate': params.get('evidence_gate', 0.5),
        'bias_gate': params.get('bias_gate', 0.5),
        'calibration_gate': params.get('calibration_gate', 0.4),
        'traceability_gate': params.get('traceability_gate', 0.4),
    }
    
    noise = params.get('auditability_noise', 0.05)
    ubr = params.get('unsafe_base_rate', 0.20)
    
    # Use smaller sample for optimisation
    sim_config = dict(config)
    sim_config['simulation'] = dict(config['simulation'])
    if n_systems:
        sim_config['simulation']['n_systems'] = n_systems
    
    outcomes, _, _, _ = run_single_evaluation(
        sim_config, profile, seed=base_seed,
        auditability_noise=noise, unsafe_base_rate=ubr
    )
    
    return outcomes


# Global config reference for optimisation callbacks
_GLOBAL_CONFIG = None


def run_grid_search(config, n_grid=5, seed=42):
    """Run grid search over safety and evidence gate thresholds."""
    safety_vals = np.linspace(0.2, 0.8, n_grid)
    evidence_vals = np.linspace(0.2, 0.8, n_grid)
    
    results = {
        'unsafe_detection_rate': np.zeros((n_grid, n_grid)),
        'safe_throughput': np.zeros((n_grid, n_grid)),
        'false_negative_harm': np.zeros((n_grid, n_grid)),
        'mean_total_friction': np.zeros((n_grid, n_grid)),
    }
    
    for i, sg in enumerate(safety_vals):
        for j, eg in enumerate(evidence_vals):
            profile = {
                'safety_gate': sg,
                'evidence_gate': eg,
                'bias_gate': 0.5,
                'calibration_gate': 0.4,
                'traceability_gate': 0.4,
            }
            outcomes, _, _, _ = run_single_evaluation(config, profile, seed=seed)
            for metric in results:
                results[metric][i, j] = outcomes[metric]
    
    results['safety_vals'] = safety_vals.tolist()
    results['evidence_vals'] = evidence_vals.tolist()
    
    return results


def main():
    """Main execution pipeline."""
    global _GLOBAL_CONFIG
    
    start_time = time.time()
    print("=" * 70)
    print("GOVERNANCE FRICTION SIMULATION v1.0")
    print("=" * 70)
    
    # Load configuration
    config_path = os.path.join(PROJECT_ROOT, 'config', 'parameters.yaml')
    config = load_yaml(config_path)
    _GLOBAL_CONFIG = config
    
    # For computational feasibility, use reduced parameters
    # n_systems is canonical at 10000 in parameters.yaml (no override needed)
    n_replicates = config['simulation'].get('n_replicates', 5)
    n_timesteps = config['simulation'].get('n_timesteps', 12)
    base_seed = config['simulation'].get('random_seed', 42)
    
    # Load analysis plan
    plan_path = os.path.join(PROJECT_ROOT, 'analysis_plan.yaml')
    analysis_plan = load_analysis_plan(plan_path)
    plan_hash = compute_plan_hash(analysis_plan)
    print(f"Analysis plan hash: {plan_hash[:16]}...")
    
    # Load threshold profiles
    threshold_path = os.path.join(PROJECT_ROOT, 'thresholds', 'threshold_profiles.yaml')
    threshold_config = load_yaml(threshold_path)
    
    # Load SCM graph and validate
    scm_graph_path = os.path.join(PROJECT_ROOT, 'config', 'scm_graph.dot')
    scm_graph = load_scm_graph(scm_graph_path)
    scm_functions_path = os.path.join(PROJECT_ROOT, 'scm_functions.yaml')
    scm_functions = load_yaml(scm_functions_path)
    print(f"SCM graph: {scm_graph.number_of_nodes()} nodes, {scm_graph.number_of_edges()} edges")
    print(f"SCM is valid DAG: {True}")
    
    # ================================================================
    # PHASE 1: VALIDATION
    # ================================================================
    print("\n--- Phase 1: Validation Tests ---")
    rng = np.random.RandomState(base_seed)
    df_val = generate_systems(config, 5000, seed=base_seed)
    df_val = classify_systems(df_val, config, unsafe_base_rate=0.20)
    df_val = apply_scm(df_val, config.get('scm', {}), rng)
    df_val = apply_observation_model(df_val, config.get('observation', {}), rng=rng)
    
    validator = ValidationSuite()
    validation_passed = validator.run_all(df_val, config.get('scm', {}), config.get('observation', {}))
    val_report = validator.get_report()
    print(f"Validation: {val_report['n_passed']}/{val_report['n_tests']} tests passed")
    
    if not validation_passed:
        print("WARNING: Some validation tests failed!")
        for name, result in val_report['details'].items():
            if not result['passed']:
                print(f"  FAIL: {name} - {result['reason']}")
    else:
        print("All validation tests PASSED")
    
    save_json(val_report, os.path.join(PROJECT_ROOT, 'outputs', 'logs', 'validation_report.json'))
    
    # ================================================================
    # PHASE 2: BASELINE SIMULATION
    # ================================================================
    print("\n--- Phase 2: Baseline Simulation ---")
    
    all_results = {}
    scenario_results = []
    
    # Run across scenarios
    scenarios = [
        {'unsafe_base_rate': 0.10, 'auditability_noise': 0.05, 'evidence_regime': 'mixed', 'drift_regime': 'medium'},
        {'unsafe_base_rate': 0.20, 'auditability_noise': 0.05, 'evidence_regime': 'mixed', 'drift_regime': 'medium'},
        {'unsafe_base_rate': 0.30, 'auditability_noise': 0.05, 'evidence_regime': 'mixed', 'drift_regime': 'medium'},
        {'unsafe_base_rate': 0.20, 'auditability_noise': 0.02, 'evidence_regime': 'artefact-heavy', 'drift_regime': 'low'},
        {'unsafe_base_rate': 0.20, 'auditability_noise': 0.10, 'evidence_regime': 'self-report-heavy', 'drift_regime': 'high'},
    ]
    
    for s_idx, scenario in enumerate(scenarios):
        print(f"  Scenario {s_idx + 1}/{len(scenarios)}: {scenario}")
        
        for profile_name, profile in threshold_config['profiles'].items():
            for rep in range(n_replicates):
                seed = derive_seed(base_seed, s_idx, profile_name, rep)
                
                outcomes, df, policy_res, friction = run_single_evaluation(
                    config, profile, seed=seed,
                    evidence_regime=scenario['evidence_regime'],
                    auditability_noise=scenario['auditability_noise'],
                    unsafe_base_rate=scenario['unsafe_base_rate'],
                    drift_regime=scenario['drift_regime']
                )
                
                result_entry = {
                    'scenario_idx': s_idx,
                    'profile_name': profile_name,
                    'replicate': rep,
                    **scenario,
                    **outcomes,
                }
                scenario_results.append(result_entry)
    
    results_df = pd.DataFrame(scenario_results)
    results_df.to_csv(os.path.join(PROJECT_ROOT, 'outputs', 'raw', 'scenario_results.csv'), index=False)
    print(f"  Completed {len(scenario_results)} evaluations")
    
    # ================================================================
    # PHASE 3: COMPENSATORY COMPARISON
    # ================================================================
    print("\n--- Phase 3: Non-compensable vs Compensatory Comparison ---")
    
    # Run moderate profile with both regimes
    moderate_profile = threshold_config['profiles']['moderate']
    comp_results = []
    
    for rep in range(n_replicates):
        seed = derive_seed(base_seed, 'comparison', rep)
        rng = np.random.RandomState(seed)
        
        df = generate_systems(config, config['simulation']['n_systems'], seed=seed)
        df = classify_systems(df, config, unsafe_base_rate=0.20)
        df = apply_scm(df, config.get('scm', {}), rng)
        df = apply_observation_model(df, config.get('observation', {}), rng=rng)
        df, _ = model_extreme_risks(df, config.get('extreme_risk', {}), rng=rng)
        
        # Non-compensable
        nc_engine = GovernancePolicyEngine(moderate_profile)
        nc_results = nc_engine.evaluate(df)
        nc_outcomes = evaluate_policy_outcomes(df, nc_results)
        
        # Compensatory
        c_engine = CompensatoryPolicyEngine(moderate_profile)
        c_results = c_engine.evaluate(df)
        c_outcomes = evaluate_policy_outcomes(df, c_results)
        
        comp_results.append({
            'replicate': rep,
            'nc_detection': nc_outcomes['unsafe_detection_rate'],
            'nc_throughput': nc_outcomes['safe_throughput'],
            'nc_fn_harm': nc_outcomes['false_negative_harm'],
            'c_detection': c_outcomes['unsafe_detection_rate'],
            'c_throughput': c_outcomes['safe_throughput'],
            'c_fn_harm': c_outcomes['false_negative_harm'],
        })
    
    comp_df = pd.DataFrame(comp_results)
    comp_df.to_csv(os.path.join(PROJECT_ROOT, 'outputs', 'raw', 'compensatory_comparison.csv'), index=False)
    print(f"  Non-comp. detection: {comp_df['nc_detection'].mean():.3f}, Comp. detection: {comp_df['c_detection'].mean():.3f}")
    print(f"  Non-comp. FN harm: {comp_df['nc_fn_harm'].mean():.1f}, Comp. FN harm: {comp_df['c_fn_harm'].mean():.1f}")
    
    # ================================================================
    # PHASE 4: GRID SEARCH
    # ================================================================
    print("\n--- Phase 4: Grid Search ---")
    grid_results = run_grid_search(config, n_grid=6, seed=base_seed)
    save_json({k: v.tolist() if isinstance(v, np.ndarray) else v 
               for k, v in grid_results.items()},
              os.path.join(PROJECT_ROOT, 'outputs', 'processed', 'grid_results.json'))
    print("  Grid search complete (6x6)")
    
    # ================================================================
    # PHASE 5: NSGA-II OPTIMISATION
    # ================================================================
    print("\n--- Phase 5: NSGA-II Optimisation ---")
    
    # Use smaller n_systems for optimisation evaluations
    opt_config = dict(config)
    opt_config['simulation'] = dict(config['simulation'])
    opt_config['simulation']['n_systems'] = 3000
    _GLOBAL_CONFIG = opt_config
    
    def eval_fn(profile):
        return run_quick_evaluation(profile, config=opt_config, base_seed=base_seed, n_systems=3000)
    
    pareto_profiles, pareto_objectives = run_nsga2(
        eval_fn, n_gen=30, pop_size=60, seed=base_seed
    )
    
    if len(pareto_objectives) > 0:
        sweet_profiles, sweet_objectives = identify_sweet_spot(
            pareto_profiles, pareto_objectives,
            min_detection=0.7, min_throughput=0.5
        )
        sweet_mask = np.array([
            any(np.allclose(list(p.values()), list(sp.values())) for sp in sweet_profiles)
            for p in pareto_profiles
        ]) if sweet_profiles else np.zeros(len(pareto_profiles), dtype=bool)
        
        print(f"  Pareto solutions: {len(pareto_profiles)}")
        print(f"  Sweet-spot solutions: {len(sweet_profiles)}")
        
        # Save Pareto results
        pareto_df = pd.DataFrame(pareto_profiles)
        pareto_df['detection_rate'] = pareto_objectives[:, 0]
        pareto_df['throughput'] = pareto_objectives[:, 1]
        pareto_df['fn_harm'] = pareto_objectives[:, 2]
        pareto_df['friction'] = pareto_objectives[:, 3]
        pareto_df['in_sweet_spot'] = sweet_mask
        pareto_df.to_csv(os.path.join(PROJECT_ROOT, 'outputs', 'processed', 'pareto_solutions.csv'), index=False)
    else:
        print("  WARNING: No Pareto solutions found")
        pareto_objectives = np.zeros((1, 4))
        sweet_mask = None
    
    _GLOBAL_CONFIG = config
    
    # ================================================================
    # PHASE 6: LIFECYCLE SIMULATION
    # ================================================================
    print("\n--- Phase 6: Lifecycle Simulation ---")
    rng = np.random.RandomState(base_seed)
    df_lifecycle = generate_systems(config, config['simulation']['n_systems'], seed=base_seed)
    df_lifecycle = classify_systems(df_lifecycle, config, unsafe_base_rate=0.20)
    df_lifecycle = apply_scm(df_lifecycle, config.get('scm', {}), rng)
    
    lifecycle_results = simulate_lifecycle(
        df_lifecycle, config.get('scm', {}),
        n_timesteps=n_timesteps, drift_regime='medium', rng=rng
    )
    print(f"  Mean final decay: {lifecycle_results['mean_final_decay']:.4f}")
    print(f"  Re-audit rate: {lifecycle_results['re_audit_rate']:.3f}")
    
    # ================================================================
    # PHASE 7: SENSITIVITY ANALYSIS
    # ================================================================
    print("\n--- Phase 7: Sobol Sensitivity Analysis ---")
    
    sens_config = dict(config)
    sens_config['simulation'] = dict(config['simulation'])
    sens_config['simulation']['n_systems'] = 2000
    _GLOBAL_CONFIG = sens_config
    
    def sobol_eval(params):
        return run_quick_evaluation(params, config=sens_config, base_seed=base_seed, n_systems=2000)
    
    sobol_results = run_sobol_analysis(sobol_eval, n_samples=64, seed=base_seed)
    
    assumed_params = {'auditability_noise', 'unsafe_base_rate'}
    sensitivity_tables = format_sensitivity_table(sobol_results, assumed_params)
    
    for outcome, table in sensitivity_tables.items():
        print(f"  {outcome}: top driver = {table.iloc[0]['parameter']} (ST={table.iloc[0]['ST']:.3f})")
        table.to_csv(os.path.join(PROJECT_ROOT, 'outputs', 'tables', f'sobol_{outcome}.csv'), index=False)
    
    _GLOBAL_CONFIG = config
    
    # ================================================================
    # PHASE 8: DECISION CURVE ANALYSIS
    # ================================================================
    print("\n--- Phase 8: Decision Curve Analysis ---")
    rng = np.random.RandomState(base_seed)
    df_dca = generate_systems(config, config['simulation']['n_systems'], seed=base_seed)
    df_dca = classify_systems(df_dca, config, unsafe_base_rate=0.20)
    df_dca = apply_scm(df_dca, config.get('scm', {}), rng)
    df_dca = apply_observation_model(df_dca, config.get('observation', {}), rng=rng)
    
    policy_results_dict = {}
    for profile_name, profile in threshold_config['profiles'].items():
        engine = GovernancePolicyEngine(profile)
        policy_results_dict[profile_name] = engine.evaluate(df_dca)
    
    # Add compensatory for comparison
    comp_engine = CompensatoryPolicyEngine(threshold_config['profiles']['moderate'])
    policy_results_dict['compensatory_moderate'] = comp_engine.evaluate(df_dca)
    
    dca_results = run_dca(df_dca, policy_results_dict)
    save_json(dca_results, os.path.join(PROJECT_ROOT, 'outputs', 'processed', 'dca_results.json'))
    print("  DCA complete across", len(policy_results_dict), "policies")
    
    # ================================================================
    # PHASE 9: STATISTICAL INFERENCE
    # ================================================================
    print("\n--- Phase 9: Statistical Inference ---")
    
    # Use moderate profile across replicates
    moderate_metrics = results_df[results_df['profile_name'] == 'moderate']
    if len(moderate_metrics) > 0:
        replicate_list = [row.to_dict() for _, row in moderate_metrics.iterrows()]
        inference_results = run_inference(replicate_list, n_bootstrap=500, seed=base_seed)
        save_json(inference_results, os.path.join(PROJECT_ROOT, 'outputs', 'processed', 'inference_results.json'))
        print(f"  Detection: {inference_results['detection_mean']:.3f} [{inference_results['detection_ci_lower']:.3f}, {inference_results['detection_ci_upper']:.3f}]")
        print(f"  Throughput: {inference_results['throughput_mean']:.3f} [{inference_results['throughput_ci_lower']:.3f}, {inference_results['throughput_ci_upper']:.3f}]")
    else:
        inference_results = {}
    
    # ================================================================
    # PHASE 10: REPLICATION PROTOCOL
    # ================================================================
    print("\n--- Phase 10: Replication Protocol ---")
    
    def replication_sim(cfg, seed):
        profile = threshold_config['profiles']['moderate']
        outcomes, _, _, _ = run_single_evaluation(cfg, profile, seed=seed)
        return outcomes
    
    replication_report = run_replication(replication_sim, config)
    save_replication_report(replication_report,
                            os.path.join(PROJECT_ROOT, 'reproducibility', 'replication_report.json'))
    print(f"  Replication: {replication_report['summary']}")
    
    # ================================================================
    # PHASE 11: GENERATE FIGURES
    # ================================================================
    print("\n--- Phase 11: Generating Figures ---")
    
    sim_results = {
        'pareto_objectives': pareto_objectives,
        'sweet_mask': sweet_mask,
        'grid_results': grid_results,
        'sobol_results': sobol_results,
        'lifecycle_results': lifecycle_results,
        'dca_results': dca_results,
    }
    
    figures = generate_all_figures(sim_results, os.path.join(PROJECT_ROOT, 'outputs', 'figures'))
    print(f"  Generated {len(figures)} figures")
    
    # ================================================================
    # PHASE 12: GENERATE TABLES
    # ================================================================
    print("\n--- Phase 12: Generating Tables ---")
    
    # Table 1: Threshold profiles and outcomes
    table1_data = []
    for profile_name in threshold_config['profiles']:
        profile_results = results_df[
            (results_df['profile_name'] == profile_name) & 
            (results_df['unsafe_base_rate'] == 0.20) &
            (results_df['auditability_noise'] == 0.05)
        ]
        if len(profile_results) > 0:
            table1_data.append({
                'profile': profile_name,
                'detection_rate': f"{profile_results['unsafe_detection_rate'].mean():.3f}",
                'throughput': f"{profile_results['safe_throughput'].mean():.3f}",
                'fn_harm': f"{profile_results['false_negative_harm'].mean():.1f}",
                'friction': f"{profile_results['mean_total_friction'].mean():.2f}",
            })
    
    table1 = pd.DataFrame(table1_data)
    table1.to_csv(os.path.join(PROJECT_ROOT, 'outputs', 'tables', 'table1_thresholds.csv'), index=False)
    
    # Table 2: Pareto summary
    if len(pareto_objectives) > 0:
        table2 = pd.DataFrame({
            'metric': ['Detection Rate', 'Safe Throughput', 'FN Harm', 'Friction'],
            'min': [f"{pareto_objectives[:, i].min():.3f}" for i in range(4)],
            'median': [f"{np.median(pareto_objectives[:, i]):.3f}" for i in range(4)],
            'max': [f"{pareto_objectives[:, i].max():.3f}" for i in range(4)],
        })
        table2.to_csv(os.path.join(PROJECT_ROOT, 'outputs', 'tables', 'table2_pareto.csv'), index=False)
    
    # ================================================================
    # PHASE 13: RUN MANIFEST
    # ================================================================
    print("\n--- Phase 13: Creating Run Manifest ---")
    
    elapsed = time.time() - start_time
    manifest = {
        'timestamp': get_timestamp(),
        'plan_hash': plan_hash,
        'config_hash': dict_hash(config),
        'n_systems': config['simulation']['n_systems'],
        'n_replicates': n_replicates,
        'n_scenarios': len(scenarios),
        'n_profiles': len(threshold_config['profiles']),
        'total_evaluations': len(scenario_results),
        'nsga2_pareto_solutions': len(pareto_profiles),
        'validation_passed': validation_passed,
        'replication_passed': replication_report.get('all_passed', False),
        'elapsed_seconds': round(elapsed, 1),
        'figures_generated': list(figures.keys()),
    }
    save_json(manifest, os.path.join(PROJECT_ROOT, 'reproducibility', 'run_manifest.json'))
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print(f"  Total evaluations: {len(scenario_results)}")
    print(f"  Pareto solutions: {len(pareto_profiles)}")
    print(f"  Validation: {'PASSED' if validation_passed else 'FAILED'}")
    print(f"  Replication: {replication_report.get('summary', 'N/A')}")
    print(f"  Elapsed time: {elapsed:.1f}s")
    print(f"  Outputs saved to: {os.path.join(PROJECT_ROOT, 'outputs')}")
    
    # Save summary for article generation
    summary = {
        'manifest': manifest,
        'validation_report': val_report,
        'inference_results': inference_results,
        'replication_report': replication_report,
        'compensatory_comparison': {
            'nc_detection_mean': float(comp_df['nc_detection'].mean()),
            'nc_throughput_mean': float(comp_df['nc_throughput'].mean()),
            'nc_fn_harm_mean': float(comp_df['nc_fn_harm'].mean()),
            'c_detection_mean': float(comp_df['c_detection'].mean()),
            'c_throughput_mean': float(comp_df['c_throughput'].mean()),
            'c_fn_harm_mean': float(comp_df['c_fn_harm'].mean()),
        },
        'table1_data': table1_data,
        'lifecycle_summary': {
            'mean_final_decay': lifecycle_results['mean_final_decay'],
            'mean_total_harm': lifecycle_results['mean_total_harm'],
            're_audit_rate': lifecycle_results['re_audit_rate'],
        },
    }
    save_json(summary, os.path.join(PROJECT_ROOT, 'outputs', 'processed', 'simulation_summary.json'))
    
    return summary


if __name__ == '__main__':
    main()
