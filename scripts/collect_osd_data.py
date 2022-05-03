"""
Loads the tool generated overscan detection data and transforms it into the required format.
"""

raw_data_paths = [
                    r"./ICIP_Overscans/part1/annotations_final",
                    r"./ICIP_Overscans/part2/annotations"
                    ]
output_path = r"./annotations/overscan_manual"
films_path = r"./films"
shots_path = r"./annotations/manual"

import os
import json
import glob

def main():
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    frame_annotations = {}

    for raw_data_path in raw_data_paths:
        for file in glob.glob(os.path.join(raw_data_path, "*.json")):
            with open(file) as data:
                frame_annotation = json.load(data)

                # path without file ending
                path_to_frame = os.path.splitext(frame_annotation["asset"]["path"])[0]
                vid, frame = os.path.split(path_to_frame)[-1].split("_")
                vid = int(vid)

                annotation = (int(frame), frame_annotation)

                if vid not in frame_annotations:
                    frame_annotations[vid] = [annotation]
                else:
                    frame_annotations[vid].append(annotation)

    # print(frame_annotations)

    for vid, annotation_tuples in frame_annotations.items():
        # Sort ascending by frame
        annotation_tuples.sort(key=lambda tuple: tuple[0])

        # Get film name
        films = glob.glob(os.path.join(films_path, f"{vid}*.m4v"))
        print(vid, "\n", films)
        assert len(films) == 1
        film_name = os.path.split(films[0])[-1]

        # Get shot file
        with open(os.path.join(shots_path, f"{vid}-shot_annotations.json")) as file:
            shots = json.load(file)

        output = []
        for aid, (frame, annotation) in enumerate(annotation_tuples):
            # Path has wrong entr
            entry = {}

            # First 5 letters are "file:" we do not need those
            path_to_frame = annotation["asset"]["path"][5:]

            os_type = path_to_frame.split('/')[3]
            if os_type == "35_ext":
                os_type = "35_w"

            # Get shotId from shot list
            shot_candidates = list(filter(lambda shot: shot["inPoint"] <= frame and shot["outPoint"] >= frame, shots))
            assert len(shot_candidates) == 1
            shotId = shot_candidates[0]["shotId"]

            entry["meta_info"]  = {
                "aid": str(aid),
                "shotId": str(shotId),
                "frmId": str(frame),
                "orig_name": film_name,
                "vid": str(vid),
                "film_type": os_type,
                "size": annotation["asset"]["size"]
                }
            entry["regions"] = annotation["regions"]
            output.append(entry)

        # Store
        with open(os.path.join(output_path, f"{vid}-overscan_annotations.json"), 'w') as outfile:
            json.dump(output, outfile, indent=4)

if __name__ == "__main__":
    main()
