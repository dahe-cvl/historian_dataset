"""
For a directory full of extracted shots. Counts the number of unique films that those shots are from (requires that the names of the shots start with the film id)
"""

import os
import glob

dir = r"./Evaluation_STC"
film_paths = glob.glob(os.path.join(dir, "**", "*.m4v"), recursive = True)

films = set()
print(f"Total number of extracted shots: {len(film_paths)}")
for path in film_paths:
    name = os.path.split(path)[-1].split('_')[0]
    films.add(name)

print(f"Extracted shots from {len(films)} films")
