"""
Hash entropy analyzer for CollapseMiner v3
Uses FFT and PCA to analyze entropy of sampled hashes.
"""
import numpy as np
from scipy.fft import fft
from sklearn.decomposition import PCA


def hash_entropy_fft(hashes: list[bytes]) -> float:
    """
    Compute entropy score using FFT on sampled hashes.
    Returns a normalized entropy score (0-1).
    """
    arr = np.array([list(h) for h in hashes], dtype=np.uint8)
    # Flatten and FFT
    spectrum = np.abs(fft(arr, axis=0)).mean(axis=1)
    entropy = np.std(spectrum) / np.mean(spectrum)
    return float(np.clip(entropy, 0, 1))


def hash_entropy_pca(hashes: list[bytes], n_components: int = 4) -> float:
    """
    Compute entropy score using PCA variance ratio.
    """
    arr = np.array([list(h) for h in hashes], dtype=np.uint8)
    pca = PCA(n_components=min(n_components, arr.shape[0]))
    pca.fit(arr)
    score = 1 - sum(pca.explained_variance_ratio_)
    return float(np.clip(score, 0, 1))
