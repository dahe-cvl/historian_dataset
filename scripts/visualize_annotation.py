"""
Creates a video which visualizes the automatic annotations for a given video.
Run with
    python scripts/visualize_annotation.py $VID $Frames

    Where $VID is the video idea (for example 427)
    The optional $Frames paramter is the distance between rendered frames. 
        For example for 10 this means that every tenth frame gets rendered.
        This makes the resulting video files significantly smaller.
        The default value is 1, meaning that every frame gets rendered
"""

import argparse
import json
import glob
import os
import cv2
import numpy as np
from itertools import count

path_films = r"./films"
path_shot_annotations = r"./annotations/automatic"
path_cmc_annotations = r"./annotations/camera_annotations_manual"
path_osd_annotations = r"./annotations/overscan_manual"
path_output = r"./visualizations"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("vid", type=int)
    parser.add_argument("write_frames", type=int, default=1)

    args  = parser.parse_args()

    print(args.vid)

    path_shot_annotation = os.path.join(path_shot_annotations, f"{args.vid}-shot_annotations.json")
    path_cmc_annotation = os.path.join(path_cmc_annotations, f"{args.vid}-sequence_annotations.json")
    path_osd_annotation = os.path.join(path_osd_annotations, f"{args.vid}-overscan_annotations.json")
    path_film = list(glob.glob(os.path.join(path_films, f"{args.vid}*.m4v")))

    has_osd_annotation = os.path.isfile(path_osd_annotation)

    print(path_film)
    assert len(path_film) == 1
    path_film = path_film[0]

    with open(path_shot_annotation) as file:
        shots = json.load(file)

    with open(path_cmc_annotation) as file:
        cms = json.load(file)

    if has_osd_annotation:
        with open(path_osd_annotation) as file:
            osd = json.load(file)

        osd.sort(key=lambda o: int(o["meta_info"]["frmId"]))
    else:
        print("No OSD annotations found for this video")

    tab = "             "

    path = os.path.join(path_output, f"{args.vid}-visualization.m4v")
    cap = cv2.VideoCapture(path_film)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None
    for frame in count():
        success, img = cap.read()

        if not success:
            break

        if out is None:
            out = cv2.VideoWriter(path,fourcc, 24, (img.shape[1], img.shape[0]+25))
        
        # Only create output every $write_frames frames
        if frame % args.write_frames == args.write_frames - 1:
            print(f"\rWorking on frame {frame}", end="")

            # Get information from annotations
            relevant_cmc = list(filter(lambda a: int(a["Start"]) <= frame and int(a["Stop"]) >= frame, cms))
            if len(relevant_cmc) == 1:
                camera_movement = relevant_cmc[0]["class_name"]
            else:
                camera_movement = "None"

            relevant_shot = list(filter(lambda s: s["inPoint"] <= frame and s["outPoint"] >= frame, shots))
            assert len(relevant_shot) == 1
            shot_length = relevant_shot[0]["outPoint"] - relevant_shot[0]["inPoint"]
            shot_type = relevant_shot[0]["shotType"]

            next_shots = list(filter(lambda s: s["inPoint"] > relevant_shot[0]["inPoint"] , shots))
            # Sort to by starting point to find the next shot
            next_shots.sort(key=lambda s: s["inPoint"])
            
            if len(next_shots) > 0:
                next_shot_in = next_shots[0]["inPoint"] - frame
            else:
                next_shot_in = "N/A"

            if has_osd_annotation:
                relevant_osd = list(filter(lambda o: int(o["meta_info"]["frmId"]) <= frame, osd))

                # If there exists an OSD annotation before the current frame we use that
                if len(relevant_osd) > 0:
                    relevant_osd.sort(key=lambda o: int(o["meta_info"]["frmId"]), reverse=True)
                    relevant_osd = relevant_osd[0]
                # Otherwise we use the earliest OSD (they are sorted by frame)
                else:
                    relevant_osd = osd[0]

                for region in relevant_osd["regions"]:
                    pts = np.array([[point["x"], point["y"]] for point in region["points"]], np.int32)
                    pts = pts.reshape((-1,1,2))
                    if region["type"] == "POLYGON":
                        cv2.polylines(img,[pts],True,(0,255,255),2)
                    else:
                        cv2.polylines(img,[pts],True,(255,255,0),2)

            # Create image and store it
            white_bar = np.zeros([25, img.shape[1], 3],dtype=np.uint8)
            white_bar.fill(255)
            cv2.putText(white_bar,f"Frame: {frame}{tab}Camera movement: {camera_movement}{tab}Shot type: {shot_type}{tab}Shot length: {shot_length}{tab}Next shot in {next_shot_in}", 
                (0,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 255], 1, cv2.LINE_AA)
            img = np.vstack([white_bar, img])
            out.write(img)
        frame += 1

    out.release()



if __name__ == "__main__":
    main()