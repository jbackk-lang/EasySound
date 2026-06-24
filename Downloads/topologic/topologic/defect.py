import numpy as np

def defect(prev, curr, sigma=2.0):
    """
    Operator defektu: wykrywa skok/anomalię.
    """
    return abs(curr - prev) > sigma * np.std([prev, curr])
