export function HarvestCard({ harvest }) {
  const statusClass = `harvest_${harvest.status.toLowerCase()}`;

  return `
      <li class="map_harvestItem ${statusClass}">
        <div class="map_harvestItem_id">
          ${harvest.id}
        </div>
        <div class="map_harvestItem_date">
          ${harvest.start_date}
        </div>
        <div class="map_harvestItem_status">
          ${harvest.status}
        </div>
        <div class="map_harvestItem_pointer">
          >
        </div>
      </li>
  `;
}
