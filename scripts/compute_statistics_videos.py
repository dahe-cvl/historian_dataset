"""
Compute video statistics like the average video length
"""

path_films = r"./films"
path_vis = r"./visualizations"
path_stats = r"./statistics"

format = ".png"
dpi = 300

##########################
# MAIN SECTION
##########################

import os, glob, subprocess
import matplotlib.pyplot as plt
import numpy as np

# https://stackoverflow.com/a/3844467/6515970 (SingleNegationElimination and Boris)
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

# Collect filmelengths
films = glob.glob(os.path.join(path_films, "*.m4v"))
film_lengths = []
for film in films:
    length = get_length(film)
    film_lengths.append(length)

statistics_string = ""
statistics_string += "\nNumber of films: {0}".format(len(films))
statistics_string += "\nFilm length avg.: {0}".format(np.mean(film_lengths))
statistics_string += "\nFilm length std.: {0}".format(np.std(film_lengths))

print(statistics_string)

with open(os.path.join(path_stats, "films.txt"), 'w') as f:
    f.write(statistics_string)

# Plot filme length
fig, ax = plt.subplots()
ax.hist(film_lengths, bins=25, linewidth=0.5, edgecolor="white")

ax.set_xlabel('Seconds')
ax.set_ylabel('Number of Films')
plt.savefig(os.path.join(path_vis, "filmlength" + format), dpi=dpi)
