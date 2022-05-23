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
path_shot_annotations = r"./annotations/manual"
path_cmc_annotations = r"./annotations/camera_annotations_manual"
path_osd_annotations = r"./annotations/overscan_manual"

# path_osd_annotations = r"/caa/Homes01/fjogl/SprocketHolesFinder/Weak_annotations"
# path_osd_annotations = r"/caa/Homes01/fjogl/SprocketHolesFinder/Output"

path_output = r"./Evaluation/Visualizations"


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
    film_name = os.path.split(path_film)[-1]

    with open(path_shot_annotation) as file:
        shots = json.load(file)

    if os.path.isfile(path_cmc_annotation):
        with open(path_cmc_annotation) as file:
            cms = json.load(file)
    else:
        cms = []
        print("No camera annotation found")

    if has_osd_annotation:
        with open(path_osd_annotation) as file:
            osd = json.load(file)

        osd.sort(key=lambda o: int(o["meta_info"]["frmId"]))
    else:
        print("No OSD annotations found for this video")

    tab = "             "

    path = os.path.join(path_output, f"{args.vid}-visualization.m4v")
    print(f"Storing video at {path}")
    cap = cv2.VideoCapture(path_film)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None
    for frame in count():
        success, img = cap.read()

        if not success:
            break

        if out is None:
            out = cv2.VideoWriter(path,fourcc, 24, (img.shape[1], img.shape[0]+50))

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

            # Find the relevant OSD annotation
            relevant_osd = None
            if has_osd_annotation:
                # Case 1: we have annotations in this shot
                osds_in_this_shot = list(filter(lambda o: int(o["meta_info"]["shotId"]) == relevant_shot[0]["shotId"], osd))

                if len(osds_in_this_shot) > 0:
                    osds_in_this_shot.sort(key=lambda o: int(o["meta_info"]["frmId"]))
                    relevant_osd = osds_in_this_shot[0]

                # Case 2: we have annotations before this shot, then we take the closest to the current shot (framewise)
                if relevant_osd is None:
                    osds_before_this_shot = list(filter(lambda o: int(o["meta_info"]["shotId"]) < relevant_shot[0]["shotId"], osd))
                    osds_before_this_shot.sort(key=lambda o: int(o["meta_info"]["frmId"]))
                    if len(osds_before_this_shot) > 0:
                        relevant_osd = osds_before_this_shot[-1]

                # Case 3: we take an annotation after this shot
                if relevant_osd is None:
                    osds_after_this_shot = list(filter(lambda o: int(o["meta_info"]["shotId"]) > relevant_shot[0]["shotId"], osd))
                    osds_after_this_shot.sort(key=lambda o: int(o["meta_info"]["frmId"]))
                    relevant_osd = osds_after_this_shot[0]

                blank_canvas = np.zeros_like(img, np.uint8)
                for region in relevant_osd["regions"]:
                    pts = np.array([[point["x"], point["y"]] for point in region["points"]], np.int32)
                    pts = pts.reshape((-1,1,2))

                    if region["type"] == "POLYGON":

                        cv2.polylines(img,[pts],True,(0,0,255),2)
                        # cv2.drawContours(blank_canvas, [pts], -1, color=(0,0,255), thickness=cv2.FILLED)
                        cv2.fillPoly(blank_canvas, pts = [pts], color =(0,0,255))

                        # cv2.imshow("hi", blank_canvas)
                        # cv2.waitKey(0)
                        # cv2.imshow("hi",img)
                        # cv2.waitKey(0)
                        # quit()
                    else:
                        cv2.polylines(img,[pts],True,(0,255,0),2)

                # cv2.imshow("hi", blank_canvas)
                # cv2.waitKey(0)
                alpha = 0.75
                mask = blank_canvas.astype(bool)
                # full_canvas[mask] = full_canvas2[mask]
                img[mask] = cv2.addWeighted(img, alpha, blank_canvas, 1 - alpha, 0)[mask]
                # img2 = cv2.addWeighted(img, alpha, blank_canvas, 1 - alpha, 0)
                #cv2.imshow("hi", img)
                #cv2.waitKey(0)
                # img2[np.invert(mask)] = img[np.invert(mask)]
                # cv2.imshow("hi", img2)
                # cv2.waitKey(0)

            # Create image and store it
            white_bar = np.zeros([25, img.shape[1], 3],dtype=np.uint8)
            white_bar.fill(255)

            white_bar2 = np.copy(white_bar)

            cv2.putText(white_bar,f"VID: {args.vid}{tab}Name: {film_name}", (0,15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, [0, 0, 255], 1, cv2.LINE_AA)
            cv2.putText(white_bar2,f"Frame: {frame}{tab}Camera movement: {camera_movement}{tab}Shot type: {shot_type}{tab}Shot length: {shot_length}{tab}Next shot in {next_shot_in}",
                (0,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 255], 1, cv2.LINE_AA)
            img = np.vstack([white_bar, white_bar2, img])
            out.write(img)
        frame += 1

    out.release()



if __name__ == "__main__":
    main()
