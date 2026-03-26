#!/usr/bin/env python
"""Quick start script for PROMETHEUS Trading Server"""
import os
import sys

# Set environment
os.environ['WORKERS'] = '1'

# Run the unified production server
if __name__ == '__main__':
    print("Starting PROMETHEUS Trading Server...")
    exec(open('unified_production_server.py').read())

