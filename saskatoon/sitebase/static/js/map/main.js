import "./leaflet.js";

function getAttributeValue(el, attr, defaultVal) {
	const node = el.getAttributeNode(attr);
	return node ? node.value : defaultVal;
}

class LeafletMap extends HTMLElement {
	map = null;

	initMap(shadow) {
		// leaflet requires a root element to bind to
		const mapRoot = document.createElement("div");
		mapRoot.id = "map-root";

		// if no size is set, then the map wont appear
		const styles = window.getComputedStyle(this);
		const height = `height: ${styles.getPropertyValue("height")};`;
		const width = `width: ${styles.getPropertyValue("width")};`;
		mapRoot.style.cssText = `${height}${width}`;

		shadow.appendChild(mapRoot);

		// leaflet requires attribution for all layers
		const layer = L.tileLayer(
			"https://tile.openstreetmap.org/{z}/{x}/{y}.png",
			{
				attribution:
					'&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			},
		);

		// Hardcode location of montreal for now, zooming out should stop if it can contain
		// the whole island
		this.map = L.map(mapRoot, {
			minZoom: 9,
		})
			.addLayer(layer)
			.setView([45.5088, -73.5617], 13);

		this.addEventListener("markerCreated", (event) => {
			event.detail.addTo(this.map);
		});

		// Make sure the map resizes correctly on css changes
		const resizeObserver = new ResizeObserver(() => {
			this.map.invalidateSize();
		});

		resizeObserver.observe(mapRoot);
	}

	connectedCallback() {
		const shadow = this.attachShadow({ mode: "open" });

		// styles are sandboxed in web components
		const leaflet = this.makeLinkNode("/static/js/map/leaflet.css");
		const fontAwesome = this.makeLinkNode(
			"/static/css/fontawesome/font-awesome.min.css",
		);
		const style = this.makeLinkNode("/static/js/map/style.css");

		shadow.append(leaflet, fontAwesome, style);
		this.initMap(shadow);
	}

	makeLinkNode(href) {
		const css = document.createElement("link");
		css.href = href;
		css.rel = "stylesheet";

		return css;
	}
}

class LeafletMarker extends HTMLElement {
	marker = null;
	icon = null;
	iconHover = null;
	popup = null;

	constructor() {
		super();

		const latitude = parseFloat(getAttributeValue(this, "latitude", ""));
		const longitude = parseFloat(getAttributeValue(this, "longitude", ""));
		if (Number.isNaN(longitude) || Number.isNaN(latitude)) {
			throw new Error("Marker needs latitude and longitude attributes");
		}

		this.marker = L.marker([latitude, longitude]);
	}

	connectedCallback() {
		// listen for popup changes
		this.addEventListener("popup-created", (event) => {
			this.popup = event.target;
			this.marker.bindPopup(this.popup);
		});

		// listen for icon changes and setup mouse events
		this.addEventListener("icon-created", (event) => {
			this.icon = event.detail;
			this.marker.setIcon(this.icon);

			this.marker.addEventListener("mouseout", (_) => {
				if (!this.marker.isPopupOpen()) {
					this.marker.setIcon(this.icon);
				}
			});

			this.marker.addEventListener("popupclose", (_) => {
				this.marker.setIcon(this.icon);
			});
		});

		this.addEventListener("hover-icon-created", (event) => {
			this.iconHover = event.detail;

			// we want the on hover icon to show when the mouse is
			// over a marker or when it's popup is opened.
			this.marker.addEventListener("mouseover", (_) => {
				this.marker.setIcon(this.iconHover);
			});
		});

		// notify leaflet-map that the marker is ready
		const markerCreated = new CustomEvent("markerCreated", {
			bubbles: true,
			detail: this.marker,
		});

		this.dispatchEvent(markerCreated);
	}
}

class LeafletIcon extends HTMLElement {
	icon = null;

	getAnchor(attr, defaultVal) {
		const anchor = getAttributeValue(this, attr, defaultVal)
			.split(" ")
			.map(Number);
		if (Number.isNaN(anchor[0]) || Number.isNaN(anchor[1])) {
			throw new Error(
				`Icon attribute ${attr} should be a space separated pair of integers, got ${anchor}`,
			);
		}

		return anchor;
	}

	constructor() {
		super();

		const popupAnchor = this.getAnchor("popup-anchor", "9 -10");
		const iconAnchor = this.getAnchor("icon-anchor", "0 0");

		this.icon = L.divIcon({
			html: this,
			className: "saskatoon-div-icon",
			popupAnchor,
			iconAnchor,
		});
	}

	// notify leaflet-marker that the icon is ready
	connectedCallback() {
		const eventName = this.className.includes("leaflet-hover-icon")
			? "hover-icon-created"
			: "icon-created";

		const iconCreated = new CustomEvent(eventName, {
			bubbles: true,
			detail: this.icon,
		});

		this.dispatchEvent(iconCreated);
	}
}

// notify leaflet-marker that the popup is ready
class LeafletPopup extends HTMLElement {
	connectedCallback() {
		const popupCreated = new CustomEvent("popup-created", {
			bubbles: true,
		});

		this.dispatchEvent(popupCreated);
	}
}

customElements.define("leaflet-map", LeafletMap);
customElements.define("leaflet-marker", LeafletMarker);
customElements.define("leaflet-icon", LeafletIcon);
customElements.define("leaflet-popup", LeafletPopup);
