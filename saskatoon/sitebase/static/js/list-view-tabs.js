// all <a> tags containing rel="keep-params"
// will forward the current params to the destination.
const keepParamsLinks = document.querySelectorAll('[rel="keep-params"]');

keepParamsLinks.forEach((link) => {
	link.addEventListener("click", (event) => {
		event.preventDefault();

		const params = window.location.search;
		const dest = link.getAttributeNode("href").value + params;

		// A short timeout can help overcome browser bugs
		window.setTimeout(() => {
			window.location.href = dest;
		}, 100);
	});
});
