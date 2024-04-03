const IP_ADRESS = 'http://127.0.0.1:8000';
const API_ON = true;
const LIMIT = 20;
const LIMIT_CATEGORIES = 10;

/*-------------------------------------------------------------------------------------------
------------------------------------------ API ----------------------------------------------
--------------------------------------------------------------------------------------------*/
async function APIResquest(request) {
    try {
        let response = await fetch(IP_ADRESS + request);
        var data = await response.json();
    } catch (error) {
        console.log(error);
    }
    return data;
}

async function APIResquest_POST(request, sendData) {
    try {
        let response = await fetch(IP_ADRESS + request, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sendData)
        });
        var status = response.status;
        var data = await response.json();
    } catch (error) {
        console.log(error);
    }
    return { 'status': status, 'body': data };
}

async function GET_OMDb_data(title) {
    let lorem = "Ecstatic. It's that law that's the problem. Desperate times call for desperate measures, my lord.Made you look! Tell her the TRUTH! Without you, I'm just Aladdin. I'm sorry, Rajah, but I can't stay here and have my life lived for me. The power! The absolute power!"
    if (!API_ON) { return { 'poster': undefined, 'Plot': lorem } }

    try {
        let response = await fetch(`http://www.omdbapi.com/?apikey=a2a3f977&t="${title}"`);
        var data = await response.json();
    } catch (error) {
        console.log(error);
    }
    return data;
}

async function GET_KINOCHECK_DATA(imdb_id) {
    try {
        let response = await fetch(`https://api.kinocheck.de/movies?imdb_id=${imdb_id}`);
        var data = await response.json();
    } catch (error) {
        console.log(error);
    }
    return data;
}

async function GetURLTrailer(imdb_id) {
    GET_KINOCHECK_DATA(imdb_id).then(kinocheck_data => {
        let trailer_url = undefined;
        if (kinocheck_data.trailer != undefined) {
            trailer_url = `https://www.youtube.com/watch?v=${kinocheck_data.trailer.youtube_video_id}`;
        }
        return { trailer_url };
    });

}

/*-------------------------------------------------------------------------------------------
---------------------------------------- COOKIES --------------------------------------------
--------------------------------------------------------------------------------------------*/
function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function resetCookie(cname) {
    setCookie(cname, '', 0);
}

/*-------------------------------------------------------------------------------------------
---------------------------------------- POP UP --------------------------------------------
--------------------------------------------------------------------------------------------*/
function AddAnimationPopUpInformation(message, animated = true) {
    let information_pop_up = document.getElementById("information-pop-up");
    information_pop_up.querySelector('span').innerHTML = message;

    information_pop_up.classList.remove("d-none");
    information_pop_up.classList.add("slide-in-from-right");
    if (!animated) {
        information_pop_up.querySelector(".spinner-border").style.setProperty("--bs-spinner-animation-name", undefined);
    }

    setInterval(function () {
        information_pop_up.classList.add("d-none");
        information_pop_up.style.setProperty("--bs-spinner-animation-name", "spinner-border");
    }, 5000);
}

/*-------------------------------------------------------------------------------------------
----------------------------------------- HEADER ---------------------------------------------
--------------------------------------------------------------------------------------------*/
function SearchBar() {
    var baseUrl = window.location.origin;
    let searchFormHeader = document.getElementById("search-form-header");

    if(searchFormHeader){
        searchFormHeader.addEventListener("submit", (e) => {
        // let searchBarHeader = document.getElementById("search-bar-header");
        let test = baseUrl + `/Web/search.html`; 
        window.location.href = test;
    });
    }
}

// function SearchBar() {
//     let searchFormHeader = document.getElementById("search-form-header");

//     if(searchFormHeader){
//         searchFormHeader.addEventListener("submit", (e) => {
//             let searchBarValue = document.getElementById("search-bar-header").value;
//             let request = `/Advancedsearch?title=${searchBarValue}`;
//             var data = APIResquest(request);
    
//             // Affichage des résultats de la recherche
//             data.then(data => {
//                 if (data.length > 0) {
//                     CreateMovieList(data, "Search result", "search-result-movie-list-group", document.getElementById('resultSearchHeader'));
//                 }
//                 else {
//                     let noResSearch = document.createElement("h2");
//                     noResSearch.innerHTML = 'No results found !';
//                     sectionSearch.appendChild(noResSearch);
//                 }
//             });
//         });
//     }
// }

function SetDropdownMenuHeader() {
    /**
     * Set the dropdown menu data with categories in the API.
     */
    let dropdownHeader = document.getElementById("categories-dropdown-menu-header");
    LISTE_GENRE = APIResquest(`/genres?limit=${LIMIT_CATEGORIES}`);
    LISTE_GENRE.then(liste_genre => {
        liste_genre.forEach(genre => {
            let elem_li = document.createElement("li");
            let elem_a = document.createElement("a");
            elem_a.setAttribute("class", "dropdown-item");
            elem_a.setAttribute("href", `home.html#genre_${genre.id_genre}-movie-list-group`);
            elem_a.innerHTML = genre.genre_name;
            elem_li.appendChild(elem_a);
            dropdownHeader.appendChild(elem_li);
        });
    });
}

function AddAnimationSearchLinkHeader() {
    /**
     * Add animation for search link button : Change the arrow direction on click.
     */
    document.querySelector('#link-search-collapse-header').addEventListener('click', function (e) {
        let elem = this.querySelector('i');
        if (elem.classList.contains('bi-arrow-right-square')) {
            elem.setAttribute("class", "bi bi-arrow-down-square-fill")
        } else {
            elem.setAttribute("class", "bi bi-arrow-right-square")
        }
    });
}

function AddAnimationAccountHeader() {
    let account = document.getElementById("account-header");
    let dropdownAccount = account.querySelector("#account-dropdown-menu-header");
    let disconnectButton = dropdownAccount.querySelector("#account-dropdown-menu-header-disconnect");
    let movieLeaveTimer;

    account.addEventListener('mouseover', function (e) {
        clearTimeout(movieLeaveTimer);
        dropdownAccount.classList.add("show")
    });

    account.addEventListener('mouseleave', function (e) {
        movieLeaveTimer = setTimeout(function () {
            dropdownAccount.classList.remove("show")
        }, 500);
    })

    disconnectButton.addEventListener('click', function () {
        resetCookie('Client');
        resetCookie('Profil');
        resetCookie('Watched');
        AddAnimationPopUpInformation("Disconnecting");
        setInterval(function () { window.location.reload(); }, 3000);
    });
}

function SetAccountHeader() {
    /**
     * Change the account header according to the status of the client (connected or disconnected)
     */
    let login_header = document.getElementById("login-header");
    let account = document.getElementById("account-header");
    if (getCookie('Client') == '') {
        account.classList.add("d-none");
        login_header.classList.remove("d-none");
    } else {
        login_header.classList.add("d-none");
        account.classList.remove("d-none");
        AddAnimationAccountHeader();
    }
}

/*-------------------------------------------------------------------------------------------
----------------------------------------- ABOUT ---------------------------------------------
--------------------------------------------------------------------------------------------*/
function AddAnimationTeamMember() {
    var TeamMember = document.getElementById("team-members");

    var MemberData = [
        { name: "Loane", pseudo: "Paprika", img1: "Loane.jpg", img2: "Paprika.png" },
        { name: "Oscar", pseudo: "Luxouille", img1: "Oscar.jpg", img2: "Luxouille.jpg" },
        { name: "Gurval", pseudo: "Gurval", img1: "Gurval.jpg", img2: "Gurval.jpg" },
        { name: "Allan", pseudo: "Trykeur", img1: "Allan.jpg", img2: "Trykeur.jpg" }
    ];

    function changeContent(imgElem, nameElem, img, name) {
        imgElem.src = `Images/Team/${img}`;
        nameElem.innerHTML = name;
    }

    if (TeamMember) {
        for (i = 0; i < TeamMember.children.length; i++) {
            let member = TeamMember.children[i];
            let imgElem = member.querySelector('img');
            let nameElem = member.querySelector('.card-body h3');
            let img1 = MemberData[i].img1;
            let img2 = MemberData[i].img2;
            let name = MemberData[i].name;
            let pseudo = MemberData[i].pseudo;
            member.addEventListener("mouseover", () => { changeContent(imgElem, nameElem, img2, pseudo) });
            member.addEventListener("mouseleave", () => { changeContent(imgElem, nameElem, img1, name) });
        }
    }
}

/*----------------------------------------------------------------------------------------------------
---------------------------------------------- HOME --------------------------------------------------
------------------------------------------------------------------------------------------------------*/
function SetMovieAttribute(attr1, attr2) {
    if (attr1 == undefined) {
        if (attr2 == undefined) {
            return "Inconnue"
        }
        return attr2
    } return attr1
}

function CreateStarsBoxRating(rating) {
    starsBox = document.createElement("div");
    for (let i = 0; i < Math.floor(rating); i++) { starsBox.innerHTML += `<i class='bi bi-star-fill text-warning'></i>`; }
    if (rating - Math.floor(rating) >= 0.5) {
        starsBox.innerHTML += `<i class='bi bi-star-half text-warning'></i>`
        for (let i = 0; i < 4 - Math.floor(rating); i++) { starsBox.innerHTML += `<i class='bi bi-star text-warning'></i>`; }
    } else {
        for (let i = 0; i < 5 - Math.floor(rating); i++) { starsBox.innerHTML += `<i class='bi bi-star text-warning'></i>`; }
    }
    return starsBox
}

function SetMovieModalDetails(IDMovie, title, rating, runtime, realeaseYear, genres, synopsis, poster, id_genre, watched) {
    document.getElementById('id_oeuvre-movie-details-modal').value = IDMovie;
    SetBookMarkIcon(document.getElementById('movie-details-modal-bookmark-icon'), watched)

    if (realeaseYear == undefined) { realeaseYear = "Inconnue" }

    Elem_title = document.getElementById("movie-details-modal-title");
    Elem_rating = document.getElementById("movie-details-modal-rating");
    Elem_runtime = document.getElementById("movie-details-modal-runtime");
    Elem_realeaseYear = document.getElementById("movie-details-modal-realeaseYear");
    Elem_genres = document.getElementById("movie-details-modal-genres");
    Elem_synopsis = document.getElementById("movie-details-modal-synopsis");
    Elem_poster = document.getElementById("movie-details-modal-poster");
    Elem_recommandation = document.getElementById("movie-details-modal-recommandation");
    var Elem_distribution = document.getElementById("movie-details-modal-distribution");
    var Elem_creator = document.getElementById("movie-details-modal-creator");


    Elem_creator.innerHTML = '';
    Elem_distribution.innerHTML = '';
    APIResquest(`/movie/id/${IDMovie}/artists`).then(data => {
        data[0].Artists.forEach(artist => {
            if (artist.profession == 'director') {
                Elem_creator.innerHTML += artist.primary_name
            } else {
                Elem_distribution.innerHTML += artist.primary_name + ", "
            }
        });
        Elem_distribution.innerHTML = Elem_distribution.innerHTML.slice(0, -2);
    });


    Elem_title.innerHTML = title;

    Elem_rating.innerHTML = '';
    Elem_rating.appendChild(CreateStarsBoxRating(rating));

    Elem_runtime.innerHTML = runtime;
    Elem_realeaseYear.innerHTML = realeaseYear;
    Elem_genres.innerHTML = genres;
    Elem_synopsis.innerHTML = synopsis;

    Elem_poster.style.backgroundImage = `url('${poster}')`;

    Elem_recommandation.innerHTML = '';

    let loader = CreateMovieLoader("Other users also watched", Elem_recommandation);

    if (getCookie('Profil') != '') {
        var data = APIResquest(`/recommandation/by/id_oeuvre/${IDMovie}/id_profil/${getCookie('Profil')}?limit=${LIMIT}`);
    } else {
        var data = APIResquest(`/recommandation/by/id_oeuvre/${IDMovie}/id_profil/null}?limit=${LIMIT}`);
    }
    let OtherViewers = false;
    data.then(data => {
        if (data.length > 0) {
            CreateMovieList(data, "Other users also watched", "movie-details-modal-recommandation", loader);
            OtherViewers = true;
        }
    });

    if (!OtherViewers) {
        let data = APIResquest(`/recommandation/by/genre/${id_genre}?limit=${LIMIT}`);
        data.then(data => { CreateMovieList(data, "Same categories", "movie-details-modal-recommandation", loader); });
    }
}

function CreateMovieCard(title, rating, src, genre, runtime) {
    // Creating the list element
    let elem_li = document.createElement("li");
    elem_li.setAttribute("class", "list-group-item");
    elem_li.setAttribute("data-bs-toggle", "modal");
    elem_li.setAttribute("data-bs-target", "#movie-details-modal");

    // Creating the image 
    let img = document.createElement("img");
    img.setAttribute("src", src);
    img.setAttribute("alt", "Affiche de film");
    img.setAttribute("class", "object-fit-cover");
    img.setAttribute("width", "200px");
    img.setAttribute("height", "200px");

    let collapse = document.createElement("div");
    collapse.setAttribute("class", "collapse-content collapse w-100 h-100 position-absolute top-0 bg-black bg-opacity-75");

    let card = document.createElement("div");
    card.setAttribute("class", "d-flex flex-column justify-content-between h-100");
    card.innerHTML += ` <div>
                            <h4>${title}</h4>
                            <p>${genre}</p>
                        </div>`;

    ratingBox = document.createElement("div");
    ratingBox.setAttribute("class", "d-flex justify-content-between");
    ratingBox.innerHTML += `${runtime} mn`;

    starsBox = CreateStarsBoxRating(rating);

    ratingBox.appendChild(starsBox);
    card.appendChild(ratingBox);
    collapse.appendChild(card);
    elem_li.appendChild(img);
    elem_li.appendChild(collapse);

    return elem_li
}

function CreateMovieList(data, title, ID, parent) {
    parent.innerHTML = `<h4>${title}</h4>`;

    var liste_ul = document.createElement("section");
    liste_ul.setAttribute("id", ID);
    liste_ul.setAttribute("class", "list-group-horizontal d-flex overflow-auto gap-2 p-2");

    data.forEach(movie => {
        GET_OMDb_data(movie.original_title).then(OMDb_data => {
            LISTE_GENRE = APIResquest(`/movie/id/${movie.id_oeuvre}?field=id_genre_list`);
            LISTE_GENRE.then(liste_genre => {
                let id_genre = liste_genre[0].id_genre_list[0];

                // let trailer_url = GetURLTrailer(OMDb_data.imdbID);

                let IDMovie = movie.id_oeuvre;
                let title = movie.original_title;
                let rating = SetMovieAttribute(movie.average_rating / 2, OMDb_data.imdbRating / 2);
                let runtime = movie.runtime_minutes;
                let realeaseYear = SetMovieAttribute(movie.realease_year, OMDb_data.Year);
                let genres = movie.genres;

                // RANDOM IMAGES
                // let poster = "https://picsum.photos/200/200?random="+Math.floor(Math.random() * 100);
                let poster = OMDb_data.Poster;
                if (poster == undefined || poster == "N/A") { poster = 'Images/SweetDonutLogo.png' }
                let synopsis = OMDb_data.Plot;

                watched = JSON.parse("[" + getCookie('Watched') + "]").includes(IDMovie);

                let elem_li = CreateMovieCard(title, rating, poster, genres, runtime)
                liste_ul.appendChild(elem_li);

                AddHoverEffect(elem_li);
                AddOpenModalOnClick(elem_li, IDMovie, title, rating, runtime, realeaseYear, genres, synopsis, poster, id_genre, watched);

            });
        });
    });

    parent.appendChild(liste_ul);
}

function CreateMovieLoader(title, parent = document.getElementsByTagName("main")[0]) {
    var section = document.createElement("section");
    section.innerHTML += `
        <h4>${title}</h4>
        <div class="spinner-border border-0" role="status">
            <img class="w-100" src="Images/donut_spin.png" alt="donut spin"/>
        </div>
        <span class="px-1">Loading ...</span>
    `;
    parent.appendChild(section);
    return section;
}

const HOVER_DELAY = 1;
let movieListEnterTimer, movieListLeaveTimer;

function AddHoverEffect(item) {
    item.addEventListener('mouseover', function () {
        clearTimeout(movieListLeaveTimer);
        let collapseContent = this.querySelector('.collapse-content');

        if (collapseContent != null) {
            movieListEnterTimer = setTimeout(function () {
                collapseContent.classList.remove('collapse');
            }, HOVER_DELAY);
        }
    });

    item.addEventListener('mouseleave', function () {
        clearTimeout(movieListEnterTimer);
        let collapseContent = this.querySelector('.collapse-content');

        if (collapseContent != null) {
            collapseContent.classList.add('collapse');
        }
    })
}

function AddOpenModalOnClick(item, IDMovie, title, rating, runtime, realeaseYear, genres, synopsis, poster, id_genre, watched) {
    item.addEventListener('click', function (e) {
        SetMovieModalDetails(IDMovie, title, rating, runtime, realeaseYear, genres, synopsis, poster, id_genre, watched)
    });
}


function SetBookMarkEventListener() {
    if (getCookie('Client') != '') {
        AddEventListenerBookmarkIcon_MovieRegistered();
    } else {
        let bookmarkIcon = document.getElementById('movie-details-modal-bookmark-icon');
        bookmarkIcon.addEventListener('click', function (e) { window.location.href = "login.html" });
    }
}

function SetBookMarkIcon(elem, fill) {
    if (fill) {
        elem.setAttribute("class", "bi bi-bookmark-check-fill fs-3")
    } else {
        elem.setAttribute("class", "bi bi-bookmark-check fs-3")
    }
}

function AddEventListenerBookmarkIcon_MovieRegistered() {
    let bookmarkIcon = document.getElementById('movie-details-modal-bookmark-icon');
    if (bookmarkIcon) {
        bookmarkIcon.addEventListener('click', function (e) {
            let id_oeuvre = parseInt(document.getElementById('id_oeuvre-movie-details-modal').value);

            fill = bookmarkIcon.classList.contains('bi-bookmark-check-fill')
            SetBookMarkIcon(bookmarkIcon, !fill)

            if (fill) {
                APIResquest_POST("/client/remove/movie", { 'id_client': getCookie('Client'), 'id_profil': getCookie('Profil'), 'id_oeuvre': id_oeuvre })
                movieList = JSON.parse("[" + getCookie('Watched') + "]").filter(function (id) { return id !== id_oeuvre })
                setCookie('Watched', movieList, 1);

                AddAnimationPopUpInformation("Deleting to list");
                setInterval(function () { window.location.href = window.location.href; }, 3000);

            } else {
                APIResquest_POST("/client/add/movie", { 'id_client': getCookie('Client'), 'id_profil': getCookie('Profil'), 'id_oeuvre': id_oeuvre })
                movieList = JSON.parse("[" + getCookie('Watched') + "]")
                movieList.push(id_oeuvre)
                setCookie('Watched', movieList, 1);

                AddAnimationPopUpInformation("Adding to list");
                setInterval(function () { window.location.href = window.location.href; }, 3000);
            }
        });
    }
}

/*----------------------------------------------------------------------------------------------------
----------------------------------------- LOAD FUNCTION ---------------------------------------------
------------------------------------------------------------------------------------------------------*/
function HomePageOnLoad() {
    if (getCookie('Client') != '') {
        let loader_1 = CreateMovieLoader("Recommended for you");
        data = APIResquest(`/old_recommandation/by/id_profil/${getCookie('Profil')}`);
        data.then(data => { CreateMovieList(data, "Recommended for you", "user-recommandation-movie-list-group", loader_1) });

        let loader_2 = CreateMovieLoader("Watch again");
        data = APIResquest(`/client/${getCookie('Client')}/get/movie?limit=${LIMIT}`);
        data.then(data => {
            if (data.length > 0) { CreateMovieList(data, "Watch again", "user-watch-movie-list-group", loader_2) }
        });
    }

    loader = CreateMovieLoader("Popular films");
    data = APIResquest(`/recommandation/TopPopularMovies?limit=${LIMIT}`);
    data.then(data => { CreateMovieList(data, "Popular films", "top-popular-movie-list-group", loader) });


    LISTE_GENRE = APIResquest(`/genres`);
    LISTE_GENRE.then(liste_genre => {
        liste_genre.forEach(genre => {
            let loader = CreateMovieLoader(genre.genre_name);
            let data = APIResquest(`/recommandation/by/genre/${genre.id_genre}?limit=${LIMIT}`);
            data.then(data => { CreateMovieList(data, genre.genre_name, `genre_${genre.id_genre}-movie-list-group`, loader); });
        });
    });
}



function LoginPageOnLoad() {
    var loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();

            let email = document.getElementById('email-input-login');
            let password = document.getElementById('password-input-login');
            let error = document.getElementById('input-error-login');
            let success = document.getElementById('input-success-login');
            let submitButton = loginForm.querySelector("button[type='submit']");


            if (email.value != "" && password.value != "") {
                APIResquest_POST("/login", { 'email': email.value, 'password': password.value }).then((response) => {

                    if (response.status == 200) {
                        submitButton.querySelector(".spinner-border").classList.remove('collapse');
                        submitButton.setAttribute('disabled', true);

                        error.classList.add('collapse');
                        success.classList.remove('collapse');

                        email.value = "";
                        password.value = "";

                        setCookie('Client', response.body['Client'], 1);
                        setCookie('Profil', response.body['Profil'], 1);
                        setCookie('Connected', true, 1);

                        APIResquest(`/client/${getCookie('Profil')}/get/movie?field=id_oeuvre`).then(WatchedMovies => {
                            movieList = []
                            WatchedMovies.forEach(movie => { movieList.push(movie.id_oeuvre) });
                            setCookie('Watched', movieList, 1);
                        });

                        setTimeout(() => { window.location.href = "home.html"; }, 2000);
                    }

                    if (response.status == 401) {
                        error.classList.remove('collapse');
                        success.classList.add('collapse');
                        password.value = "";
                    }

                });
            }
        });
    }
}



function RegisterPageOnLoad() {
    var registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", (e) => {
            e.preventDefault();

            let name = document.getElementById('name-input-register');
            let email = document.getElementById('email-input-register');
            let password = document.getElementById('password-input-register');
            let confirmPassword = document.getElementById('confirm-password-input-register');
            let terms = document.getElementById('terms-check-register');

            let error = document.getElementById('input-error-register');
            let success = document.getElementById('input-success-register');
            let submitButton = registerForm.querySelector("button[type='submit']");


            if (name.value != "" && email.value != "" && password.value != "" && confirmPassword.value != "") {
                if (password.value == confirmPassword.value) {
                    if (terms.checked) {
                        APIResquest_POST("/register", { 'name': name.value, 'email': email.value, 'password': password.value }).then((response) => {

                            if (response.status == 200) {
                                submitButton.querySelector(".spinner-border").classList.remove('collapse');
                                submitButton.setAttribute('disabled', true);

                                error.classList.add('collapse');
                                success.classList.remove('collapse');

                                name.value = "";
                                email.value = "";
                                setCookie('Registered', true, 1);

                                setTimeout(() => { window.location.href = "login.html"; }, 3000);
                            }

                            if (response.status == 401) {
                                error.classList.remove('collapse');
                                error.innerHTML = "email is already used"
                            }

                            password.value = "";
                            confirmPassword.value = "";

                        });
                    } else {
                        error.classList.remove('collapse');
                        error.innerHTML = "You must accept the terms and conditions"
                    }

                } else {
                    error.classList.remove('collapse');
                    error.innerHTML = "Password and confirm password do not match"
                }
            }
        });
    }
}




/*----------------------------------------------------------------------------------------------------
----------------------------------------- MAIN EXECUTION ---------------------------------------------
------------------------------------------------------------------------------------------------------*/
window.addEventListener('load', function () {
    /*-------------------- HEADER --------------------*/
    SetDropdownMenuHeader();            // Set Categories in dropdown menu
    SetAccountHeader();                 // Set the account header (Connected / disconnected) 
    AddAnimationSearchLinkHeader();     // Add animation in search button (arrow)
    SearchBar();


    /*-------------------- INIT PAGES --------------------*/
    if (this.document.title == "Sweet donuts - Home") {
        HomePageOnLoad();
        SetBookMarkEventListener();
    }

    if (this.document.title == "Sweet donuts - About") { AddAnimationTeamMember() }

    if (this.document.title == "Sweet donuts - Login") { LoginPageOnLoad() }

    if (this.document.title == "Sweet donuts - Register") { RegisterPageOnLoad() }

    if (this.document.title == "Sweet donuts - Advanced Search") { SetBookMarkEventListener(); }

    /*-------------------- ADD POP UP --------------------*/
    if (getCookie('Connected') != '') {
        AddAnimationPopUpInformation("Connected", false);
        resetCookie('Connected');
    }

    if (getCookie('Registered') != '') {
        AddAnimationPopUpInformation("Created account", false);
        resetCookie('Registered');
    }

});
