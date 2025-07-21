# models/metrics.py
import numpy as np


def precision_at_k(recommended, actual, k=10):
    recs = [pid for pid, _ in recommended[:k]]
    actual_set = set(actual)
    if not recs:
        return 0.0
    hits = sum(1 for r in recs if r in actual_set)
    return hits / min(k, len(recs))


def recall_at_k(recommended, actual, k=10):
    recs = [pid for pid, _ in recommended[:k]]
    actual_set = set(actual)
    if not actual_set:
        return 0.0
    hits = sum(1 for r in recs if r in actual_set)
    return hits / len(actual_set)
