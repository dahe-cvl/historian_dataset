*Disclaimer: This list is mostly meant to allow us to replicate the dataset generation.*
# Setup

1. Create a python environment and install the required packages.

2. Create the directory structure:
    ```python scripts/create_dirs.py```

# Collect Shot + Film Data
Running the following commands on vhh_core will collect the raw data from VhhMMSI.

3. Manual annotations:
```python download_annotation_results.py -i 8332 8333 8334 8335 8336 8337 8338 8339 8340 8341 8342 8343 8344 8345 8346 8347 8348 8349 8350 8351 8352 8353 8354 8355 8356 8357 8362 8363 8364 8366 8367 8368 8369 8370 8371 8381 8382 8383 8401 8402 8405 8406 8407 8408 8409 8410 8412 8413 8414 8415 8416 8417 8418 8419 8421 8422 8423 8424 8425 8426 8427 8428 8437 8439 8440 8441 8442 8443 8444 8445 8446 8447 8448 8449 8450 8451 8452 9226 9227 9228 9229 9230 9231 9232 9233 9234 9235 9236 9237 9238 9239 9240 9241 9242 9243 9244 9245 9246 -p /data/ext/VHH/datasets/HistShotDS_V2/annotations/manual/ --manual --json```

4. Automatic annotations
```python download_annotation_results.py -i 8332 8333 8334 8335 8336 8337 8338 8339 8340 8341 8342 8343 8344 8345 8346 8347 8348 8349 8350 8351 8352 8353 8354 8355 8356 8357 8362 8363 8364 8366 8367 8368 8369 8370 8371 8381 8382 8383 8401 8402 8405 8406 8407 8408 8409 8410 8412 8413 8414 8415 8416 8417 8418 8419 8421 8422 8423 8424 8425 8426 8427 8428 8437 8439 8440 8441 8442 8443 8444 8445 8446 8447 8448 8449 8450 8451 8452 9226 9227 9228 9229 9230 9231 9232 9233 9234 9235 9236 9237 9238 9239 9240 9241 9242 9243 9244 9245 9246 -p /data/ext/VHH/datasets/HistShotDS_V2/annotations/automatic/ --json```

5. Videos
```python download_videos.py -i 8332 8333 8334 8335 8336 8337 8338 8339 8340 8341 8342 8343 8344 8345 8346 8347 8348 8349 8350 8351 8352 8353 8354 8355 8356 8357 8362 8363 8364 8366 8367 8368 8369 8370 8371 8381 8382 8383 8401 8402 8405 8406 8407 8408 8409 8410 8412 8413 8414 8415 8416 8417 8418 8419 8421 8422 8423 8424 8425 8426 8427 8428 8437 8439 8440 8441 8442 8443 8444 8445 8446 8447 8448 8449 8450 8451 8452 9226 9227 9228 9229 9230 9231 9232 9233 9234 9235 9236 9237 9238 9239 9240 9241 9242 9243 9244 9245 9246 -n -a -p /data/ext/VHH/datasets/HistShotDS_V2/films --full_name```

6. (optional) Check if data collection was successful
```python scripts/check_for_all_files.py```

# Preparing Shot + Film Data
7. Transform raw annotation data to desired format
```python scripts/prepare_raw_annotation_results.py```

8. Remove files without "shot-annotation" from annotations/manual and annotations/automatic
9. (optional) Check if you lost any files
```python scripts/check_for_all_files.py```

# CMC Data
Collect CMC annotations from manual annotations
```python scripts/collect_cmc_data.py```

# OSD Data
Extract OSD data for annotations
```python scripts/extract_frames_for_OSD.py```

Transform annotated OSD data into the required format
```python scripts/collect_osd_data.py```


# Statistics & Evaluation
```python scripts/compute_statistics_shots.py```

```python scripts/compute_statistics_videos.py```
```python scripts/sbd_eval.py > Evaluation/sbd.txt```
```python scripts/stc_eval.py > Evaluation/stc.txt```

# Visualization
To visualize the annotations on a video:
```python scripts/visualize_annotation.py VID (#FRAMES)```
- VID is the ID of the video to visualize (e.g. 8332)
- #FRAMES is an optional parameter that describes how many frames to output.
  For example 2 will mean that every second frame will be written (default: 1)
