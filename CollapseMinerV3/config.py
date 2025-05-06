"""
Configuration constants for CollapseMiner v3
Switch to real RPC mode by editing RPC_URL and HEADER/TARGET below.
"""

# Fold size (number of nonces per fold)
FOLD_SIZE = 1000000

# Number of hashes to sample for entropy analysis per fold
SAMPLE_SIZE = 256

# Entropy threshold for skipping folds (lower = more selective)
ENTROPY_THRESHOLD = 0.7

# Placeholder block header (bytes-like object, 80 bytes for HNS)
HEADER = bytes.fromhex(
    '00'*80  # Replace with real header when using RPC
)

# Placeholder mining target (as hex string, 32 bytes)
TARGET_HEX = '00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'

# RPC URL (set to real endpoint for live mining)
RPC_URL = 'http://localhost:12037'  # Set to your HSD node endpoint

# Mock mining mode (set True for local testing, False for real mining)
MOCK_MODE = True
