"""
Find and remove duplicate films from the dataset, that is video files that correspond to the same film but a different bitrate
"""

import os, glob, re, json

path_films = r"./films"
path_auto_annotations = r"./annotations/automatic"
path_manual_annotations = r"./annotations/manual"
path_metadata_csv = "metadata.csv"
path_metadata_json = "metadata.json"

##########################
# MAIN SECTION
##########################

# Remove directories from film_name
films = [os.path.split(path)[-1] for path in glob.glob(os.path.join(path_films, "*.m4v"))]

film_without_bitrate = {}
regex = re.compile(r"([0-9]+Mbit)")
for film in films:
    bitrate = regex.search(film).group()
    if bitrate is None:
        continue

    general_name = film.replace(bitrate, "")[5:-1]
    if not general_name in film_without_bitrate:
        film_without_bitrate[general_name] = [(film, bitrate)]
    else:
        film_without_bitrate[general_name].append((film, bitrate))


# Remove
print("Will only keep the entries marked with +")

for ls in list(film_without_bitrate.values()):
    if len(ls) == 1:
        continue

    # If we have duplicate we keep the 12Mbit variant
    target_films = list(filter(lambda tuple: tuple[1] == "12Mbit", ls))
    films_to_remove = list(map(lambda tuple: tuple[0], list(filter(lambda tuple: tuple[1] != "12Mbit", ls))))
    if len(target_films) != 1:
        print("No film with bitrate 12Mbit")
        quit()

    target_film = target_films[0][0]
    print("\nFound the following {0} duplicates:".format(len(ls)))

    for film in list(map(lambda tuple: tuple[0], ls)):
        if film == target_film:
            print("+ {0}".format(film))
        elif film in films_to_remove:
            print("- {0}".format(film))

    # Remove annotations
    ids_to_remove = []
    for film in films_to_remove:
        id = film[0:4]
        ids_to_remove.append(id)
        path_anno_auto = os.path.join(path_auto_annotations, id + ".json")
        path_anno_manu = os.path.join(path_manual_annotations, id + ".json")

        if not os.path.isfile(path_anno_auto):
            print(path_anno_auto, "not found")
        else:
            os.remove(path_anno_auto)

        if not os.path.isfile(path_anno_manu):
            print(path_anno_manu, "not found")
        else:
            os.remove(path_anno_manu)
    print("Removed annotations")

    # Remove from metadata.csv
    with open(path_metadata_csv, "r") as f:
        lines = f.readlines()
    with open(path_metadata_csv, "w") as f:
        for line in lines:
            if line[0:4] not in ids_to_remove:
                f.write(line)
    print("Removed from metadata.csv")

    # Remove from metadata.json
    ids_to_remove = list(map(lambda id: int(id), ids_to_remove))
    with open(path_metadata_json) as f:
        json_old = json.load(f)

    json_new = []
    for entry in json_old:
        if not entry["id"] in ids_to_remove:
            json_new.append(entry)

    with open(path_metadata_json, 'w') as outfile:
        json.dump(json_new, outfile)
    print("Removed from metadata.json")

    # Remove films
    for film in films_to_remove:
        path_to_remove = os.path.join(path_films, film)
        os.remove(path_to_remove)
    print("Removed films")
