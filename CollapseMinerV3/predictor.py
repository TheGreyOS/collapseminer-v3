"""
Fold predictor for CollapseMiner v3
Ranks fold entropy, decides if fold should be skipped.
"""
from config import ENTROPY_THRESHOLD


def should_fold_be_mined(entropy_score: float) -> bool:
    """
    Decide whether to mine this fold based on entropy score.
    """
    return entropy_score >= ENTROPY_THRESHOLD
