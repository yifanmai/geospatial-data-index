import traceback
from pathlib import Path
import json

from geospatial_data_index.crawl import crawl_catalog


CATALOGS_INDEX_PATH = "/home/yifanmai/oss/geospatial-data-index/catalogs.json"
TARGET_PATH = "/home/yifanmai/oss/geospatial-data-index/stac_catalogs"

target_path = Path("./stac_catalogs/")

def get_public_static_catalogs():
    with open(CATALOGS_INDEX_PATH) as f:
        catalogs = json.load(f)
    return [catalog for catalog in catalogs if not catalog["isPrivate"]  and not catalog["isApi"]]




def main() -> None:
# target_path = Path("./stac_catalogs/")
    catalogs = get_public_static_catalogs()
    for catalog in catalogs:
        catalog_slug = catalog["slug"]
        catalog_url = catalog["url"]
        target_path = Path(TARGET_PATH) / catalog_slug
        status_path = target_path / "status.json"
        if status_path.exists():
            with open(status_path, "r") as status_file:
                status = json.load(status_file)
                if status["status"] == "done":
                    print(f"Catalog already mirrored from {catalog_url} to {target_path}; skipping")
                    continue
        try:
            print(f"Mirroring catalog from {catalog_url} to {target_path}")
            crawl_catalog(catalog_url, target_path)
            with open(status_path, "w") as status_file:
                json.dump({"status": "done"}, f)
            print("Done crawling catalog")
        except Exception:
            traceback.print_exc()
            print(f"Could not mirror catalog from {catalog_url} to {target_path}")
        break

        
        


    # DEMO_URL = "https://storage.googleapis.com/cfo-public/catalog.json"
    # target_path = Path("./stac_mirror_normalized/")
    # print(f"Mirroring catalog at {DEMO_URL} to {target_path}")
    # crawl_catalog(DEMO_URL, target_path)
    # print("Done crawling catalog")

