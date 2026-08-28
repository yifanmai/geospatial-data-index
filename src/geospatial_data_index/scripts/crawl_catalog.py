import argparse
from pathlib import Path

from geospatial_data_index.crawl import crawl_root_catalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog_url", help="URL of root catalog")
    parser.add_argument("output_directory", help="Path to root output directory; will be created if it does not exist")
    args = parser.parse_args()
    crawl_root_catalog(args.catalog_url, Path(args.output_directory))
