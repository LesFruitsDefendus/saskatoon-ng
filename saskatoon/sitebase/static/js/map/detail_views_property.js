import { mapInit } from "./utils.js";

const DATA_URL = "/data.geojson";

window.addEventListener("map:init", mapInit(DATA_URL));
