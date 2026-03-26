#!/usr/bin/env python3
"""Simplified DirectML detection script - no torch import"""
try:
    import torch_directml
    device = torch_directml.device()
    print("DIRECTML_OK")
except Exception as e:
    print(f"DIRECTML_FAIL:{e}")
