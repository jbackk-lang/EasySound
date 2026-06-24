import numpy as np

class J:
    """
    Operator J: punkt skrętu między dwoma sygnałami.
    Łączy:
    - skręt (twist),
    - defekt (defect),
    - rezonans (resonance)
    w jedną decyzję topologiczną.
    """

    def __init__(self, twist_fn, defect_fn, resonance_fn):
        self.twist = twist_fn
        self.defect = defect_fn
        self.resonance = resonance_fn

    def __call__(self, prev_a, curr_a, prev_b, curr_b):
        """
        Zwraca strukturę opisującą:
        - czy nastąpił skręt,
        - czy wystąpił defekt,
        - czy jest rezonans,
        - oraz punkt J (0–1).
        """

        twist_a = self.twist(prev_a, curr_a)
        twist_b = self.twist(prev_b, curr_b)

        defect_a = self.defect(prev_a, curr_a)
        defect_b = self.defect(prev_b, curr_b)

        resonance = self.resonance([prev_a, curr_a, prev_b, curr_b])

        # Punkt J = średnia ważona trzech operatorów
        J_point = np.mean([
            float(twist_a or twist_b),
            float(defect_a or defect_b),
            float(resonance)
        ])

        return {
            "twist": twist_a or twist_b,
            "defect": defect_a or defect_b,
            "resonance": resonance,
            "J": float(J_point)
        }
