#!/usr/bin/env python3
"""Wrapper script - full pipeline via run_all.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.run_all import main
if __name__ == '__main__':
    main()
