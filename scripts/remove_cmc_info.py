"""
Removes cmc (and other unncessary information) from JSON files.
Adds shotId to JSON.
Also renames them, for example "8247.json" becomes "8247-shot_annotations.json"
"""

import os
import glob
import json

path_auto_annotations = r"./annotations/automatic"
path_manual_annotations = r"./annotations/manual"
keys_to_keep = ["inPoint", "outPoint", "shotType", "isConfirmed", "value", "label"]

for path in [path_auto_annotations, path_manual_annotations]:
    annotations_path = glob.glob(os.path.join(path, "*.json"))
    for annotation_path in annotations_path:
        vid = os.path.split(annotation_path)[-1].split('.')[0]
        with open(annotation_path) as f:
            ann_list_old = json.load(f)
        ann_list_new = []

        shotId = 1
        # Automatic annotations
        if path == path_auto_annotations:
            for annotation in ann_list_old:
                # Skip CMC
                if "cameraMovement" in annotation:
                    continue

                new_annotation = {
                    "shotId": shotId,
                    "inPoint": annotation["inPoint"],
                    "outPoint": annotation["outPoint"],
                    "shotType": annotation["shotType"]}
                ann_list_new.append(new_annotation)
                shotId += 1


        # Manuel annotations
        else:
            for annotation in ann_list_old:
            #     # Skip CMC
                if annotation["value"] in ["PAN", "TILT"]:
                    print(path)

                ann_list_new.append({
                    "shotId": shotId,
                    "inPoint": annotation["inPoint"],
                    "outPoint": annotation["outPoint"],
                    "shotType": annotation["value"]})
                shotId += 1

        # Store in file
        with open(os.path.join(path, f'{vid}-shot_annotations.json'), 'w') as outfile:
            json.dump(ann_list_new, outfile)
