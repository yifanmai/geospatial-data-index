import json
import os


ROOT_PATH = "/home/yifanmai/oss/stac-catalogs"
GEOTIFFS_PATH = "/home/yifanmai/oss/geospatial-data-index/data/geotiff_paths.json"

def find_all_geotiffs():
    cog_paths = []
    for base_path, _, file_names in os.walk(ROOT_PATH):
        for file_name in file_names:
            file_path = os.path.join(base_path, file_name)
            with open(file_path) as input_file:
                contents = input_file.read()
                if "profile=cloud-optimized" in contents:
                    cog_paths.append(file_path)
                    # print(file_path)

    with open(GEOTIFFS_PATH, "w") as output_file:
        json.dump(cog_paths, output_file)



def main():
    find_all_geotiffs()


if __name__ == "__main__":
    main()