"""Governance Policy Engine: non-compensable gates, evidence floors, abstention rules."""
import numpy as np
import pandas as pd


class GovernancePolicyEngine:
    """
    Tier-1 governance policy with non-compensable gates.
    Each gate must independently pass; failure in ANY gate blocks deployment.
    """
    
    def __init__(self, threshold_profile):
        """Initialize with a threshold profile dict."""
        self.thresholds = threshold_profile
        self.regime = 'non_compensable'
    
    def evaluate(self, df):
        """
        Evaluate all systems against governance gates.
        Returns DataFrame with gate results and final verdict.
        """
        n = len(df)
        results = pd.DataFrame(index=df.index)
        
        # Gate 1: Safety gate - observed intrinsic safety must exceed threshold
        safety_thresh = self.thresholds.get('safety_gate', 0.5)
        obs_safety = df.get('observed_intrinsic_safety', df['intrinsic_safety']).values
        results['gate_safety'] = (obs_safety >= safety_thresh).astype(int)
        
        # Gate 2: Evidence gate - evidence quality must exceed threshold
        evidence_thresh = self.thresholds.get('evidence_gate', 0.5)
        obs_evidence = df.get('observed_evidence_strength', df['evidence_strength']).values
        results['gate_evidence'] = (obs_evidence >= evidence_thresh).astype(int)
        
        # Gate 3: Bias gate - bias must be below threshold (inverted)
        bias_thresh = self.thresholds.get('bias_gate', 0.5)
        obs_bias = df.get('observed_bias_harm_index', df['bias_harm_index']).values
        results['gate_bias'] = (obs_bias <= bias_thresh).astype(int)
        
        # Gate 4: Calibration gate
        cal_thresh = self.thresholds.get('calibration_gate', 0.4)
        obs_cal = df.get('observed_uncertainty_calibration', df['uncertainty_calibration']).values
        results['gate_calibration'] = (obs_cal >= cal_thresh).astype(int)
        
        # Gate 5: Traceability gate
        trace_thresh = self.thresholds.get('traceability_gate', 0.4)
        obs_trace = df.get('observed_traceability_integrity', df['traceability_integrity']).values
        results['gate_traceability'] = (obs_trace >= trace_thresh).astype(int)
        
        # Non-compensable: ALL gates must pass
        gate_cols = ['gate_safety', 'gate_evidence', 'gate_bias', 
                     'gate_calibration', 'gate_traceability']
        results['all_gates_pass'] = results[gate_cols].prod(axis=1).astype(int)
        
        # Abstention rule: high abstention rate triggers deferral
        abstention = df.get('abstention_rate', pd.Series(np.zeros(n))).values
        results['abstention_triggered'] = (abstention > 0.5).astype(int)
        
        # Fallback safety check
        fallback_safe = df.get('observed_fallback_safety_delta',
                               df.get('fallback_safety_delta', pd.Series(np.ones(n)))).values
        results['fallback_adequate'] = (fallback_safe >= 0.3).astype(int)
        
        # Final verdict: pass only if all gates pass AND no blocking abstention
        results['approved'] = (
            results['all_gates_pass'] & 
            (~results['abstention_triggered'] | results['fallback_adequate'])
        ).astype(int)
        
        # Track which gate caused rejection (for interpretability)
        results['rejection_gate'] = 'none'
        for col in gate_cols:
            mask = (results[col] == 0) & (results['rejection_gate'] == 'none')
            results.loc[mask, 'rejection_gate'] = col.replace('gate_', '')
        
        return results


class CompensatoryPolicyEngine:
    """Alternative compensatory (composite scoring) regime for comparison."""
    
    def __init__(self, threshold_profile):
        self.thresholds = threshold_profile
        self.regime = 'compensatory'
        self.weights = {
            'safety': 0.3,
            'evidence': 0.2,
            'bias': 0.2,
            'calibration': 0.15,
            'traceability': 0.15
        }
    
    def evaluate(self, df):
        """Evaluate using weighted composite score."""
        n = len(df)
        results = pd.DataFrame(index=df.index)
        
        obs_safety = df.get('observed_intrinsic_safety', df['intrinsic_safety']).values
        obs_evidence = df.get('observed_evidence_strength', df['evidence_strength']).values
        obs_bias = 1 - df.get('observed_bias_harm_index', df['bias_harm_index']).values
        obs_cal = df.get('observed_uncertainty_calibration', df['uncertainty_calibration']).values
        obs_trace = df.get('observed_traceability_integrity', df['traceability_integrity']).values
        
        composite = (
            self.weights['safety'] * obs_safety +
            self.weights['evidence'] * obs_evidence +
            self.weights['bias'] * obs_bias +
            self.weights['calibration'] * obs_cal +
            self.weights['traceability'] * obs_trace
        )
        
        results['composite_score'] = composite
        overall_thresh = np.mean(list(self.thresholds.values())[:3])
        results['approved'] = (composite >= overall_thresh).astype(int)
        results['rejection_gate'] = np.where(results['approved'] == 0, 'composite', 'none')
        
        return results


def evaluate_policy_outcomes(df, policy_results):
    """
    Compute outcome metrics: detection rate, throughput, harm, false negatives.
    """
    truly_unsafe = df['truly_unsafe'].values
    approved = policy_results['approved'].values
    
    # True positives: unsafe systems correctly rejected
    tp = np.sum((truly_unsafe == 1) & (approved == 0))
    # False negatives: unsafe systems incorrectly approved
    fn = np.sum((truly_unsafe == 1) & (approved == 1))
    # True negatives: safe systems correctly approved
    tn = np.sum((truly_unsafe == 0) & (approved == 1))
    # False positives: safe systems incorrectly rejected
    fp = np.sum((truly_unsafe == 0) & (approved == 0))
    
    n_unsafe = np.sum(truly_unsafe == 1)
    n_safe = np.sum(truly_unsafe == 0)
    
    unsafe_detection_rate = tp / max(n_unsafe, 1)
    safe_throughput = tn / max(n_safe, 1)
    
    # Harm from false negatives
    harm_vals = df.get('realised_harm_t0', df.get('baseline_harm', pd.Series(np.zeros(len(df))))).values
    false_neg_mask = (truly_unsafe == 1) & (approved == 1)
    false_negative_harm = np.sum(harm_vals[false_neg_mask])
    
    # Average harm of approved systems
    approved_mask = approved == 1
    mean_harm_approved = np.mean(harm_vals[approved_mask]) if np.sum(approved_mask) > 0 else 0
    
    return {
        'unsafe_detection_rate': float(unsafe_detection_rate),
        'safe_throughput': float(safe_throughput),
        'false_negative_harm': float(false_negative_harm),
        'mean_harm_approved': float(mean_harm_approved),
        'n_approved': int(np.sum(approved)),
        'n_rejected': int(np.sum(1 - approved)),
        'tp': int(tp),
        'fn': int(fn),
        'tn': int(tn),
        'fp': int(fp),
        'precision': float(tp / max(tp + fp, 1)),
        'recall': float(unsafe_detection_rate),
    }
