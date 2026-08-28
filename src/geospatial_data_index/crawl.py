import os
import json
import logging
from pathlib import Path
from time import sleep
from typing import Optional

from pystac import Catalog, Collection, Item, Link, STACObject
from pystac.layout import HrefLayoutStrategy, BestPracticesLayoutStrategy

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


def _crawl_status_path(catalog: Catalog) -> str:
    catalog_href = catalog.get_self_href()
    assert catalog_href
    return os.path.join(os.path.dirname(catalog_href), STATUS_FILE_NAME)


def _get_crawl_status(catalog: Catalog) -> str:
    try:
        with open(_crawl_status_path(catalog), "r") as status_file:
            status_contents = json.load(status_file)
            return status_contents[STATUS_KEY]
    except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
        return NOT_STARTED


def _set_crawl_status(catalog: Catalog, status: str) -> None:
    with open(_crawl_status_path(catalog), "w") as status_file:
        json.dump({STATUS_KEY: status}, status_file)


def add_derived_from_link_to_self_href(stac_object: STACObject) -> None:
    # See https://github.com/radiantearth/stac-spec/blob/v1.1.0/best-practices.md#using-relation-types
    # for "derived_from" link
    self_href = stac_object.get_self_href()
    assert self_href
    if not stac_object.get_single_link(DERIVED_FROM):
        stac_object.add_link(Link(rel=DERIVED_FROM, target=self_href, media_type="application/json"))


def crawl_root_catalog(source_path: str, destination_path: Path):
    href_layout_strategy = BestPracticesLayoutStrategy()
    source_catalog = Catalog.from_file(source_path)
    catalog_destination_href = href_layout_strategy.get_href(source_catalog, str(destination_path), is_root=True)
    try:
        # Try to resume from destination
        catalog = Catalog.from_file(catalog_destination_href)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        source_catalog.set_self_href(catalog_destination_href)
        source_catalog.save_object()
        catalog = source_catalog
    crawl_catalog_recursively(catalog, BestPracticesLayoutStrategy())


def crawl_catalog_recursively(catalog: Catalog, href_layout_strategy: HrefLayoutStrategy) -> None:
    """
    Precondition: catalog, parent catalog, and all ancestors are in the destination, and have correct parent and root links.
    Postcondition: all descendents are in the destination directory."""
    catalog_href = catalog.get_self_href()
    if _get_crawl_status(catalog) == FINISHED:
        logger.debug(f"skipping {catalog_href}")
        return
    logger.debug(f"crawling {catalog_href}")
    _set_crawl_status(catalog, RUNNING)
    
    catalog_href = catalog.get_self_href()
    for child in catalog.get_children():
        # Child can be from the source or destination directory.
        child_href = href_layout_strategy.get_href(child, catalog_href, is_root=False)
        # Mirror this child from the source to the destination directory.
        # This is idempotent.
        # If the child is already in the destination directory, this does a no-op round trip.
        child.set_self_href(child_href)
        child.save_object()
        catalog.save_object()
        crawl_catalog_recursively(child, href_layout_strategy)
    if isinstance(catalog, Collection):
        for item in catalog.get_items():
            update_item_links(item, catalog, href_layout_strategy)
            item.save_object()
            catalog.save_object()
    _set_crawl_status(catalog, FINISHED)
    catalog.save_object()


def update_catalog_links(catalog: Catalog, parent_catalog: Catalog, href_layout_strategy: HrefLayoutStrategy) -> None:
    """
    Precondition: all ancestors are in the destination, and have correct parent and root links.
    """
    root = parent_catalog.get_root()
    assert root
    catalog.set_root(root)
    catalog.set_parent(parent_catalog)
    parent_href = catalog.get_self_href()
    assert parent_href
    add_derived_from_link_to_self_href(catalog)
    catalog.set_self_href(href_layout_strategy.get_href(catalog, parent_href, is_root=False))



def update_item_links(item: Item, collection: Collection, href_layout_strategy: HrefLayoutStrategy) -> None:
    """
    Precondition: all ancestors are in the destination, and have correct parent and root links.
    """
    root = collection.get_root()
    assert root
    item.set_root(root)
    item.set_parent(collection)
    collection_href = collection.get_self_href()
    assert collection_href
    if len(item.get_links("collection")) == 1:
        item.get_links("collection")[0].target = collection_href
    else:
        item.remove_links("collection")
        item.add_link(Link.collection(collection))
    add_derived_from_link_to_self_href(item)
    item.set_self_href(href_layout_strategy.get_href(item, collection_href, is_root=False))
