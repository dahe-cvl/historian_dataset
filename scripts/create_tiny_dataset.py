"""
For the given film list, creates a tiny variant of the dataset:
    - Containing the first k shots of each film
    - The corresponding shot informations
    - The corresponding camera sequences
    - Overscan needs to be handled manually
"""

film_list = ["8408_(NARA_LID-111-SFR-53-R02_MPPC_NAID-36151_OFMID-1603889378291_H264_1440x1080_AAC-stereo_24fps_12Mbit_GOP01_crop_AC-VHH-P_OFM_2021-10-09.mp4).m4v",
    "8242_(NARA_LID-18-SFP-9115_INSK_NAID-131494090_OFMID-1603878987057_H264_1440x1080_MOS_24fps_08Mbit_GOPvar_uncrop_AC-VHH-P_OFM_2020-12-18.mp4).m4v",
    "8419_(NARA_LID-111-ADC-4233_DNS_NAID-18035_OFMID-1603890649210_H264_1440x1080_MOS_24fps_12Mbit_GOP01_uncrop_AC-VHH-P_OFM_2021-11-11.mp4).m4v"]
nr_shots_per_film = 10

import os
import json
import csv

from extract_evaluation_data import store_snippet


path_manual_annotations = r"./annotations/manual"
path_films = r"./films"
path_camera_annotations = r"./eval_cmc/annotations_per_vid_12022022"
path_tiny_dataset = r"./tiny_dataset"
path_metadata = f"./metadata.csv"

path_tiny_manual_annotations = os.path.join(path_tiny_dataset, "shot_annotations_manual")
path_tiny_camera_annotations = os.path.join(path_tiny_dataset, "camera_annotations_manual")
path_tiny_films = os.path.join(path_tiny_dataset, "films")

# Create directory structure
def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

for path in [path_tiny_dataset, path_tiny_manual_annotations, path_tiny_camera_annotations, path_tiny_films]:
    mkdir(path)

vids = []

for film in film_list:
    vid = film.split("_")[0]
    vids.append(vid)
    path_film = os.path.join(path_films, film)

    path_man_ann = os.path.join(path_manual_annotations, f"{vid}-shot_annotations.json")
    with open(path_man_ann) as f:
        manual_annotations = json.load(f)

    # Only select the first nr_shots_per_film annotations
    manual_annotations = manual_annotations[:nr_shots_per_film]

    last_frame = manual_annotations[-1]["outPoint"]

    path_cam_ann = os.path.join(path_camera_annotations, f"{vid}.csv")
    with open(path_cam_ann) as f:
        csv_reader = csv.DictReader(f, delimiter=';')
        all_camera_annotations = [dict(row) for row in csv_reader]

    # Collect camera annotations
    camera_annotations = []
    for annotation in all_camera_annotations:
        if int(annotation["start"]) <= last_frame:
            corresponding_shot = list(filter(lambda shot: shot["inPoint"] <= int(annotation["start"]) and shot["outPoint"] >= int(annotation["stop"]), manual_annotations))
            assert len(corresponding_shot) == 1

            camera_annotations.append({
            "shotId": corresponding_shot[0]["shotId"],
            # Note that SID in the CMCs is actually cmId (see below)
            "cmId": int(annotation["sid"]),
            "Start": annotation["start"],
            "Stop": annotation["stop"],
            "class_name": annotation["class_name"]})

    # Store annotations
    with open(os.path.join(path_tiny_manual_annotations, f"{vid}-shot_annotations.json"), 'w') as outfile:
        json.dump(manual_annotations, outfile)

    with open(os.path.join(path_tiny_camera_annotations, f"{vid}-sequence_annotations.json"), 'w') as outfile:
        json.dump(camera_annotations, outfile)

    # Store snippet of film
    print(path_film, os.path.join(path_tiny_films, film))
    store_snippet(path_film, os.path.join(path_tiny_films, film), 0, last_frame)

# Metadata
metadata = []
with open(path_metadata) as f:
    csv_reader = csv.DictReader(f, delimiter=';')
    for row in csv_reader:
        entry =  dict(row)
        if entry["id"] in vids:
            metadata.append(entry)

with open(os.path.join(path_tiny_dataset, "metadata.csv"), 'w') as outfile:
    dict_writer = csv.DictWriter(outfile, metadata[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(metadata)

print(metadata)
