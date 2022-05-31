"""
For each video that has an overscan assigned in metadata.csv,
extract three frames (at 25%, 50%, 75% through the film) to annotate.
"""

import os
import glob
import csv
import cv2

path_metadata = r"metadata_OSD_NEW.csv"
path_films = r"./films"
path_output = r"./tmp_overscan_films/Selected_Frames_14032022_extended"

def main():
    if not os.path.isdir(path_output):
        os.mkdir(path_output)

    with open(path_metadata, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for i, row in enumerate(csv_reader):
            overscan_type= row["overscan_type"]
            if overscan_type != "none":
                print(f"\rFinished extraction from {i} films", end = "")
                path_dir = os.path.join(path_output, row["overscan_type"])
                if not os.path.isdir(path_dir):
                    os.mkdir(path_dir)

                film_path = os.path.join(path_films, row["Filename"])

                cap = cv2.VideoCapture(film_path)
                nr_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                frames = [int(nr_frames*0.25), int(nr_frames*0.5), int(nr_frames*0.75)]

                for frame in frames:
                    cap.set(1, frame)
                    ret, img = cap.read()

                    if not ret:
                        print("Failed")
                        continue

                    cv2.imwrite(os.path.join(path_dir, f"{row['intern_id']}_{frame}.png"), img)

if __name__ == "__main__":
    main()
