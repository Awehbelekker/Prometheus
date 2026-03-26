#!/usr/bin/env python3
"""
🔐 Alpaca API Configuration
IMPORTANT: Set your Alpaca API secret keys here
"""

import os

# SECURITY NOTE:
# Do not hardcode API credentials in source code. Use environment variables or a .env file.
# This script demonstrates how to set them at runtime for local testing ONLY.

PAPER_KEY = os.getenv("ALPACA_PAPER_KEY")
PAPER_SECRET = os.getenv("ALPACA_PAPER_SECRET")
LIVE_KEY = os.getenv("ALPACA_LIVE_KEY")
LIVE_SECRET = os.getenv("ALPACA_LIVE_SECRET")

if not all([PAPER_KEY, PAPER_SECRET]):
	print("Set ALPACA_PAPER_KEY and ALPACA_PAPER_SECRET in your environment before running.")
else:
	os.environ["ALPACA_PAPER_KEY"] = PAPER_KEY
	os.environ["ALPACA_PAPER_SECRET"] = PAPER_SECRET

if LIVE_KEY and LIVE_SECRET:
	os.environ["ALPACA_LIVE_KEY"] = LIVE_KEY
	os.environ["ALPACA_LIVE_SECRET"] = LIVE_SECRET

print("Alpaca API keys configured from environment (secrets not printed)")
