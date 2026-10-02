import json
import os


ROOT_PATH = "/home/yifanmai/oss/stac-catalogs"
GEOTIFFS_PATH = "/home/yifanmai/oss/geospatial-data-index/data/geotiff_paths.json"
GEOTIFFS_SAMPLE_PATH = "/home/yifanmai/oss/geospatial-data-index/data/sample_geotiffs.json"

def sample_geotiffs():
    with open(GEOTIFFS_PATH, "r") as geotiffs_paths_file:
        geotiff_paths = json.load(geotiffs_paths_file)
    data_sample = []
    for geotiff_path in geotiff_paths:
        if len(data_sample) > 10:
            break
        if "agroforestry-tree-detection-india" not in geotiff_path:
            continue
        print(geotiff_path)
        with open(geotiff_path, "r") as item_file:
            item = json.load(item_file)
        if item["type"] != "Feature":
            continue
        geotiff_assets = {}
        for asset_key, asset in item["assets"].items():
            if ((asset["href"].startswith("https://") or asset["href"].startswith("http://"))
                    and asset["type"] == "image/tiff; application=geotiff; profile=cloud-optimized"):
                geotiff_assets[asset_key] = asset
        data_sample.append({
            "bbox": item["bbox"],
            "geometry": item["geometry"],
            "assets": geotiff_assets,
        })
    with open(GEOTIFFS_SAMPLE_PATH, "w") as output_file:
        json.dump(data_sample, output_file, indent=2)


def main():
    sample_geotiffs()


if __name__ == "__main__":
    main()