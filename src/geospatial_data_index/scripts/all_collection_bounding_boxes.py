import geojson
import json
from geojson import Polygon, Feature, FeatureCollection

def main():
    COLLECTION_PATHS_FILENAME = "/home/yifanmai/oss/geospatial-data-index/output/indexes/collection_paths.json"
    GEOJSON_PATH = "/home/yifanmai/oss/geospatial-data-index/output/collections_geojson.json"
    with open(COLLECTION_PATHS_FILENAME, "r") as collection_paths_file:
        collection_paths = json.load(collection_paths_file)
    collections_with_extent = []
    features = []
    for collection_path in collection_paths:
        with open(collection_path, "r") as collection_file:
            collection = json.load(collection_file)
            collection_extent = collection.get("extent")
            if collection_extent and "spatial" in collection_extent and "bbox" in collection_extent["spatial"]:
                coordinates = collection_extent["spatial"]["bbox"][0]
                if not isinstance(coordinates, list):
                    # Some are missing an outer list
                    coordinates = collection_extent["spatial"]["bbox"]
                if len(coordinates) != 4:
                    print(f"Found coordinates with {len(coordinates) / 2} dimensions, skipping")
                    continue
                # print(coordinates)

                polygon = Polygon([[
                                   (coordinates[0], coordinates[1]),
                                   (coordinates[2], coordinates[1]),
                                   (coordinates[2], coordinates[3]),
                                   (coordinates[0], coordinates[3]),
                                   (coordinates[0], coordinates[1]),
                                ]])
                features.append(Feature(geometry=polygon))
                collections_with_extent.append(collection_path)
    feature_collection = FeatureCollection(features=features)
    with open(GEOJSON_PATH, "w") as geojson_file:
        geojson.dump(feature_collection, geojson_file)

    print(f"Found {len(collections_with_extent)} collections with spatial extent")
    
if __name__ == "__main__":
    main()