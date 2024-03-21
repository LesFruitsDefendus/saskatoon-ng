/**
 * GeoJSON-tuple of latitude and longitude.
 *
 * @typedef {[number, number]} latitude, longitude
 * */

/**
 * GeoJSON-compatible coordinates.
 *
 * @typedef {object} Geometry
 * @property {type} string
 * @property {LatLng} coordinates
 * */

/**
 * GeoJSON-compatible feature.
 *
 * @typedef {object} Feature
 * @property {type} string
 * @property {number} id
 * @property {Geometry|null} geometry
 * @property {object} properties - model fields
 * */

/**
 * GeoJSON-compatible collection of features.
 *
 * @typedef {object} FeatureCollection
 * @property {string} type
 * @property {Feature[]} features
 * */
