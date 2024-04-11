import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv('Fase3_Javier_Izquierdo.csv')

plt.plot(data['Tiempo'], data['G_parcial'], color='black')
plt.xlim(0, 15)
plt.ylim(0, 3000)

print(np.mean(np.diff(data['Tiempo'])))

g_total = np.sum(data['G_parcial'])
g_parcial_std = np.std(data['G_parcial'])

plt.axvspan(0, 4.15,      facecolor=(.9, 1, 0.12), alpha=0.3, label='Move to Cube')
plt.axvspan(4.15, 4.43,  facecolor=(.8, 0, 0.22), alpha=0.3, label='Open Gripper')
plt.axvspan(4.43, 4.96,  facecolor=(.7, 1, 0.32), alpha=0.3, label='Move arm to cube')
plt.axvspan(4.96, 5.25,  facecolor=(.6, 0, 0.42), alpha=0.3, label='Close Gripper')
plt.axvspan(5.25, 6.84, facecolor=(.5, 1, 0.52), alpha=0.3, label='Move cube to side')
plt.axvspan(6.84, 8.52,  facecolor=(.4, 0, 0.62), alpha=0.3, label='Move cubo to deposit')
plt.axvspan(8.52, 8.81,  facecolor=(.3, 1, 0.72), alpha=0.3, label='Open Gripper')
plt.axvspan(8.81, 10.76,  facecolor=(.2, 0, 0.82), alpha=0.3, label='Return arm to side')
plt.axvspan(10.76, 14.23,  facecolor=(.1, 1, 0.92), alpha=0.3, label='Return arm to original pos')
plt.axvspan(14.23, 15,    facecolor=(.0, 0, 1),    alpha=0.3, label='Extra time')

plt.legend(loc='upper right')
plt.ylabel('G_parcial')
plt.xlabel('Tiempo')
plt.title(f"Tiempo vs G-parcial: G-total = {round(g_total,2)} y Std = {round(g_parcial_std,2)}")
plt.show()
