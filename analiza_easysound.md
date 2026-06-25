import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(10,4))
plt.title("Porównanie widma: oryginał vs ultra_soft")
plt.plot(freqs, orig_spectrum, label="oryginał")
plt.plot(freqs, ultra_spectrum, label="ultra_soft")
plt.xlim(0, 8000)
plt.legend()
plt.grid(True)
