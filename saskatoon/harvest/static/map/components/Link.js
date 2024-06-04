/**
 * Wrapper component for an `<a>` tag.
 *
 * @param {Object} opts
 * @param {string} opts.href - URL that the link directs to.
 * @param {string[]} [opts.children = []] - Array of components
 */
export function Link({ href, children = [] }) {
  return `
    <a href="${href}">
      ${children.join("")}
    </a>
  `;
}
