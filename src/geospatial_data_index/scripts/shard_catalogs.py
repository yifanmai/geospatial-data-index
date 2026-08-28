import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

CATALOG_HOST_PATTERN = re.compile(r"[^/]+://([^/]+)/?")

def get_catalog_host(catalog: dict) -> str: 
    catalog_url = catalog["url"]
    match = CATALOG_HOST_PATTERN.match(catalog_url)
    if not match:
        return catalog_url.split("/")[0]
    return match[1]

def is_public_static_catalog(catalog: dict) -> bool:
    return not catalog["isPrivate"]  and not catalog["isApi"]

def shard_catalogs():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument("output_path", help="Output directory; will be created if it does not exist")
    parser.add_argument("num_shards", type=int)
    args = parser.parse_args()
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    num_shards = args.num_shards
    with open(input_path, "r") as in_file:
        all_catalogs = json.load(in_file)

    public_static_catalogs = [catalog for catalog in all_catalogs if is_public_static_catalog(catalog)]

    host_to_catalogs: dict[str, list[dict]] = defaultdict(list)
    for catalog in public_static_catalogs:
        host_to_catalogs[get_catalog_host(catalog)].append(catalog)

    shards = [{}] * num_shards

    for index, (host, catalog) in enumerate(host_to_catalogs.items()):
        shards[index % num_shards][host] = catalog

    output_path.mkdir(parents=True, exist_ok=True)
    for index, shard in enumerate(shards):
        shard_path = output_path / f"shard_{index}.json"
        with open(shard_path, "w") as shard_file:
            print(f"writing {shard_path}")
            json.dump(shard, shard_file, indent=2)

    print(f"Wrote {len(public_static_catalogs)} catalogs in {len(host_to_catalogs)} hosts to {num_shards} shards.")
