function getToken() {
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i in cookies) {
            const matches = /csrftoken=(.*)/.exec(cookies[i])
            if (matches?.length > 1) {
                return decodeURIComponent(matches[1]);
            }
        }
    }

    return null;
}

function authorizeProperty(pk) {
    fetch(`/property/${pk}/`, {
        method: 'PATCH',
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
            'Accept': 'application/json',
            'X-CSRFToken': getToken()
        },
        body: '{"authorized": true}'
    }).then((response) => {
        if (response.status == 200) {
            location.reload();
        } else {
            alert(response.status);
        }
    });

}
