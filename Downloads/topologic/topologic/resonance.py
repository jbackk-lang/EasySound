import numpy as np

def resonance(values):
    """
    Operator rezonansu: wiele sygnałów zmienia się w tym samym kierunku.
    """
    diffs = np.diff(values)
    return np.all(np.sign(diffs) == np.sign(diffs[0]))
