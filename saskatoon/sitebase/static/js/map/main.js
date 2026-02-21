import "./leaflet.js";

function getAttributeValue(el, attr, defaultVal) {
	const node = el.getAttributeNode(attr);
	return node ? node.value : defaultVal;
}

class LeafletMap extends HTMLElement {
	constructor() {
		super();
		this.map = null;
		this.markerBuffer = [];
		this.markerCluster = null;

		const shadow = this.attachShadow({ mode: "open" });

		// styles are sandboxed in web components
		const leaflet = this.makeLinkNode("/static/js/map/leaflet.css");
		const leafletClusterLink = this.makeLinkNode(
			"/static/js/vendor/leaflet.markercluster-1.4.1/MarkerCluster.css",
		);
		const leafletClusterDefault = this.makeLinkNode(
			"/static/js/vendor/leaflet.markercluster-1.4.1/MarkerCluster.Default.css",
		);
		const fontAwesome = this.makeLinkNode(
			"/static/css/fontawesome/font-awesome.min.css",
		);
		const style = this.makeLinkNode("/static/js/map/style.css");

		const leafletCluster = this.makeScriptNode(
			"/static/js/vendor/leaflet.markercluster-1.4.1/leaflet.markercluster.js",
		);
		const bootstrap = this.makeLinkNode("/static/css/bootstrap.min.css");

		shadow.append(
			leaflet,
			fontAwesome,
			style,
			leafletCluster,
			leafletClusterDefault,
			leafletClusterLink,
			bootstrap,
		);

		// leaflet requires a root element to bind to
		const mapRoot = document.createElement("div");
		mapRoot.id = "leaflet-container";

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
		const map = L.map(mapRoot, {
			minZoom: 9,
		})
			.addLayer(layer)
			.setView([45.5088, -73.5617], 13);

		let markerCluster = null;
		let markerBuffer = [];
		leafletCluster.addEventListener("load", () => {
			markerCluster = L.markerClusterGroup();
			markerCluster.addLayers(markerBuffer);
			map.addLayer(markerCluster);

			// clear memory
			markerBuffer = [];
		});

		this.addEventListener("markerCreated", (event) => {
			if (markerCluster === null) {
				markerBuffer.push(event.detail);
			} else {
				markerCluster.addLayer(event.detail);
			}
		});

		// Make sure the map resizes correctly on css changes
		const resizeObserver = new ResizeObserver(() => {
			map.invalidateSize();
		});

		resizeObserver.observe(mapRoot);
	}

	makeScriptNode(src) {
		const js = document.createElement("script");
		js.src = src;
		js.defer = true;

		return js;
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
	tooltip = null;

	constructor() {
		super();

		const latitude = parseFloat(getAttributeValue(this, "latitude", ""));
		const longitude = parseFloat(getAttributeValue(this, "longitude", ""));
		if (Number.isNaN(longitude) || Number.isNaN(latitude)) {
			throw new Error("Marker needs latitude and longitude attributes");
		}

		this.marker = L.marker([latitude, longitude]);

		// listen for popup changes
		this.addEventListener("popup-created", (event) => {
			this.popup = L.popup({
				content: event.target,
				className: "saskatoon-map-popup",
			});

			this.marker.bindPopup(this.popup, { maxWidth: "auto" });
		});

		// listen for tooltip changes
		this.addEventListener("tooltip-created", (event) => {
			this.tooltip = event.detail;

			this.marker.bindTooltip(this.tooltip);

			// The tooltip can still open when the popup is open
			this.marker.addEventListener("tooltipopen", (_) => {
				if (this.marker.isPopupOpen()) {
					this.tooltip.close();
				}
			});
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
	}

	connectedCallback() {
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
			className: "saskatoon-map-div-icon",
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

// notify leaflet-marker that the tooltip is ready
class LeafletTooltip extends HTMLElement {
	connectedCallback() {
		const direction = getAttributeValue(this, "direction", "auto");
		const tooltip = L.tooltip({
			content: this,
			direction: direction,
		});

		const tooltipCreated = new CustomEvent("tooltip-created", {
			bubbles: true,
			detail: tooltip,
		});

		this.dispatchEvent(tooltipCreated);
	}
}

customElements.define("leaflet-map", LeafletMap);
customElements.define("leaflet-marker", LeafletMarker);
customElements.define("leaflet-icon", LeafletIcon);
customElements.define("leaflet-popup", LeafletPopup);
customElements.define("leaflet-tooltip", LeafletTooltip);
