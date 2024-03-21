export function Header({ title = "", subtitle = "", tag = "" }) {
  return `
      <div class="map_header">
        <div class="map_headerTitle">
          ${title}
        </div>
        <div class="map_headerSubtitle">
          <div class="map_headerSubTitle_left"
            ${subtitle}
          </div>
          <div class="map_headerSubTitle_right"
            ${tag}
          </div>
        </div>
      </div>
    `;
}
