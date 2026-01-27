class LeafletMap extends HTMLElement {

    map = null
    icon = null

    initMap(shadow) {
        const mapRoot = document.createElement('div');
        mapRoot.id = 'map-root';
        const style = this.getAttributeNode('style');
        if (style) {
            console.log(style)
            mapRoot.style = style.value;
        }
        shadow.appendChild(mapRoot);
        const layer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });
        const map = L.map(mapRoot, {
            minZoom: 9,
        }).addLayer(layer).setView([45.5088, -73.5617], 11);

        const children = this.children;

        this.icon = L.icon({
            iconUrl: "/static/js/map/icon/marker-default.svg",
            iconSize: [30, 30],
            iconAnchor: [20, 10],
            popupAnchor: [-5, -10],
        });

        this.map = map;
        for (let i = 0; i < children.length; i++) {
            if (children[i].tagName === "LEAFLET-MARKER") {
                this.processMarker(children[i]);
            }
        }
    }

    processMarker(node) {
        const long = parseFloat(node.getAttributeNode('long').value);
        const lat = parseFloat(node.getAttributeNode('lat').value);

        if (long && lat && !isNaN(long) && !isNaN(lat)) {
            L.marker([lat, long], { icon: this.icon }).addTo(this.map).bindPopup(node);
        }
    }

    connectedCallback() {
        const shadow = this.attachShadow({ mode: "open" });
        const leafletcss = this.getLeafletStyleNode();
        const leafletjs = this.getLeafletScriptNode();

        leafletcss.onload = (ev) => {
            shadow.appendChild(leafletjs);
        }

        leafletjs.onload = (ev) => {
            this.initMap(shadow)
        }

        shadow.appendChild(leafletcss);
    }

    getLeafletStyleNode = () => {
        let css = document.createElement('link');
        css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        css.rel = 'stylesheet';
        css.crossorigin = ""

        return css;
    }

    getLeafletScriptNode = () => {
        let js = document.createElement('script');
        js.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        js.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
        js.crossOrigin = '';
        js.async = 'false';

        return js;
    }

}

customElements.define('leaflet-map', LeafletMap);
customElements.define('leaflet-marker', class extends HTMLElement {})
