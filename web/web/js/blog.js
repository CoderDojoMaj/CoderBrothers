async function loadPage(pageNumber, postsPerPage) { // test function, make sure input is bytearray
	return await fetch(`/posts?page=${pageNumber}&posts_per_page=${postsPerPage}`).then(x => x.text())
}

async function searchPage(search, pageNumber, postsPerPage) { //! TODO MAKE SURE NO ERRORS AND SECURITY VULNS COME FROM THIS
	return await fetch(`/posts?page=${pageNumber}&posts_per_page=${postsPerPage}&search=${search}`).then(x => x.text())
}

let page = 0;
let finished = false;
let search = '';
function loadNextPage(postsPerPage) {
	// Add spinner
	if (!finished) {
		(search === '' ? loadPage(page, postsPerPage) : searchPage(search, page, postsPerPage)).then(html => {
			page++;
			// Remove spinner
			if (html == '') {
				finished = true;
			} else {
				document.getElementById('posts').innerHTML += html;
			}
		})
	}
}
const POSTS_PER_PAGE = 10

loadNextPage(POSTS_PER_PAGE)

document.getElementById('searchBar').onkeypress = function (ev) {
	if (ev.keyCode === 13) {
		// Enter hit
		page = 0
		finished = false
		search = this.value
		this.value = ''
		document.getElementById('posts').innerHTML = '';
		loadNextPage(POSTS_PER_PAGE)
	}
}