"""Observation Model: simulate audit signals with noise, artefacts, and gaming."""
import numpy as np


def apply_observation_model(df, obs_config, evidence_regime='mixed', 
                            auditability_noise=0.05, rng=None):
    """
    Generate observed audit signals from true latent traits.
    Three layers: measurement error, artefact visibility, misreporting.
    """
    if rng is None:
        rng = np.random.RandomState(0)
    
    n = len(df)
    base_noise = obs_config.get('measurement_noise_sd', 0.05)
    artefact_reduction = obs_config.get('artefact_noise_reduction', 0.6)
    mis_scale = obs_config.get('misreporting_scale', 0.15)
    
    # Evidence regime affects artefact availability
    regime_factors = {
        'artefact-heavy': 0.8,
        'mixed': 0.5,
        'self-report-heavy': 0.2
    }
    artefact_factor = regime_factors.get(evidence_regime, 0.5)
    
    # Observable trait names and their true values
    observed_traits = [
        'intrinsic_safety', 'clinical_utility', 'uncertainty_calibration',
        'bias_harm_index', 'evidence_strength', 'evidence_visibility',
        'traceability_integrity', 'stress_robustness', 'fallback_safety_delta'
    ]
    
    for trait in observed_traits:
        if trait not in df.columns:
            continue
            
        true_vals = df[trait].values
        
        # Layer 1: Measurement noise (reduced by artefact availability)
        effective_noise = base_noise + auditability_noise
        # Artefact-backed evidence has lower noise
        noise_reduction = artefact_factor * artefact_reduction
        effective_noise *= (1 - noise_reduction)
        noise = rng.normal(0, effective_noise, n)
        
        # Layer 2: Artefact visibility effect (reduces variance)
        # Already factored into noise reduction above
        
        # Layer 3: Misreporting bias (gaming)
        gaming = df['adversarial_gaming_capability'].values * mis_scale
        # Gaming inflates positive-seeming traits, deflates negative ones
        if trait in ['intrinsic_safety', 'clinical_utility', 'evidence_strength',
                     'evidence_visibility', 'traceability_integrity', 'stress_robustness',
                     'fallback_safety_delta']:
            bias = gaming  # inflate positive traits
        elif trait == 'bias_harm_index':
            bias = -gaming  # deflate negative traits (hide bias)
        else:
            bias = gaming * 0.5
        
        observed = np.clip(true_vals + noise + bias, 0, 1)
        df[f'observed_{trait}'] = observed
    
    # Composite observed signal quality
    df['observed_signal_quality'] = (
        0.4 * df.get('observed_evidence_strength', df.get('evidence_strength', 0)).values +
        0.35 * df.get('observed_evidence_visibility', df.get('evidence_visibility', 0)).values +
        0.25 * df.get('observed_traceability_integrity', df.get('traceability_integrity', 0)).values
    )
    
    return df
