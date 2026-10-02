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
        obj = objs[0]
        print(obj)
        path = obj["path"]
        geom = obj["feature_collection"]["features"][0]["geometry"]
        
        with conn.cursor() as cur:
            cur.execute("INSERT INTO collections_with_names (name, geom) VALUES (%s, ST_GeomFromGeoJSON(%s))", (path, Jsonb(geom)))
            # cur.execute("""CREATE TABLE collections_with_names (name varchar PRIMARY KEY, geom GEOMETRY)""")

if __name__ == "__main__":
    main()