# HISTORIAN dataset code repository
The official code repository for the historian dataset of the "HISTORIAN: A Large-Scale HISTORIcal Film Dataset with Cinematographic ANnotation" paper. The dataset can be found [here](https://zenodo.org/record/6184281), it contains 98 historical films with annotated shot boundaries, shot types, camera movements, sprocket holes, overscan and film types. The entire dataset is roughly 100gb large.

This repository contains all scripts to generat, evaluate and visualize the dataset from our data (meaning annotations and films). You do not need this repository to use our data. Explanations of how the data is structured are under `Dataset Structure` below.

## How to install
Installing this code is not necessary to use our dataset. 

- Clone the repository ```git clone github.com/dahe-cvl/icprs2022_histshot_v2```
- Change into this directory ```cd icprs2022_histshot_v2```
- Create a folder for the virtual environment ```mkdir venv```
- Create a virtual environment ```python3 -m venv venv```
- Activate virtual environment ```source venv/bin/activate```
- Install requirements ```pip install -r requirements.txt```
- Download data from the link above. Copy the content of the dataset into the repository directory. Afterwards, this directory should contain an `Films` and `Annotations` folder.

## Dataset Structure
The following depicts a frame of a filme together with annotations.
<img src="imgs/film_vis_1.png" alt="Results" width="800">

The data is split into the directories `Films` and `Annotations`.

`Films` contains 98 different films as `.m4v` files. The first four letters of a filename represent the video ID (VID). For example the VID of the film 
```
8367_NARA_LID-111-OF-11-R02_FGMC_NAID-36077_OFMID-1603882747755_H264_1440x1080_AAC-stereo_24fps_12Mbit_GOP01_crop_AC-VHH-P_OFM_2021-10-28.mp4).m4v
```
is 8367. This VID can be used to identify the correspond annotations.


`Annotations` contains manual and automatic annotations of the 98 films. The annotations are organized into directories. Each directory contains annotations of a specific type that can be mapped to a filme via a VID. Note that not every type of annotation is available for each film as not every film has camera movements or overscan area.


`automatic` and `manual` contain shot annotations obtained via automatic or manual annotation, respectively. Each file splits a film into a series of shots and assigns a shot type to each film. For example the following
```
{
        "shotId": 5,
        "inPoint": 810,
        "outPoint": 1001,
        "shotType": "MS"
},
```
is the fifth shot in a film, it starts at frame 810 and its last frame is 1001. This shot is of type `medium shot` (MS).

`camera_annotations_manual` contain manual camera annotations for the films. For example the following
```
{
        "shotId": 39,
        "cmId": 6,
        "Start": 13589,
        "Stop": 13778,
        "class_name": "tilt"
},
```
is the 6th detected camera movement in the film and occurs in shot 39 starting at frame 13589 and ending with frame 13778. This type of camera movement is a `tilt`.

`overscan_manual` contains overscan annotations for each film. Each file has annotations for multiple frames in the film. Each of those frames is annotated with polygons that mark sprocket holes and depending on the film type the frame window. The figure below shows an example of this: red areas are sprocket holes and the green area is the frame window.

## How to Use the Scripts
While this repository contains many scripts, we think the following two are the most relevant.

```visualize_annotation.py``` can be used to visualize annotations via
```
python scripts/visualize_annotation.py $VID $Frames
```
Where $VID is the video idea (for example 427)
The optional $Frames paramter is the distance between rendered frames.
For example for 10 this means that every tenth frame gets rendered.
This makes the resulting video files significantly smaller.
The default value is 1, meaning that every frame gets rendered. An example result of this is shown in the following figure.
<img src="imgs/film_vis_2.png" alt="Results" width="800">

```sprocketHolesFinder.py``` can be used to generate additional sprocket holes annotations from a single annotation.  Use it via
```
python sprocketHolesFinder.py $path_film $path_osd $path_sbd $path_output
```
Where all $path_ point the a film / osd annotation / annotation of any fil, and  $path_output is the path to a file that should store the output.


Finally, the file ```Generate_data_commands.md``` contains information how scripts were used to generate the data. 


## How to Cite
If you use our data, code or ideas, please cite
```
@inproceedings{HISTORIAN,
  title={HISTORIAN: A Large-Scale HISTORIcal Film Dataset with Cinematographic ANnotation},
  author={TBD},
  booktitle={TBD},
  year={2022}
}
```