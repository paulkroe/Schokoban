import sys
import os
import numpy as np
import pandas as pd
import csv
import os
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'DejaVu Serif'

# path = "Results/CBC/solution_lengths.csv"
path = "Results/Microban/solution_lengths.csv"
df = pd.read_csv(path, index_col=None)
level_ids = df.iloc[:, 0].values
sol_diffs = df.iloc[:, 1].values - df.iloc[:, 2].values
mean = np.mean(sol_diffs)

for i in range(0, max(level_ids), 5):
    plt.axvline(x=i, color='lightblue', linestyle='--')
plt.scatter(level_ids, sol_diffs, marker='x', color='b')
plt.axhline(y=mean, color='r', linestyle='--', label=f'Mean: {mean:.2f}')
plt.xlabel("Level Id")
plt.ylabel("Box Pushes Schokoban - Box Pushes Vanillaban")
plt.legend(loc='lower left')
plt.show()