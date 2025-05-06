"""
Utility functions for CollapseMiner v3
"""
import hashlib
import struct

def blake2b_hash(header: bytes, nonce: int) -> bytes:
    """
    Compute blake2b hash of header + nonce (nonce as uint32_le)
    """
    nonce_bytes = struct.pack('<I', nonce)
    data = header + nonce_bytes
    return hashlib.blake2b(data, digest_size=32).digest()


def hex_to_int(hex_str: str) -> int:
    return int(hex_str, 16)
