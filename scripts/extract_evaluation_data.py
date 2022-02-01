"""
Used to evaluate the quality of the automatic annotation process.
Extracts a percentage of shots with a given shot type
"""

import argparse
import glob
import os
import json
import math
import random

import numpy as np
import cv2
from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument('type', nargs=1, type=str, default='LS',)
parser.add_argument('percentage', nargs=1, type=float, default=0.1,)

args = parser.parse_args()

dir_stc = r"./Evaluation_STC"
path_auto_annotations = r"./annotations/automatic"
path_films = r"./films"

if not os.path.isdir(dir_stc):
    os.mkdir(dir_stc)

annotations_path = glob.glob(os.path.join(path_auto_annotations, "*-shot_annotations.json"))
shots = []

target_type = args.type[0]
percentage = args.percentage[0]

# Set seeds to ensure reproducibility
np.random.seed(0)
random.seed(0)

# Collect shots
for path in annotations_path:
    with open(path) as f:
        shot_candidates = json.load(f)
    vid = os.path.split(path)[-1].split("-shot_annotations")[0]

    for shot in shot_candidates:
        if shot["shotType"] == target_type:
            shots.append({
                "vid": vid,
                "shotId": shot["shotId"],
                "inPoint": shot["inPoint"],
                "outPoint": shot["outPoint"],
                "shotType": shot["shotType"]})

# Select
nr = math.ceil(len(shots) * percentage)
selected_shots = np.random.choice(shots, size=nr, replace=False)
print(f"Selected {len(selected_shots)} out of {len(shots)} shots with correct type")

# Create output dir
output_dir = os.path.join(dir_stc, target_type)
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

def get_film_path(vid):
    candidates =  glob.glob(os.path.join(path_films, f"{vid}*.m4v"))
    assert len(candidates) == 1
    return candidates[0]


def store_snippet(path_film, path_snipped, inPoint, outPoint):
    # Collect images
    images = []
    cap = cv2.VideoCapture(path_film)
    for frame in range(inPoint, outPoint+1):
        cap.set(1, frame)
        ret, img = cap.read()

        if not ret:
            continue
        images.append(img)

    print(len(images))
    print(images[0].shape, inPoint, outPoint)

    # Fill up every video to at least 5 seconds (assuming a frame rate of 24 fps)
    for _ in range(24*5 - len(images)):
        images.append(images[-1])

    # Store snippet
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path_snipped,fourcc, 24, (images[0].shape[1], images[0].shape[0]))
    for img in images:
        out.write(img)
    out.release()

for shot in tqdm(selected_shots):
    film_path = get_film_path(shot["vid"])
    print(film_path)
    snipped_name = f"{shot['vid']}_SID_{shot['shotId']}_{shot['shotType']}_{shot['inPoint']}_{shot['outPoint']}.m4v"
    snippet_path = os.path.join(output_dir, snipped_name)
    store_snippet(film_path, snippet_path, shot["inPoint"], shot["outPoint"] )
