"""

"""

# Either auto or manual
# decides whether to use auto or manual annotations
prefix = "auto"

path_auto_annotations = r"./annotations/automatic"
path_manual_annotations = r"./annotations/manual"
path_vis = r"./visualizations"
path_stats = r"./statistics"

import os, json, glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if prefix == "auto":
    path_annotations = path_auto_annotations
elif prefix == "manual":
    path_annotations = path_manual_annotations
else:
    raise ValueError("Prefix is neither auto nor manual")

json_paths = glob.glob(os.path.join(path_annotations, "*.json"))
all_shots = []
movies = []
for path in json_paths:
    with open(path) as f:
        shots = json.load(f)
    movies.append(shots)
    all_shots += shots

nr_shots_per_movie = list(map(lambda shots: len(shots), movies))

statistics_string = ""
statistics_string += "Total number of shots: {0}".format(len(nr_shots_per_movie))
statistics_string += "\nNr shots / film avg.: {0}".format(np.mean(nr_shots_per_movie))
statistics_string += "\nNr shots / film std.: {0}".format(np.std(nr_shots_per_movie))

print(statistics_string)
with open(os.path.join(path_stats, prefix + "_shots.txt"), 'w') as f:
    f.write(statistics_string)

df = pd.DataFrame.from_records(all_shots)
df['duration'] = df["outPoint"] - df["inPoint"]

print(df)
