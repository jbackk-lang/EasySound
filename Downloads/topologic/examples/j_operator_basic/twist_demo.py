from topologic.twist import twist

def main():
    # Prosty sygnał: rośnie, potem spada
    values = [1.0, 1.5, 2.0, 1.8, 1.2, 0.7]
    threshold = 0.0

    print("=== TWIST DEMO ===")
    for i in range(1, len(values)):
        prev = values[i - 1]
        curr = values[i]
        t = twist(prev, curr, threshold=threshold)
        print(f"prev={prev:.2f}, curr={curr:.2f} -> twist={t}")

if __name__ == "__main__":
    main()
