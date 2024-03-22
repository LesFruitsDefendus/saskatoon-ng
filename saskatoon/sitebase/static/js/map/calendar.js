import { mapInit } from "./utils.js";

const DATA_URL = "/property/geo/";

window.addEventListener("map:init", mapInit(DATA_URL));
