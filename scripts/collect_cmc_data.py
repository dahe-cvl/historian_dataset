"""
    Collect and prepare the CMC data for dataset
    (similar to create_tiny_datastet.py but only for CMC)
"""

path_manual_annotations = r"./annotations/manual"
path_camera_annotations = r"./eval_cmc/all_annotations_per_vid_09032022"
path_cmc_output = r"./annotations/camera_annotations_manual"

import os
import json
import glob
import csv

def main():
    if not os.path.isdir(path_cmc_output):
        os.mkdir(path_cmc_output)

    annotations = glob.glob(os.path.join(path_manual_annotations, "*-shot_annotations.json"))
    for path in annotations:
        vid = os.path.split(path)[-1].split('-')[0]

        with open(path) as f:
            manual_annotations = json.load(f)

        path_cam_ann = os.path.join(path_camera_annotations, f"{vid}.csv")

        # Only continue if a camera movement exists
        if not os.path.isfile(path_cam_ann):
            continue

        with open(path_cam_ann) as f:
            csv_reader = csv.DictReader(f, delimiter=';')
            all_camera_annotations = [dict(row) for row in csv_reader]

        # Collect camera annotations
        camera_annotations = []
        for annotation in all_camera_annotations:
            corresponding_shot = list(filter(lambda shot: shot["inPoint"] <= int(annotation["start"]) - 1 and shot["outPoint"] >= int(annotation["stop"]) - 1, manual_annotations))
            # print(annotation)
            # print(corresponding_shot)
            if not len(corresponding_shot) == 1:
                print("VID: ", vid, "Start:", annotation["start"], "Stop:", annotation["stop"])
                continue

            camera_annotations.append({
            "shotId": corresponding_shot[0]["shotId"],
            # Note that SID in the CMCs is actually cmId (see below)
            "cmId": int(annotation["sid"]),
            "Start": int(annotation["start"]) - 1,
            "Stop": int(annotation["stop"]) - 1,
            "class_name": annotation["class_name"]})

        with open(os.path.join(path_cmc_output, f"{vid}-sequence_annotations.json"), 'w') as outfile:
            json.dump(camera_annotations, outfile, indent=4)


if __name__ == "__main__":
    main()
