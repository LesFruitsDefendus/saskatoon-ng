export const mapInit = (dataUrl) => {
  return async (event) => {
    const map = event.detail.map;

    // Download GeoJSON data
    const resp = await fetch(dataUrl);
    const data = await resp.json();

    const onEachFeature = (feature, layer) => {
      const coords = feature.geometry.coordinates;
      if (coords) {
        const latLng = L.latLng(coords[1], coords[0]);
        map.panTo(latLng);
      }
      const props = feature.properties;
      const content = `<h3>${props.title}</h3><p>${props.description}</p>`;
      // <img width="300" src="${props.picture_url}"/>
      layer.bindPopup(content);
    };

    L.geoJson(data, { onEachFeature }).addTo(map);
  };
};
