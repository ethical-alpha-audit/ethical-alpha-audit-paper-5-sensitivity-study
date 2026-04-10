# Methods Note

## Simulation Framework

This repository implements a Monte Carlo simulation framework for evaluating governance friction in medical AI deployment. The framework models the complete governance pipeline: from latent AI system properties, through noisy audit observation, to governance decisions and lifecycle outcomes.

## Structural Causal Model (SCM)

A directed acyclic graph with 28 nodes and 19 edges encodes causal relationships among latent traits, intermediate variables, and outcome nodes. All structural equations are instantiated from a versioned function library (`scm_functions.yaml` v1.0).

Key functional forms:
- **Baseline harm:** logistic function of intrinsic safety (intercept = −3.0, slope = 4.0)
- **Subgroup harm:** linear in bias_harm_index (base = 1.0, sensitivity = 2.0)
- **Stress failure:** Bernoulli-logistic (base rate ~5%, robustness effect = −3.0)
- **Performance decay:** multiplicative drift model (rate = 0.02, monitoring reduction = 0.5)

## System Generation

Synthetic AI systems are generated using a Gaussian copula with Beta marginal distributions for bounded traits and lognormal for deployment volume. A 10×10 correlation matrix encodes associations justified by the SCM structure. Each evaluation generates 10,000 systems.

## Observation Model

Observed audit signals are derived from true latent traits through three layers:
1. Measurement noise (base SD = 0.05, reduced by artefact availability)
2. Evidence regime effects (artefact-heavy, mixed, self-report-heavy)
3. Adversarial misreporting bias proportional to gaming capability (scale = 0.15)

## Governance Policy Engine

The Tier-1 governance model implements five non-compensable gates: safety, evidence quality, bias (inverted), calibration, and traceability. A system is approved only if all five observed gate scores meet their respective thresholds. A compensatory (composite scoring) comparator is also implemented.

## Multi-Objective Optimisation

NSGA-II explores the five-dimensional threshold space over 30 generations with population 60, optimising four objectives simultaneously: maximise detection, maximise throughput, minimise false-negative harm, minimise friction.

## Sobol Sensitivity Analysis

Variance-based global sensitivity analysis with 7 parameters (5 gate thresholds + auditability noise + unsafe base rate) using 64 base samples and quasi-random Saltelli sampling.

## Decision Curve Analysis

Net benefit computed across a range of harm–benefit preference thresholds for all governance policies, following the Vickers & Elkin (2006) framework.

## Extreme Risk Modelling

Tail risks modelled via the Generalized Pareto Distribution (tail index = 0.3, threshold at 95th percentile).
