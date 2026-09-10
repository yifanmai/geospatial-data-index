// https://openlayers.org/doc/faq.html
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import TileLayer from 'ol/layer/Tile.js';
import OSM from 'ol/source/OSM.js';
import GeoJSON from 'ol/format/GeoJSON.js';


const geojsonObject = {
        'type': 'Polygon',
        'coordinates': [
      [
        [
          38.77115511410053,
          8.957454111257789
        ],
        [
          38.771185084350314,
          8.909402280786303
        ],
        [
          38.81950605991044,
          8.909428862720652
        ],
        [
          38.81948241866229,
          8.957480838823232
        ],
        [
          38.77115511410053,
          8.957454111257789
        ]
      ]
        ],
      }

const vectorSource = new VectorSource({
  features: new GeoJSON().readFeatures(geojsonObject),
});



const vectorLayer = new VectorLayer({
  source: vectorSource,
  // style: styleFunction,
}); 

const washingtonLonLat = [38.77115511410053,
          8.957454111257789];
const map = new Map({
  layers: [
    new TileLayer({
      source: new OSM()
    }),
    vectorLayer,
  ],
  target: 'map',
  view: new View({
    projection: 'EPSG:4326',
    center: washingtonLonLat,
    zoom: 12
  })
});