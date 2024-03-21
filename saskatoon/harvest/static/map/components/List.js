/**
 * Wrapper component for an `<ul>` tag.
 *
 * @param {Object} opts
 * @param {string} opts.className - class attribute of the `<ul>` element
 * @param {string[]} [opts.children = []] - Array of components
 */
export function Link({ className, children = [] }) {
  return `
    <ul>
      ${children.join("")}
    </a>
  `;
}
