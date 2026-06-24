from topologic.twist import twist
from topologic.defect import defect
from topologic.resonance import resonance
from topologic.j_operator import J

def main():
    Jop = J(twist, defect, resonance)

    # Dwa sygnały: A i B
    prev_a, curr_a = 1.0, 0.6   # A: lekki spadek
    prev_b, curr_b = 0.9, 1.4   # B: wzrost

    result = Jop(prev_a, curr_a, prev_b, curr_b)

    print("=== J-POINT DEMO ===")
    print(f"prev_a={prev_a}, curr_a={curr_a}")
    print(f"prev_b={prev_b}, curr_b={curr_b}")
    print("result:", result)

if __name__ == "__main__":
    main()
