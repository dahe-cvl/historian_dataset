"""
Compute precision and recall of our SBD predictions by comparing them to the manual annotations
Creates a list of all films with manual annotation data
"""

import os
import glob
import json

path_auto_annotations = r"./annotations/automatic"
path_manual_annotations = r"./annotations/manual"
path_videos = r"./films"

path_manual_annotations_films = r"./statistics/films_with_manual_annotations.txt"

auto_paths = glob.glob(os.path.join(path_auto_annotations, "*-shot_annotations.json"))
manual_paths = glob.glob(os.path.join(path_manual_annotations, "*-shot_annotations.json"))

combined_paths = zip(auto_paths, manual_paths)

get_vid = lambda path: os.path.split(path)[-1].split("-shot_annotations")[0]

print(len(auto_paths), len(manual_paths))

def compute_metrics(tp, tn, fp, fn):
    precision = float(tp) / (tp+fp)
    recall = float(tp) / (tp + fn)
    accuracy = float(tp + tn) / (tp + tn + fp + fn)
    f1 = 2*precision*recall / (precision+recall)
    print(f"Precision: {precision}\nRecall: {recall}\nF1: {f1}\nAccuracy: {accuracy}")

vids_with_manual_annotations = []
nr_non_empty_manual_annotations = 0
manual_shots = 0
auto_shots = 0
tp, tn, fp, fn =  0, 0, 0, 0
for auto_path, manual_path in combined_paths:
    # Check whether we compare the correct json files
    assert get_vid(auto_path) == get_vid(manual_path)

    with open(auto_path) as f:
        shots_auto = json.load(f)
    with open(manual_path) as f:
        shots_manual = json.load(f)

    inPoints_auto = [shot["inPoint"] for shot in shots_auto]
    inPoints_manual = [shot["inPoint"] for shot in shots_manual]

    # Do not use empty annotations
    if len(inPoints_manual) == 0:
        continue

    vids_with_manual_annotations.append(get_vid(auto_path))


    nr_frames = max([shot["outPoint"] for shot in shots_auto])
    manual_shots += len(inPoints_manual)
    auto_shots += len(inPoints_auto)
    nr_non_empty_manual_annotations += 1

    new_tp = 0
    new_fp = 0
    new_fn = 0
    for inPoint in inPoints_auto:
        if inPoint in inPoints_manual:
            new_tp += 1
        else:
            new_fp += 1

    for inPoint in inPoints_manual:
        if not inPoint in inPoints_auto:
            new_fn += 1

    new_tn = nr_frames - new_tp - new_fp - new_fn
    tp += new_tp
    tn += new_tn
    fp += new_fp
    fn += new_fn

print("EVALUATION DATA")
print(f"Total automatic shots: {auto_shots}")
print(f"Total manual shots: {manual_shots}")
print(f"Total videos checked: {nr_non_empty_manual_annotations}")

print(f"tp: {tp}, tn: {tn} fp: {fp}, fn: {fn}")
compute_metrics(tp, tn, fp, fn)
