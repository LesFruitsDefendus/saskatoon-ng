import "./leaflet.js";

class LeafletMap extends HTMLElement {
    map = null

    initMap(shadow) {
        // leaflet requires a root element to bind to
        const mapRoot = document.createElement('div');
        mapRoot.id = 'map-root';

        // if no size is set, then the map wont appear
        const styles = window.getComputedStyle(this);
        const height = `height: ${styles.getPropertyValue('height')};`;
        const width = `width: ${styles.getPropertyValue('width')};`;
        mapRoot.style.cssText = `${height}${width}`;

        shadow.appendChild(mapRoot);

        // leaflet requires attribution for all layers
        const layer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });

        // Hardcode location of montreal for now, zooming out should stop if it can contain
        // the whole island
        this.map = L.map(mapRoot, {
            minZoom: 9,
        }).addLayer(layer).setView([45.5088, -73.5617], 11);

        this.addEventListener('markerCreated', (event) => {
            event.detail.addTo(this.map);
        });
    }

    connectedCallback() {
        const shadow = this.attachShadow({ mode: "open" });

        // styles are sandboxed in web components
        const leaflet = this.getLinkNode('/static/js/map/leaflet.css');
        const fontAwesome = this.getLinkNode('/static/css/fontawesome/font-awesome.min.css');

        // marker text needs to be centered and with no bg, leaflet adds one by default
        const divIconStyle = document.createElement('style');
        divIconStyle.innerHTML = '.saskatoon-div-icon { text-align: center; line-height: 20px; }';

        shadow.append(leaflet, fontAwesome, divIconStyle);
        this.initMap(shadow)
    }

    getLinkNode(href) {
        const css = document.createElement('link');
        css.href = href;
        css.rel = 'stylesheet';

        return css;
    }
}

class LeafletMarker extends HTMLElement {
    icon = null
    iconHover = null
    marker = null

    getAttributeValue(val, def) {
        const node = this.getAttributeNode(val);
        return node ? node.value : def;
    }

    getAnchor(val, def) {
        const anchor = this.getAttributeValue(val, def).split(' ').map(Number);
        if (isNaN(anchor[0]) || isNaN(anchor[1])) {
            throw new Error(
                `Marker attribute ${val} should be a space separated pair of integers, got ${anchor}`
            );
        }

        return anchor;
    }

    makeIcon(iconAnchor, iconClass, iconStyle) {
        // popupAnchor value really only matters for the hover icon
        // but can be set for both.
        const popupAnchor = this.getAnchor('popup-anchor', '9 -10');

        const iconEl = document.createElement('i');
        iconEl.className = iconClass;
        iconEl.style.cssText = iconStyle;

        return L.divIcon({
            html: iconEl,
            className: "saskatoon-div-icon",
            popupAnchor,
            iconAnchor,
         });
    }

    constructor() {
        super();

        const long = parseFloat(this.getAttributeValue('long', ''));
        const lat = parseFloat(this.getAttributeValue('lat', ''));
        if (isNaN(long) || isNaN(lat)) {
            throw new Error("Marker needs lat and long")
        }

        // I wish we could use getComputedStyle() for this, but leaflet
        // resets the style of the leaflet-marker tag
        const iconClass = this.getAttributeValue('class', 'fa-solid fa-toolbox')
        const iconStyle = this.getAttributeValue('style', 'color: #0000;');
        const iconAnchor = this.getAnchor('icon-anchor', '0 0');

        this.icon = this.makeIcon(iconAnchor, iconClass, iconStyle);

        // Since we're not using getComputedStyle(), we cant use
        // a real stylesheet to add an on hover rule.
        this.iconHover = this.makeIcon(
            this.getAnchor('icon-anchor-on-hover', iconAnchor.join(' ')),
            this.getAttributeValue('class-on-hover', iconClass),
            this.getAttributeValue('style-on-hover', iconStyle)
        );

        this.marker = L.marker([lat, long], { icon: this.icon });
    }

    connectedCallback() {
        // Use a proper div in case leaflet-marker has many children
        const popup = document.createElement('div');
        popup.append(...this.children);
        this.marker.bindPopup(popup);

        // we want the on hover icon to show when the mouse is
        // over a marker or when it's popup is opened.
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

        // notify leaflet-map that the marker is ready
        const markerCreated = new CustomEvent('markerCreated', {
            bubbles: true,
            detail: this.marker,
        });

        this.dispatchEvent(markerCreated);
    }
}

customElements.define('leaflet-map', LeafletMap);
customElements.define('leaflet-marker', LeafletMarker)
