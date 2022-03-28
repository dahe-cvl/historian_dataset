"""
    Creates the (empty) folder structure for the dataset
"""

import os

folders = [r"./films", r"./visualizations", r"./annotations", r"./annotations/automatic", r"./annotations/manual", r"./annotations/overscan_manual", r"./annotations/camera_annotations_manual"]

for path in folders:
    if not os.path.isdir(path):
        os.mkdir(path)
