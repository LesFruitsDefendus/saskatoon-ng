$(document).ready(function () {
    const url = new URL(window.location);
    const searchInput = $('#search-input');

    const currentVal = url.searchParams.get("search");
    if (currentVal) {
        searchInput.val(currentVal);
    }

    function search() {
        url.searchParams.set("search", searchInput.val());
        window.location = url;
    }

    searchInput.keydown(function (e) {
        if (e.keyCode == 13) {
            search();
        }
    });

    $('#search-button').click(search);
});
