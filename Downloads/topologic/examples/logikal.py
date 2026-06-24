from topologic.twist import twist
from topologic.defect import defect
from topologic.resonance import resonance
from topologic.j_operator import J


def main():
    print("=== LOGIKAL: Topological Logic Demo ===")

    # Dwa sygnały A i B
    A = [1.0, 1.3, 1.7, 1.2, 0.8, 0.6]
    B = [0.9, 1.0, 1.4, 1.6, 1.1, 0.7]

    Jop = J(twist, defect, resonance)

    for i in range(1, len(A)):
        prev_a, curr_a = A[i - 1], A[i]
        prev_b, curr_b = B[i - 1], B[i]

        t = twist(prev_a, curr_a)
        d = defect(prev_a, curr_a)
        r = resonance([prev_a, curr_a, prev_b, curr_b])
        j = Jop(prev_a, curr_a, prev_b, curr_b)

        print(f"\n--- Step {i} ---")
        print(f"A: {prev_a:.2f} → {curr_a:.2f}")
        print(f"B: {prev_b:.2f} → {curr_b:.2f}")
        print(f"twist={t}, defect={d}, resonance={r}")
        print(f"J-point={j['J']:.3f}")


if __name__ == "__main__":
    main()
