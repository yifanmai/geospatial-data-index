import argparse
import os
import json

from geospatial_data_index.crawl import crawl_root_catalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogs_shard", help="Path of catalogs shard")
    parser.add_argument("output_directory", help="Path to root output directory; will be created if it does not exist")
    args = parser.parse_args()

    with open(args.catalogs_shard, "r") as catalogs_file:
        host_to_catalogs = json.load(catalogs_file)
    for catalogs in host_to_catalogs.values():
        for catalog in catalogs:
            catalog_slug = catalog["slug"]
            catalog_url = catalog["url"]
            catalog_output_directory = os.path.join(args.output_directory, catalog_slug)
            crawl_root_catalog(catalog_url, catalog_output_directory)
