import os
import json
import psycopg
from psycopg.types.json import Jsonb

GEOJSON_PATH = "/home/yifanmai/oss/geospatial-data-index/output/collections_geojson_with_names.jsonl"

def main():
    connection_string = os.getenv("POSTGIS_CONNECTION_STRING")
    if not connection_string:
        raise Exception("No connection string found")
    objs = []
    with open(GEOJSON_PATH, "r") as f:
        for line in f:
            obj = json.loads(line)
            objs.append(obj)
    # print(objs)
    
    with psycopg.connect(connection_string) as conn:
        for obj in objs:
            path = obj["path"]
            title = obj["title"]
            description = obj["description"]
            geom = obj["feature_collection"]["features"][0]["geometry"]
            
            with conn.cursor() as cur:
                cur.execute("INSERT INTO stac_collections (url, title, description, bbox) VALUES (%s, %s, %s, ST_GeomFromGeoJSON(%s)) ON CONFLICT DO NOTHING", (path, title, description, Jsonb(geom)))
                # cur.execute("""CREATE TABLE collections_with_names (name varchar PRIMARY KEY, geom GEOMETRY)""")

if __name__ == "__main__":
    main()