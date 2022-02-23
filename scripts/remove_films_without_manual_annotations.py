"""
Removes films for which no manual annotations exist
Also removes their annotations and removes them from the metadata files
"""

import os
import glob
import json

path_films = r"./films"
path_auto_annotations = r"./annotations/automatic"
path_manual_annotations = r"./annotations/manual"
path_overscan_annotations = r"./annotations/overscan_manual"

path_metadata_csv = "metadata.csv"
path_metadata_json = "metadata.json"

def main():
    # Collect VIDs of all films
    vids = []
    for manual_ann_path in glob.glob(os.path.join(path_manual_annotations, "*.json")):
        filename = os.path.split(manual_ann_path)[-1]
        # Avoid overcounting VIDs
        if not "-shot_annotations" in filename:
            vids.append(filename.split('.')[0])

    removed_vids = []
    for vid in vids:
        path_auto_ann = os.path.join(path_auto_annotations, f"{vid}.json")
        path_auto_ann2 = os.path.join(path_auto_annotations, f"{vid}-shot_annotations.json")
        path_manual_ann = os.path.join(path_manual_annotations, f"{vid}.json")
        path_manual_ann2 = os.path.join(path_manual_annotations, f"{vid}-shot_annotations.json")

        with open(path_manual_ann) as file:
            manual_ann = json.load(file)

        # Ignore films for which manual annotations exist
        if len(manual_ann) > 0:
            continue
        removed_vids.append(vid)

        # Check if osd exists for this vid
        osd_candidates = glob.glob(os.path.join(path_overscan_annotations, f"{vid}-overscan_annotations.json"))
        assert len(osd_candidates) == 0

        film_candidates = glob.glob(os.path.join(path_films, f"{vid}*.m4v"))
        assert len(film_candidates) == 1
        path_film = film_candidates[0]

        print("\n\nRemoving:",
            f"\n\t{path_auto_ann}",
            f"\n\t{path_auto_ann2}",
            f"\n\t{path_manual_ann}",
            f"\n\t{path_manual_ann2}",
            f"\n\t{path_film}")

        # Remove data:
        os.remove(path_auto_ann)
        os.remove(path_auto_ann2)
        os.remove(path_manual_ann)
        os.remove(path_manual_ann2)
        os.remove(path_film)

        # Remove from metadata.csv
        with open(path_metadata_csv, "r") as f:
            lines = f.readlines()
        with open(path_metadata_csv, "w") as f:
            for line in lines:
                if line[0:4] != vid:
                    f.write(line)
        print("Removed from metadata.csv")

        # Remove from metadata.json
        with open(path_metadata_json) as f:
            json_old = json.load(f)

        json_new = []
        for entry in json_old:
            if str(entry["id"]) != vid:
                json_new.append(entry)

        with open(path_metadata_json, 'w') as outfile:
            json.dump(json_new, outfile)
        print("Removed from metadata.json")



    print(f"Deleted: {removed_vids}")

if __name__ == "__main__":
    main()
