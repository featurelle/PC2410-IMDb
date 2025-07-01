async function tryPostForm(form, postUrl, csrfToken) {

    if (!csrfToken) {
        csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value
    }
    
    const request = new Request(
        postUrl,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            mode: 'same-origin',
            body: new FormData(form),
        }
    )
    return await fetch(request)
}
