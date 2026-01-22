import { PopupProperty } from "./components/Popup.js";

/**
 * Generates a callback function to attach to the `map:init` event for django-leaflet maps.
 *
 * @param {Event} event - `map:init` event called by `django-leaflet`
 * @param {string} property_url - URL endpoint of properties.
 * @param {string} harvest_url - URL endpoint of harvests.
 * */
export async function mapInit(event, { property_url, harvest_url }) {
  // for some reason, another seemingly unrelated event ({__leaflet_id: 2, ...}) fires on the same event type
  if (event.type !== "map:init") return;

  /* If FeatureCollection is passed from MapView */
  // const featureCollection = {{ properties|geojsonfeature|safe }};

  /* If JSON endpoints are used. */
  // const featureCollection = await getFeatureCollection(property_url);
  const featureCollection = await getFeatureCollection(property_url, {
    simulatePoints: true,
  });

  const map = event.detail?.map;

  const mapIcon = L.icon({
    iconUrl: "/static/map/icon/marker-default.svg",
    iconSize: [80, 80],
    iconAnchor: [30, 20],
    popupAnchor: [0, -10],
  });

  // Add feature collection to the map
  L.geoJson(featureCollection, { pointToLayer, onEachFeature }).addTo(map);

  /*
   * Converts a feature to a leaflet Layer
   */
  function pointToLayer(feature, latLng) {
    return L.marker(latLng, { icon: mapIcon }).bindPopup(
      PopupProperty({ feature, property_url, harvest_url }),
    );
  }

  /**
   * Callback to run for each feature in a geoJSON FeatureCollection
   */
  function onEachFeature(feature, layer) {}
}

/**
 * Retrieves an objects from the given endpoint and wraps it into the necessary GeoJSON-compatible FeatureCollection shape.
 *
 * @param {string} dataUrl - URL of the GeoJSON API to fetch.
 * @return FeatureCollection
 * */
export async function getFeatureCollection(
  url = "",
  { simulatePoints = false },
) {
  const data = await (async () => {
    try {
      const resp = await fetch(url, {
        headers: {
          Accept: "application/json",
        },
      });
      return await resp.json();
    } catch (e) {
      console.error("Could not fetch properties!\n\n" + e);
    }
  })();

  if (data.type == "FeatureCollection") return data;

  return {
    type: "FeatureCollection",
    features: data.results.map((property) => ({
      type: "Feature",
      id: property.id,
      geometry: property.geom,
      // geometry: simulatePoints ? randomGeometry() : property.geom,
      properties: property,
    })),
  };

  /**
   * Generates a random GeoJSON.PointField geometry object to be used with placeholder data.
   */
  function randomGeometry() {
    return {
      type: "Point",
      coordinates: [-73.4 - Math.random() * 0.4, 45.35 + Math.random() * 0.3],
    };
  }
}
