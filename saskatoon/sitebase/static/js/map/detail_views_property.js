import { mapInit } from "./utils.js";

// TODO: Hit API with filter for current property being viewed
const DATA_URL = "/property/geo/";

window.addEventListener("map:init", mapInit(DATA_URL, { center: true }));
