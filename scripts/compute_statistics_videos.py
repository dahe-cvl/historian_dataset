"""
Compute video statistics like the average video length
"""

path_films = r"./films"
path_vis = r"./visualizations"
path_stats = r"./Evaluation"

format = ".pdf"
dpi = 300

##########################
# MAIN SECTION
##########################

import os, glob, subprocess

import matplotlib.pyplot as plt
import numpy as np
import cv2

# https://stackoverflow.com/a/3844467/6515970 (SingleNegationElimination and Boris)
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def get_nr_frames(filename):
    cap = cv2.VideoCapture(filename)
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Collect filmelengths
films = glob.glob(os.path.join(path_films, "*.m4v"))
film_lengths = []
film_frames = []
for film in films:
    film_lengths.append(get_length(film))
    film_frames.append(get_nr_frames(film))

statistics_string = "Number of films: {0}".format(len(films))
statistics_string += "\nTotal duration: {0}s".format(sum(film_lengths))
statistics_string += "\nFilm length avg.: {0}s".format(np.mean(film_lengths))
statistics_string += "\nFilm length std.: {0}s".format(np.std(film_lengths))
statistics_string += "\nFilm length min.: {0}s".format(min(film_lengths))
statistics_string += "\nFilm length max.: {0}s".format(max(film_lengths))

statistics_string += f"\nTotal nr of frames: {sum(film_frames)}"

print(statistics_string)

with open(os.path.join(path_stats, "films_statistics.txt"), 'w') as f:
    f.write(statistics_string)

# Plot filme length
fig, ax = plt.subplots()
ax.hist(film_lengths, bins=50, linewidth=0.5, edgecolor="white")

ax.set_xlabel('Seconds')
ax.set_ylabel('Number of Films')
plt.savefig(os.path.join(path_vis, "filmlength" + format), dpi=dpi)
