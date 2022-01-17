"""

"""

# Either auto or manual
# decides whether to use auto or manual annotations
prefix = "auto"

path_auto_annotations = r"./annotations/automatic"
path_manual_annotations = r"./annotations/manual"
path_vis = r"./visualizations"
path_stats = r"./statistics"

format = ".png"
dpi = 300
barplot_width = 0.35

import os, json, glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if prefix == "auto":
    path_annotations = path_auto_annotations
elif prefix == "manual":
    path_annotations = path_manual_annotations
else:
    raise ValueError("Prefix is neither auto nor manual")

def store_plot(visualizaion_name):
    path =  os.path.join(path_vis, prefix + "_" + visualizaion_name + format)
    plt.savefig(path, dpi=dpi)

json_paths = glob.glob(os.path.join(path_annotations, "*.json"))
all_shots = []
movies = []
for path in json_paths:
    with open(path) as f:
        shots = json.load(f)
    movies.append(shots)
    all_shots += shots

nr_shots_per_movie = list(map(lambda shots: len(shots), movies))

df = pd.DataFrame.from_records(all_shots)
df['duration'] = df["outPoint"] - df["inPoint"]

statistics_string = ""
statistics_string += "Total number of shots: {0}".format(len(all_shots))
statistics_string += "\nNr shots / film avg.: {0}".format(np.mean(nr_shots_per_movie))
statistics_string += "\nNr shots / film std.: {0}".format(np.std(nr_shots_per_movie))

for target_cat in ["shotType", "cameraMovement"]:
    statistics_string += "\n\n" + target_cat
    for category in df[target_cat].unique():
        nr = df.loc[df[target_cat] == category].shape[0]
        statistics_string += "\n\t{0}: {1}".format(category, nr)



# Plot stc / cmc vs shot duration
def plot_type_vs_shotduration(df, use_log_scaling):
    for target_cat in ["shotType", "cameraMovement"]:
        means = []
        medians = []
        stds = []
        names = []
        values = []
        for category in df[target_cat].unique():
            selected_values = df.loc[df[target_cat] == category]
            means.append(np.median(selected_values["duration"]))
            medians.append(np.median(selected_values["duration"]))
            stds.append(np.std(selected_values["duration"]))
            names.append(category)
            values.append(selected_values["duration"].tolist())

        # As histogram
        fig, ax = plt.subplots()
        ax.hist(values, bins=25, linewidth=0.5, edgecolor="white", label=names, stacked=True)
        if use_log_scaling:
            ax.set_yscale('log')

        ax.set_xlabel('Duration (frames)')
        ax.set_ylabel('Number of Shots')
        ax.set_title("Histogram of " + target_cat)
        plt.legend(loc='upper right')
        if use_log_scaling:
            store_plot(target_cat + "_vs_duration(histogram, log)")
        else:
            store_plot(target_cat + "_vs_duration(histogram)")
        plt.close()

        # As a barplot
        ind = np.arange(len(names))
        plt.bar(ind, means, barplot_width, yerr=stds)
        plt.ylabel('Duration (frames)')
        plt.xticks(ind, names)
        store_plot(target_cat + "_vs_duration(barplot)")
        plt.close()

# Plot number of stc/ cmc shots
def plot_nr_shots(df):
    index = df["shotType"].value_counts().index.tolist()
    values = []

    for cmc in ["NA", "PAN", "TILT"]:
        selected_rows = df.loc[df["cameraMovement"] == cmc]
        values.append(selected_rows["shotType"].value_counts())

    ind = np.arange(len(index))
    plt_NA = plt.bar(ind, values[0], barplot_width, label="NA")
    plt_TILT = plt.bar(ind, values[1], barplot_width, bottom=values[0], label="TILT")
    plt_PAN = plt.bar(ind, values[2], barplot_width, bottom=np.array(values[0])+np.array(values[1]), label="PAN")

    plt.ylabel('Number of Shots')
    plt.title("Shot Distribution")
    plt.legend(loc="upper right", title="cameraMovement")
    plt.xticks(ind, index)
    plt.xlabel("shotType")
    store_plot("shot_distribution")
    plt.close()

# Plot stc / cmc vs shot starting point
def plot_type_vs_inPoint(df, use_log_scaling):
    for target_cat in ["shotType", "cameraMovement"]:
        means = []
        medians = []
        stds = []
        names = []
        values = []
        for category in df[target_cat].unique():
            selected_values = df.loc[df[target_cat] == category]
            means.append(np.median(selected_values["inPoint"]))
            medians.append(np.median(selected_values["inPoint"]))
            stds.append(np.std(selected_values["inPoint"]))
            names.append(category)
            values.append(selected_values["inPoint"].tolist())

        # As histogram
        fig, ax = plt.subplots()
        ax.hist(values, bins=25, linewidth=0.5, edgecolor="white", label=names, stacked=True)
        if use_log_scaling:
            ax.set_yscale('log')

        ax.set_xlabel('Frame')
        ax.set_ylabel('Number of Shots')
        ax.set_title("Histogram of inPoints of " + target_cat)
        plt.legend(loc='upper right')
        if use_log_scaling:
            store_plot(target_cat + "_vs_inPoint(histogram, log)")
        else:
            store_plot(target_cat + "_vs_inPoint(histogram)")
        plt.close()

# PLOT

# plot_type_vs_shotduration(df, True)
# plot_type_vs_shotduration(df, False)
# plot_nr_shots(df)
# plot_type_vs_inPoint(df, True)
# plot_type_vs_inPoint(df, False)

# TEXT STATISTICS

print(statistics_string)
with open(os.path.join(path_stats, prefix + "_shots.txt"), 'w') as f:
    f.write(statistics_string)

print(df)
