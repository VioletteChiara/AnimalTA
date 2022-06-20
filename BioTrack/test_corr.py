import numpy as np

import pandas as pd


video = 'pbio.3000319.s001'
output_filepath = 'C:/Users/Usuario/Desktop/' + video + '_tracked.csv'

df = pd.read_csv(output_filepath)
df.head()
dx = df['pos_x'] - df['pos_x'].shift(2)
dy = df['pos_y'] - df['pos_y'].shift(2)
df['speed'] = np.sqrt(dx**2 + dy**2)
df['cum_dist'] = df['speed'].cumsum()
df = df.sort_values(by=['id', 'frame'])
print(sum(df['pos_x'].isna))