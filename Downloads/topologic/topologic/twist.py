def twist(prev, curr, threshold=0.0):
    """
    Operator skrętu: zmiana kierunku sygnału.
    Zwraca True jeśli nastąpił skręt.
    """
    return (curr - prev) * (prev - threshold) < 0
