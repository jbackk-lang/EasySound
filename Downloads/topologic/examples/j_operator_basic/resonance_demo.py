from topologic.resonance import resonance

def main():
    # Dwa zestawy wartości:
    # 1) wspólny kierunek (rezonans)
    # 2) mieszany kierunek (brak rezonansu)
    values_resonant = [1.0, 1.2, 1.5, 1.9]
    values_non_resonant = [1.0, 0.8, 1.1, 0.9]

    print("=== RESONANCE DEMO ===")
    r1 = resonance(values_resonant)
    r2 = resonance(values_non_resonant)

    print(f"values_resonant={values_resonant} -> resonance={r1}")
    print(f"values_non_resonant={values_non_resonant} -> resonance={r2}")

if __name__ == "__main__":
    main()
