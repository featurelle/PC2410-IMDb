const searchGroup = select => document.getElementById('searchGroup').querySelector(select)

function searchSelected() {
    const searchUrl = searchGroup('[name="url"]').value
    const query = searchGroup('[name="query"]').value
    const searchType = searchGroup('[name="type"]').value
    const urlQuery = `?opt=${searchType}&query=${encodeURIComponent(query)}`
    location.href = searchUrl + urlQuery
}

const queryInput = searchGroup('[name="query"]')
queryInput.addEventListener('keyup', event => {
    if (queryInput === document.activeElement && event.key === "Enter") {
        searchSelected()
    }
})