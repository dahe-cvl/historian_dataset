"""
Performs shot based comparison of STC.
We have STC that are obtained by applying them to manual shot boundaries. Then we compare the classifications for the different shots
"""

import glob
import os
import csv
import json

from sklearn.metrics import classification_report, confusion_matrix
import sklearn.metrics as metrics

paths_auto_stc  = r"./Evaluation/STC_Data"
paths_manu_stc = r"./annotations/manual"

def main():
    # Check that we have a manual annotation for each auto annotations
    auto_annotations_path = glob.glob(os.path.join(paths_auto_stc, "*.csv"))

    print(len(auto_annotations_path), len(glob.glob(os.path.join(paths_manu_stc, "*.json"))))
    assert len(auto_annotations_path) == len(glob.glob(os.path.join(paths_manu_stc, "*.json")))

    y_true, y_pred = [], []

    for ann_path in auto_annotations_path:
        vid = os.path.split(ann_path)[-1].split('.')[0]
        shots_auto = []

        # Load auto annotation
        with open(ann_path, 'r') as file:
            csv_reader = csv.DictReader(file, delimiter  = ';')
            for shot in csv_reader:
                shots_auto.append({"start": shot["start"], "end": shot["end"], "stc": shot["stc"]})

        # Get manual annotation
        manual_ann_candidates = glob.glob(os.path.join(paths_manu_stc, f"{vid}*.json"))
        assert len(manual_ann_candidates) == 1

        # Compare to manual annotation
        with open(manual_ann_candidates[0], 'r') as file:
            shots_man = json.load(file)

        for i, shot_man in enumerate(shots_man):
            shot_auto = shots_auto[i]
            assert shot_man["inPoint"] == int(shot_auto["start"]) and shot_man["outPoint"] == int(shot_auto["end"])
            y_true.append(shot_man["shotType"])
            y_pred.append(shot_auto["stc"])

            # if shot_man["shotType"] != shot_auto["stc"]:
            #     print(shot_man["shotType"], shot_auto["stc"])

    gt_np = y_true
    preds_np = y_pred
    classes = ["CU", "ELS", "T", "LS", "MS", "NA"]
    report_dict = classification_report(gt_np, preds_np, target_names=classes, output_dict=True)
    matrix = confusion_matrix(gt_np, preds_np)

    output = "\n".join([
        f"Accuracy {metrics.accuracy_score(y_true, y_pred)}",
        f"F1 (macro) {metrics.f1_score(y_true, y_pred, average='macro')}",
        f"{classification_report(gt_np, preds_np, target_names=classes, output_dict=False)}",
        f"{matrix}"
    ])
    print(output)


if __name__ == "__main__":
    main()
