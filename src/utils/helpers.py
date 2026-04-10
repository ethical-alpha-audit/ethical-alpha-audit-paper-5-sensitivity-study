"""Utility functions for the governance friction simulation."""
import hashlib
import json
import yaml
import numpy as np
import os
from datetime import datetime


def load_yaml(path):
    """Load a YAML configuration file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_json(data, path):
    """Save data as JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def file_hash(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def dict_hash(d):
    """Compute SHA-256 hash of a dictionary."""
    s = json.dumps(d, sort_keys=True, default=str)
    return hashlib.sha256(s.encode()).hexdigest()


def sigmoid(x):
    """Numerically stable sigmoid function."""
    return np.where(x >= 0,
                    1 / (1 + np.exp(-x)),
                    np.exp(x) / (1 + np.exp(x)))


def derive_seed(base_seed, *args):
    """Derive a deterministic seed from base seed and identifiers."""
    h = hashlib.sha256(str(base_seed).encode())
    for a in args:
        h.update(str(a).encode())
    return int(h.hexdigest()[:8], 16)


def get_timestamp():
    """Get current UTC timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def build_correlation_matrix(config):
    """Build full correlation matrix from lower-triangle specification."""
    values = config['correlation_matrix']['values']
    n = len(values)
    mat = np.eye(n)
    for i in range(n):
        for j in range(len(values[i])):
            mat[i, j] = values[i][j]
            mat[j, i] = values[i][j]
    return mat, config['correlation_matrix']['variables']
