(() => {
    const starsModal = document.querySelector('#starsModal')
    const starsChoice = starsModal.querySelector('#starsChoice')
    const starsDisplay = starsModal.querySelector('#starsDisplay')
    const rateButton = starsModal.querySelector('#starsSubmit')

    for (let input of starsChoice.querySelectorAll('input')) {
        input.addEventListener('click', e => {
            starsDisplay.textContent = e.target.value
        })
    }

    // rateButton.addEventListener('click', e => {
    //     e.preventDefault()
    //     e.stopPropagation()
    //     const postRatingUrl = '/api/simple/ratings/movies/post'
    //     const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value
    //     const form = document.querySelector('#starsForm')
        
    //     const request = new Request(
    //         postRatingUrl,
    //         {
    //             method: 'POST',
    //             headers: {
    //                 'X-CSRFToken': csrfToken
    //             },
    //             mode: 'same-origin',
    //             body: new FormData(form),
    //         }
    //     )
    //     fetch(request).then(response => {location.reload()})
    //     }
    // )
})()