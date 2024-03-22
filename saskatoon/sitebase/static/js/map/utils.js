/**
 * @typedef {Object} MapInitOpts
 * @property {boolean} center - Center the map at the location of the feature.
 * */

/**
 * Generates a callback function to attach to the `map:init` event for django-leaflet maps.
 *
 * @param {string} dataUrl - URL of the GeoJSON API to fetch.
 * @param {MapInitOpts} [opts={}] - Optional set of options to alter the callback function.
 * @return
 * */
export const mapInit = (dataUrl, opts = {}) => {
  return async (event) => {
    const PROPERTY_URL = "/property";
    const CENTER_ZOOM_FACTOR = 12;
    const map = event.detail.map;

    // Fetch GeoJSON data
    const resp = await fetch(dataUrl);
    const data = await resp.json();

    console.log(data);

    const onEachFeature = (feature, layer) => {
      if (!!opts.center && feature.geometry.coordinates) {
        const coords = feature.geometry.coordinates;
        const latLng = L.latLng(coords[1], coords[0]);
        map.setView(latLng, CENTER_ZOOM_FACTOR);
      }

      console.log(opts.center);

      const props = feature.properties;
      const content = `
        <h3>${props.id}</h3>
        <p>${props.trees}</p>
        <a href="${PROPERTY_URL}/${props.id}">
          <button>
            Details
          </button>
        </a>
      `;
      // <img width="300" src="${props.picture_url}"/>
      layer.bindPopup(content);
    };

    L.geoJson(data, { onEachFeature }).addTo(map);
  };
};
