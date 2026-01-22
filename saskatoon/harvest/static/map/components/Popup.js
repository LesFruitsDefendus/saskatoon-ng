import { Button } from "./Button.js";
import { HarvestCard } from "./HarvestCard.js";
import { Header } from "./Header.js";
import { Link } from "./Link.js";

export function PopupProperty({ feature, property_url, harvest_url }) {
  const property = feature.properties;

  const [name, address] = property.title.split("at");

  const popupHeader = Header({
    title: `<h3>${address}</h3>`,
    subtitle: `<h4>${name}</h4>`,
    tag: `<h4>${property.neighborhood}</h4>`,
  });

  // const trees = `<p>${JSON.stringify(property.trees, null, 2)}</p>`;

  const propertyBody = `
    <div class="map_propertyBody">
      ${Button({
        className: "map_detailsButton",
        href: `${property_url}${property.id}`,
        label: "Property details",
      })}
    </div>
  `;

  const harvestsHeader = `
    <div class="map_harvestsHeader"> 
      <h5>${property.harvests.length > 0 ? "Harvests" : "No harvests!"}</h5>
    </div>
  `;

  const harvestsList = `
    <div class="map_harvestsList_container">
      <ul class="map_harvestsList">
        ${property.harvests
          .map((harvest) =>
            Link({
              href: `${harvest_url}${harvest.id}`,
              children: [HarvestCard({ harvest })],
            }),
          )
          .join("")}
      </ul>
    </div>
  `;

  return `
    <div class="map_popup">
      ${popupHeader}
      ${propertyBody}

      ${harvestsHeader}
      ${harvestsList}
    </div>
  `;
}
