"""
Given a film, SBD annotations and a single OSD annotation, this script will try to adapt this OSD annotation to each shot.


Example use:
python sprocketHolesFinder.py "/data/ext/VHH/datasets/HistShotDS_V2/films/8354_(NARA_LID-18-SFP-9195_INSK_NAID-178930081_OFMID-1603878987137_H264_1440x1080_MOS_24fps_12Mbit_GOP01_uncrop_AC-VHH-P_OFM_2021-10-28.mp4).m4v" /data/ext/VHH/datasets/HistShotDS_V2/annotations/overscan_manual/8354-overscan_annotations.json /data/ext/VHH/datasets/HistShotDS_V2/annotations/automatic/8354-shot_annotations.json /caa/Homes01/fjogl/SprocketHolesFinder/Output/8354-overscan_annotations.json

For details on the parameters call this script with "- h"
"""

import argparse
import json
import copy

from matplotlib import pyplot as plt
import numpy as np
import cv2
from sklearn.mixture import GaussianMixture

max_x_range = 20
max_y_range = 20

max_x_widen_polygon = 40
max_y_widen_polygon = 40


def widen_polygons(polygons, change_x, change_y, width, height):
    """
                O-----O
    O--O        |     |
    |  |  ->    |     |
    O--O        |     |
                O-----O
    
    """
    new_polygons = []
    for polygon in polygons:
        points = []
        x_average, y_average = 0, 0
        for point in polygon:
            x_average += point["x"]
            y_average += point["y"]

        x_average = x_average / len(polygon)
        y_average = y_average / len(polygon)

        for point in polygon:
            x = point["x"]
            y = point["y"]

            if x > x_average:
                x = min(width - 1, x + change_x)
            elif x < x_average:
                x = max(0, x - change_x) 

            if y > y_average:
                y = min(height - 1, y + change_y)
            elif y < y_average:
                y = max(0, y - change_y)

            points.append({'x': x, 'y': y})
        new_polygons.append(points)
    return new_polygons

def mask_from_polygons(img, polygons):
    blank_canvas = np.zeros([img.shape[0], img.shape[1]], np.uint8)
    for polygon in polygons:
        pts = np.array([[point["x"], point["y"]]
                       for point in polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))

        cv2.polylines(blank_canvas, [pts], True, ( 255), 2)
        cv2.fillPoly(blank_canvas, pts=[pts], color=(255))

    mask = np.zeros(img.shape[:2], np.uint8)
    mask[blank_canvas.astype(bool)] = 255
    return mask

def generate_mask_from_gmm(polygons, img, max_x_range, max_y_range, has_white_sprocket_holes):
    wider_polygons = widen_polygons(polygons, max_x_range, max_y_range, img.shape[1], img.shape[0])
    # draw_polygons(img, wider_polygon, "original", store = False)
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gmm = GaussianMixture(n_components=1, covariance_type='tied', tol=1e-3,
                    reg_covar=1e-6, max_iter=800, n_init=1, init_params='kmeans',
                    weights_init=None, means_init=None, precisions_init=None,
                    random_state=None, warm_start=False,
                    verbose=False, verbose_interval=10)

    mask = mask_from_polygons(img_bw, wider_polygons)
    polygons_content_as_vector = img_bw[mask == 255].reshape((-1, 1))

    gmm.fit(polygons_content_as_vector)
    threshold = np.mean(gmm.means_)

    binary_img = img.copy()
    binary_img[mask != 255] = 0

    if has_white_sprocket_holes:
        binary_img[binary_img > threshold] = 255
        binary_img[img_bw <= threshold] = 0
    else:
        binary_img[binary_img < threshold] = 255
        binary_img[img_bw >= threshold] = 0

    # cv2.imshow("mask annotation", binary_img)
    # cv2.waitKey(0)
    return binary_img

def find_best_polygons(polygons, img, has_white_sprocket_holes):
    # draw_polygons(img, polygons, "original")
    height, width, _ = img.shape
    best_similarity = -110000000
    best_delta_x, best_delta_y = -1, -1

    mask = generate_mask_from_gmm(polygons, img, max_x_widen_polygon, max_y_widen_polygon, has_white_sprocket_holes)
    # plt.plot(fingerprint_target)
    # plt.show()

    for delta_x in range(int(-max_x_range/2), int(max_x_range/2), 1):
        for delta_y in range(int(-max_y_range/2), int(max_y_range/2), 1):
            trial_polygons = move_polygons(
                polygons, delta_x, delta_y, width, height)
            fingerprint_prediction = analyze_polygons(mask, trial_polygons)
            similarity = float(fingerprint_prediction[255])
            print(f"\rx shift: {delta_x:3}\ty shift: {delta_y:3}\tSimilarity: {similarity:3}", end="")

            if similarity >= best_similarity:
                best_similarity = similarity
                best_delta_x, best_delta_y = delta_x, delta_y
                best_polygon = trial_polygons

    print(f"\rx shift: {best_delta_x:3}\ty shift: {best_delta_y:3}\tSimilarity: {best_similarity}")
    # analyze_polygons(img, move_polygons(polygons, best_delta_x,
    #               best_delta_y, width, height), do_plot = False)

    return best_polygon


def move_polygons(polygons, change_x, change_y, width, height):
    new_polygons = []
    for polygon in polygons:
        points = []
        for point in polygon:
            x = point["x"] 
            y = point["y"] 

            # If we move a BB that touches the wall away from the wall then extend the BB so it keeps touching the BB
            if not (x == 0 and change_x > 0) and not (x == width - 1 and change_x < 0):
                x += change_x

            if not (y == 0 and change_y > 0) and not (y == height - 1 and change_y < 0):
                y += change_y


            # Ensure we do not move a polygon out of the image
            x = max(0, x)
            y = max(0, y)
            x = min(x, width-1)
            y = min(y, height-1)

            points.append({'x': x, 'y': y})

        new_polygons.append(points)

    # print(f"\n\n{polygons}\n{new_polygons}")
    return new_polygons


def draw_polygons(img, polygons, text = "", store = False):
    img = img.copy()
    blank_canvas = np.zeros_like(img, np.uint8)
    for polygon in polygons:
        pts = np.array([[point["x"], point["y"]]
                       for point in polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))

        cv2.polylines(img, [pts], True, (0, 0, 255), 2)
        cv2.fillPoly(blank_canvas, pts=[pts], color=(0, 0, 255))

    mask = blank_canvas.astype(bool)
    alpha = 0.75
    img[mask] = cv2.addWeighted(img, alpha, blank_canvas, 1 - alpha, 0)[mask]

    if store:
        cv2.imwrite(f"./imgs/{text}.png", img)
    else:
        cv2.imshow(text, img)
        cv2.waitKey(0)


def analyze_polygons(img, polygons, do_plot = False):
    """
    Returns an array that encodes the color histogram, normalized to 1
    """
    blank_canvas = np.zeros_like(img, np.uint8)
    for polygon in polygons:
        pts = np.array([[point["x"], point["y"]]
                       for point in polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))

        cv2.polylines(blank_canvas, [pts], True, (0, 0, 255), 2)
        cv2.fillPoly(blank_canvas, pts=[pts], color=(0, 0, 255))

    mask = np.zeros(img.shape[:2], np.uint8)
    mask[blank_canvas.astype(bool)[:,:,2]] = 255

    color_histogram = cv2.calcHist([cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)], [0], mask, [256], [0, 256])
     
    if np.linalg.norm(color_histogram) > 0:
        color_histogram = color_histogram / np.linalg.norm(color_histogram)

    if do_plot:
        plt.plot(color_histogram)
        plt.show()
    
    return color_histogram

def update_osd_annotation(osd_annotations, new_polygons, shot_id, frame):
    aid = len(osd_annotations)
    annotation = {}
    meta_info = copy.deepcopy(osd_annotations[0]["meta_info"])
    
    meta_info["aid"] =  aid
    meta_info["shotId"] = shot_id
    meta_info["frmId"] = frame
    regions = []

    for polygon in new_polygons:
        region = {
                "id": "NAN",
                "type": "POLYGON",
                "tags": [
                    "sprocket_hole"
                ]}

        # region: bounding box
        x_list = [tpl["x"] for tpl in polygon]
        y_list = [tpl["y"] for tpl in polygon]

        min_x, max_x = min(x_list), max(x_list)
        min_y, max_y = min(y_list), max(y_list)
        region["boundingBox"] = {"height": max_y - min_y,
                    "width": max_x - min_x,
                    "left": min_x,
                    "top": min_y}

        # region: points
        region["points"] = copy.deepcopy(polygon)

        regions.append(region)

    osd_annotations.append({"meta_info": meta_info, "regions": regions})

def run_on_film(path_film, osd_annotations, sbd_annotations, samples_per_shot = 1):
    cap = cv2.VideoCapture(path_film)
    nr_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Colllect polygon annotations
    polygons = []
    for i, ann in enumerate(osd_annotations):
        frame_annotation = int(ann["meta_info"]["frmId"])
        print(f"OSD annotation in frame frame {frame_annotation}")
        cap.set(1, frame_annotation)
        success, img = cap.read()

        # Filter out all polygons that are not sprocket holes
        new_polygons = list(
            filter(lambda region: "sprocket_hole" in region["tags"], ann["regions"]))

        # Drop all info from polygons except the points list
        new_polygons = list(map(lambda polygon: polygon["points"], new_polygons))

        # We get the color of the sprocket holes by analyzing whether their color histogram has more darker or brigther colors
        if i == 0:
            histogram = analyze_polygons(img, new_polygons, False)
            lower_half = np.sum(histogram[:123])
            upper_half = np.sum(histogram[123:])
            has_white_sprocket_holes = upper_half > lower_half
            print(f"Sprocket holes color: {'WHITE' if has_white_sprocket_holes else 'BLACK'}")  

        # Determine the boundaries for which this annotation is relevant
        relevant_shots = list(filter(lambda shot: shot["inPoint"] <= frame_annotation and shot["outPoint"] >= frame_annotation, sbd_annotations))
        assert len(relevant_shots) == 1
        relevant_shot = relevant_shots[0]

        if i == 0:
            start_point = 0
        else:
            start_point = polygons[-1][1]

        if i != len(osd_annotations) - 1:
            end_point = relevant_shot["outPoint"]
        else:
            end_point = nr_frames - 1

        polygons.append((start_point, end_point, new_polygons))

    # Collect points for which we want to compute sprocket hole positions
    frames = []
    for shot in sbd_annotations:
        # Edge case: not enough frames in a shot
        # -> use all frames in the shot
        if shot["outPoint"] - shot["inPoint"] < samples_per_shot:
            frames += [(shot["inPoint"] + i, shot["shotId"]) for i in range(shot["outPoint"] - shot["inPoint"] + 1)]
            continue

        frames_between_samples = max(1, int((shot["outPoint"] - shot["inPoint"])/(samples_per_shot+1)))
        frames += [(shot["inPoint"] + i*frames_between_samples, shot["shotId"]) for i in range(samples_per_shot)]

    for (frame, shot_id) in frames:
        cap.set(1, frame)
        success, img = cap.read()

        if not success:
            break

        # Find the relevant polygon from OSD annotations
        relevant_polygons = list(filter(lambda triplet: triplet[0] <= frame and triplet[1] >= frame, polygons))
        assert len(relevant_polygons) == 1

        # [(start, end, [polygon])] -> [polygon]
        relevant_polygons = relevant_polygons[0][2]

        best_polygon = find_best_polygons(relevant_polygons, img, has_white_sprocket_holes)
        update_osd_annotation(osd_annotations, best_polygon, shot_id, frame)

def main(path_film, path_osd, path_sbd, path_output, samples_per_shot):
    # Load osd annotation
    with open(path_osd) as file:
        osd_annotations = json.load(file)
    osd_annotations.sort(key=lambda o: int(o["meta_info"]["frmId"]))
    assert len(osd_annotations) > 0

    # Load sbd annotation
    with open(path_sbd) as file:
        sbd_annotations = json.load(file)
    assert len(sbd_annotations) > 0

    print(f"Number of OSD annotationed frames: {len(osd_annotations)}")
    print(f"Number of shots: {len(sbd_annotations)}")

    run_on_film(path_film, osd_annotations, sbd_annotations, samples_per_shot)

    print(osd_annotations)
    with open(path_output, 'w') as file:    
        json.dump(osd_annotations, file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path_film', type=str,
                    help='Path to the film')
    parser.add_argument('path_osd', metavar='path_osd', type=str,
                    help='Path to an OSD annotation')
    parser.add_argument('path_sbd', metavar='path_sbd', type=str,
                    help='Path to an SBD annotation')
    parser.add_argument('path_out', metavar='path_out', type=str,
                    help='Path where the output OSD file should be stored')
    parser.add_argument('--samples', default=1, type=int,
                    help='Number of samples per shot to detect sprocket holes (default 1)')
    args = parser.parse_args()

    main(args.path_film, args.path_osd, args.path_sbd, args.path_out, args.samples)
