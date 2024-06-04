export function Button({ className = "", href = "", label = "Details" }) {
  return `
      <div class="${className}">
        <a href="${href}">
          <button>
            Property details
          </button>
        </a>
      </div>
    `;
}
