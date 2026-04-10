"""Preregistration: analysis plan enforcement and hash verification."""
import hashlib
import json
import os
from ..utils.helpers import load_yaml, dict_hash


def load_analysis_plan(path='analysis_plan.yaml'):
    """Load and validate the analysis plan."""
    plan = load_yaml(path)
    return plan


def compute_plan_hash(plan):
    """Compute deterministic hash of the analysis plan."""
    return dict_hash(plan)


def verify_plan_hash(plan, expected_hash):
    """Verify that the plan hash matches expected."""
    actual = compute_plan_hash(plan)
    return actual == expected_hash, actual


def enforce_paper_mode(plan, config):
    """
    Enforce paper mode constraints.
    Returns True if all checks pass.
    """
    if plan is None:
        raise ValueError("Paper mode requires analysis_plan.yaml")
    
    # Check required fields
    required_fields = ['plan_id', 'hypotheses', 'primary_estimands', 'scenarios']
    ap = plan.get('analysis_plan', plan)
    for field in required_fields:
        if field not in ap:
            raise ValueError(f"Analysis plan missing required field: {field}")
    
    return True
