import json
import logging
from pathlib import Path
from time import sleep

from pystac import Catalog, Collection, Item, Link, STACObject

logger = logging.getLogger(__name__)


# Catalogs and items can have errors... we need to mark them somehow

# We want to get to convert catalogs to "Self-contained Metadata Only"

USE_SLUG = "USE_SLUG"
USE_ID = "USE_ID"
DERIVED_FROM = "derived_from"

NOT_STARTED = "not_started"
RUNNING = "running"
FINISHED = "finished"

# Saving and loading crawl status

STATUS_FILE_NAME = "status.json"
STATUS_KEY = "status"

def get_crawl_status(catalog_destination_directory: Path) -> str:
    status_destination_path = catalog_destination_directory / STATUS_FILE_NAME
    try:
        with open(status_destination_path, "r") as status_file:
            status_contents = json.load(status_file)
            return status_contents[STATUS_KEY]
    except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
        return NOT_STARTED


def set_crawl_status(catalog_destination_directory: Path, status: str) -> None:
    catalog_destination_directory.mkdir(parents=True, exist_ok=True)
    status_destination_path = catalog_destination_directory / STATUS_FILE_NAME
    with open(status_destination_path, "w") as status_file:
        json.dump({STATUS_KEY: status}, status_file)


def add_derived_from_link_to_self_href(stac_object: STACObject) -> None:
    # See https://github.com/radiantearth/stac-spec/blob/v1.1.0/best-practices.md#using-relation-types
    # for "derived_from" link
    self_href = stac_object.get_self_href()
    assert self_href
    if not stac_object.get_single_link(DERIVED_FROM):
        stac_object.add_link(Link(rel=DERIVED_FROM, target=self_href, media_type="application/json"))


def crawl_root_catalog(source_path: str, destination_path: Path, id_strategy: str = USE_ID):
    catalog = Catalog.from_file(source_path)
    normalize_and_save_catalog(catalog, destination_path, id_strategy)


def normalize_and_save_catalog(catalog: Catalog, destination_path: Path, id_strategy: str = USE_ID) -> None:
    catalog_destination_directory = destination_path / catalog.id
    if get_crawl_status(catalog_destination_directory) == FINISHED:
        print(f"skipping {catalog_destination_directory}")
        return
    sleep(0.1)
    print(f"writing {catalog_destination_directory}")
    destination_path.mkdir(parents=True, exist_ok=True)
    catalog.resolve_links()
    if isinstance(catalog, Collection):
        catalog_destination_path = catalog_destination_directory / "collection.json"
    else:
        catalog_destination_path = catalog_destination_directory / "catalog.json"
    add_derived_from_link_to_self_href(catalog)
    catalog.set_self_href(str(catalog_destination_path))
    for child in catalog.get_children():
        try:
            normalize_and_save_catalog(child, catalog_destination_directory, id_strategy)
        except Exception:
            logger.exception(f"Could not save {child.id} to {catalog_destination_directory}")
    if isinstance(catalog, Collection):
        for item in catalog.get_items():
            try:
                normalize_and_save_item(item, catalog, catalog_destination_directory, id_strategy)
            except Exception:
                logger.exception(f"Could not save {item.id} to {catalog_destination_directory}")
    set_crawl_status(catalog_destination_directory, FINISHED)
    catalog.save_object()


def normalize_and_save_item(item: Item, collection: Collection, collection_destination_directory: Path, id_strategy: str = USE_ID) -> None:
    sleep(0.1)
    collection_destination_directory.mkdir(parents=True, exist_ok=True)
    item_destination_path = collection_destination_directory / f"{item.id}.json"
    collection_href = collection.get_self_href()
    assert collection_href
    collection_links = item.get_links("collection")
    if len(collection_links) > 1:
        raise Exception("Expected at most one collection link")
    elif len(collection_links) == 1:
        collection_links[0].target = collection_href
    elif len(collection_links) == 0:
        item.add_link(Link.parent(collection))
    add_derived_from_link_to_self_href(item)
    item.set_self_href(str(item_destination_path))
    item.save_object()
