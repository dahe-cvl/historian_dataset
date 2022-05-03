"""
Checks if all necessary files are in the dataset
Run with "python scripts/check_for_all_files.py"
"""

import os, glob

path_films = r"./films"
path_auto_annotations = r"./annotations/automatic"
path_manual_annotations = r"./annotations/manual"
path_metadata_csv = "metadata.csv"

nr_films = 98

##########################
# MAIN SECTION
##########################

films = glob.glob(os.path.join(path_films, "*.m4v"))
annotations_auto = glob.glob(os.path.join(path_auto_annotations, "*.json"))
annotations_manual = glob.glob(os.path.join(path_manual_annotations, "*.json"))

# Check if we have the correct number of files
assert len(films) == nr_films

# Either we have one annotation per film
# or two per film if we have already created the $vid-shot_annotations.json files
assert len(annotations_auto) == nr_films or len(annotations_auto) == 2*nr_films
assert len(annotations_manual) == nr_films or len(annotations_manual) == 2*nr_films
assert os.path.isfile(path_metadata_csv)
print("We have the correct number of files")

# Check that we have an annotation for every film
annotations_auto_just_id = [os.path.split(path)[-1][0:4] for path in annotations_auto]
annotations_manual_just_id = [os.path.split(path)[-1][0:4] for path in annotations_manual]

film_ids = [os.path.split(path_film)[-1].split("_")[0] for path_film in films]

for film_id in film_ids:
    assert film_id in annotations_auto_just_id
    assert film_id in annotations_manual_just_id
    annotations_auto_just_id.remove(film_id)
    annotations_manual_just_id.remove(film_id)
print("There exist annotations for every film")

# Check if every film is in the metadata files
with open(path_metadata_csv, "r") as f:
    lines_from_csv = f.readlines()

for film_id in film_ids:
    assert len(list(filter(lambda line: line.split(',')[1] == film_id, lines_from_csv))) == 1

print("Every film is mentioned once in each metadata file")

print("All checks complete")
