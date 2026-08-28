import os

import geojson_validator
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pystac import Catalog

MONGODB_URI = os.environ.get("MONGODB_URI")
# Create a new client and connect to the server


COLLECTION_NAME = "stac-items"
BASE_PATH = "/home/yifanmai/oss/geospatial-data-index/stac_catalogs"


def get_mongo_client() -> MongoClient:
    if not MONGODB_URI:
        import pdb
        pdb.set_trace()
        raise Exception("MONGODB_URI environment ariable must be set")
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client

def get_items_to_ingest(catalog_path: str):
    catalog = Catalog.from_file(catalog_path)
    for item in catalog.get_items(recursive=True):
        path = os.path.relpath(item.self_href, BASE_PATH)
        # id_parts = [item.id]
        # ancestor = item.get_parent()
        # assert ancestor
        # root = ancestor.get_root()
        # assert root
        # while ancestor != root:
        #     id_parts.append(ancestor.id)
        #     ancestor_parent = ancestor.get_parent()
        #     assert ancestor_parent
        #     ancestor = ancestor_parent
        # id_parts.append(ancestor.id)
        # id_parts.reverse()
        # id = "/".join(id_parts)
        # yield id
        # item.geometry
        geometry = item.geometry
        validation_results = geojson_validator.validate_geometries(geometry)
        if validation_results["invalid"]:
            fixed_features = geojson_validator.fix_geometries(geometry)["features"]
            assert len(fixed_features) == 1
            geometry = fixed_features[0]["geometry"]
            import pdb
            pdb.set_trace()

        yield {
            "path": path,
            "geometry": geometry,
        }

def ingest_catalog_into_mongodb(catalog_path: str):
    client = get_mongo_client()
    database = client.get_database()
    collection = database.get_collection(COLLECTION_NAME)
    collection.list_indexes()
    collection.create_index("path", unique=True)
    collection.create_index(
        [( "geometry", "2dsphere" )]
    )
    for item in get_items_to_ingest(catalog_path):
        collection.insert_one(item)

