"""
Combine cameraMovement and shotType entries into a single entry in automatic annotations.

E.g. {"inPoint": 1, "outPoint": 257, "cameraMovement": "NA"}, {"inPoint": 1, "outPoint": 257, "shotType": "LS"}
becomes {"inPoint": 1, "outPoint": 257, "cameraMovement": "NA", "shotType": "LS"}

This makes parsing the JSON files easier.
Also removes 1 from inPoint and outPoint s.t. the first frame is 0.
"""

import os, glob, json

path_auto_annotations = r"./annotations/automatic"

##########################
# MAIN SECTION
##########################

annotation_paths = glob.glob(os.path.join(path_auto_annotations, "*.json"))

for annotation_path in annotation_paths:
    shots_new = []
    with open(annotation_path) as f:
        shots_old = json.load(f)

    for shot in shots_old:
        # First element
        if shots_new == []:
            shots_new.append(shot)
            continue

        if shots_new[-1]["inPoint"] == shot["inPoint"] and shots_new[-1]["outPoint"] == shot["outPoint"]:
            if "shotType" in shot:
                shots_new[-1]["shotType"] = shot["shotType"]
            else:
                shots_new[-1]["cameraMovement"] = shot["cameraMovement"]
        else:
            shots_new.append(shot)

    # Check if the shots all contain cameraMovement and shotType
    # Remove 1 from inPoint and outPoint
    for shot in shots_new:
        if "shotType" not in shot:
            raise ValueError("shotType not found")
        elif "cameraMovement" not in shot:
            shot["cameraMovement"] = "NA"

        shot["inPoint"] = shot["inPoint"] - 1
        shot["outPoint"] = shot["outPoint"] - 1
        
    assert len(shots_new) >= (len(shots_old) / 2.0) and len(shots_new) <= len(shots_old)

    # print(shots_new)
    # quit()
    with open(annotation_path, 'w') as outfile:
        json.dump(shots_new, outfile)
