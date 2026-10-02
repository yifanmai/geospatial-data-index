import json
import os


ROOT_PATH = "/home/yifanmai/oss/geospatial-data-index/output/stac_catalogs"
GEOTIFFS_PATH = "/home/yifanmai/oss/geospatial-data-index/output/indexes/collection_paths.json"

def find_all_collections():
    collection_paths = []
    for base_path, _, file_names in os.walk(ROOT_PATH):
        for file_name in file_names:
            file_path = os.path.join(base_path, file_name)
            if file_path.endswith(".gstmp"):
                continue
            with open(file_path) as input_file:
                # print(input_file)
                try:
                    contents = json.load(input_file)
                    # if "profile=cloud-optimized" in contents:
                    # print(contents.get("type"))
                    if contents.get("type") == "Collection":
                        collection_paths.append(file_path)
                        # print(file_path)
                except json.decoder.JSONDecodeError as e:
                    print(f"JSON decode error in {file_path}")
                    print(e)

    with open(GEOTIFFS_PATH, "w") as output_file:
        json.dump(collection_paths, output_file)
    print(f"Found {len(collection_paths)} collections.")



def main():
    find_all_collections()


if __name__ == "__main__":
    main()