from topologic.defect import defect

def main():
    # Sygnał z jednym dużym skokiem (defekt)
    values = [1.0, 1.1, 1.2, 1.3, 3.5, 3.6, 3.7]

    print("=== DEFECT DEMO ===")
    for i in range(1, len(values)):
        prev = values[i - 1]
        curr = values[i]
        d = defect(prev, curr, sigma=2.0)
        print(f"prev={prev:.2f}, curr={curr:.2f} -> defect={d}")

if __name__ == "__main__":
    main()
