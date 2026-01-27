import "./leaflet.js";

class LeafletMap extends HTMLElement {
    map = null

    initMap(shadow) {
        const mapRoot = document.createElement('div');
        mapRoot.id = 'map-root';
        const style = this.getAttributeNode('style');
        if (style) {
            mapRoot.style = style.value;
        }
        shadow.appendChild(mapRoot);
        const layer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });
        this.map = L.map(mapRoot, {
            minZoom: 9,
        }).addLayer(layer).setView([45.5088, -73.5617], 11);

        this.addEventListener('markerCreated', (event) => {
            event.detail.addTo(this.map);
        });
    }

    connectedCallback() {
        const shadow = this.attachShadow({ mode: "open" });
        const leafletcss = this.getLeafletStyleNode();

        shadow.appendChild(leafletcss);
        this.initMap(shadow)
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

class LeafletMarker extends HTMLElement {
    icon = null
    iconHover = null
    marker = null

    constructor() {
        super();

        const long = parseFloat(this.getAttributeNode('long').value);
        const lat = parseFloat(this.getAttributeNode('lat').value);
        const icon = this.getAttributeNode('icon');
        const iconHover = this.getAttributeNode('icon-hover');

        if (!long || !lat || isNaN(long) || isNaN(lat)) {
            throw new Error("Marker needs lat and long")
        }

        this.icon = L.icon({
            iconUrl: icon ? icon.value : '/static/js/map/icon/marker-default.svg',
            iconSize: [30, 30],
            iconAnchor: [20, 10],
            popupAnchor: [-5, -10],
        });

        this.iconHover = L.icon({
            iconUrl: iconHover ? iconHover.value : '/static/js/map/icon/marker-hover.svg',
            iconSize: [36, 36],
            iconAnchor: [23, 13],
            popupAnchor: [-5, -10],
        });

        this.marker = L.marker([lat, long], { icon: this.icon });
    }

    connectedCallback() {
            const popup = document.createElement('div');
            popup.append(...this.children);
            this.marker.bindPopup(popup);

            this.marker.addEventListener('mouseover', (event) => {
                this.marker.setIcon(this.iconHover);
            });

            this.marker.addEventListener('mouseout', (event) => {
                if (!this.marker.isPopupOpen()) {
                    this.marker.setIcon(this.icon);
                }
            });

            this.marker.addEventListener('popupclose', (event) => {
                this.marker.setIcon(this.icon);
            });
            const markerCreated = new CustomEvent('markerCreated', {
                bubbles: true,
                detail: this.marker,
            });

            this.dispatchEvent(markerCreated);
    }
}

customElements.define('leaflet-map', LeafletMap);
customElements.define('leaflet-marker', LeafletMarker)
