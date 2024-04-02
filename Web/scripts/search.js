function SetDropdownGenreSearch(){
    // mise en place du dropdown
    let dropdownGenre = $('#genre-input-search');
    dropdownGenre.select2({ 
        theme: "bootstrap-5",
        width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
        placeholder: $(this).data('placeholder'),
        closeOnSelect: false,
        allowClear: true,
        scrollAfterSelect : false,
    });

    // création dynamique des options de genre 
    LISTE_GENRE = APIResquest(`/genres`);
    LISTE_GENRE.then(liste_genre => {
        liste_genre.forEach(genre => {
            let opt = document.createElement("option");
            opt.value = genre.id_genre;
            opt.innerHTML = genre.genre_name;
            dropdownGenre.append(opt);
        });
    });

}

function yearPicker(){
    $(document).ready(function(){
        $("#date-input-search").datepicker({
            format: "yyyy",
            viewMode: "years", 
            minViewMode: "years",
            autoclose:true
        });   
        $("#date2-input-search").datepicker({
            format: "yyyy",
            viewMode: "years", 
            minViewMode: "years",
            autoclose:true
        });   
    })
}

var etoiles = document.getElementsByClassName("etoile");
function colorEtoileHover(etoile){ // colorie les étoiles en fonction du placement de la souris
    var stop = etoile.getAttribute('data-value');
    for (let i = 0; i < etoiles.length; i++) {
        if(etoiles[i].getAttribute('data-value')>stop){
            etoiles[i].classList.replace('bi-star-fill','bi-star');
        }
        else{
            etoiles[i].classList.replace('bi-star','bi-star-fill');
        }
    }
}
function etoileOut(){ // colorie les étoiles en fonction de la valeur donnée
    for (let i = 0; i < etoiles.length; i++) {
        if(etoiles[i].getAttribute('data-value') == document.getElementById('etoile-input-search').value){
            colorEtoileHover(etoiles[i]);
        }
    }
}
function etoileListener() {

    var etoile0 = etoiles[0]
    etoile0.addEventListener("mouseover", function(){colorEtoileHover(etoile0);});
    etoile0.addEventListener("click", function(){document.getElementById('etoile-input-search').value = (etoile0.getAttribute('data-value'));});    
    var etoile1 = etoiles[1]
    etoile1.addEventListener("mouseover", function(){colorEtoileHover(etoile1)});
    etoile1.addEventListener("click", function(){document.getElementById('etoile-input-search').value = (etoile1.getAttribute('data-value'));});    
    var etoile2 = etoiles[2]
    etoile2.addEventListener("mouseover", function(){colorEtoileHover(etoile2)});
    etoile2.addEventListener("click", function(){document.getElementById('etoile-input-search').value = (etoile2.getAttribute('data-value'));});    
    var etoile3 = etoiles[3]
    etoile3.addEventListener("mouseover", function(){colorEtoileHover(etoile3)});
    etoile3.addEventListener("click", function(){document.getElementById('etoile-input-search').value = (etoile3.getAttribute('data-value'));});    
    var etoile4 = etoiles[4]
    etoile4.addEventListener("mouseover", function(){colorEtoileHover(etoile4)});
    etoile4.addEventListener("click", function(){document.getElementById('etoile-input-search').value = (etoile4.getAttribute('data-value'));});    

    var bloc_etoile = document.getElementsByClassName("bloc-etoile")[0];
    bloc_etoile.addEventListener("mouseout", etoileOut);

}

function search(){ // système de recherche
    var searchForm = document.getElementById("search-form");
    if(searchForm){
        searchForm.addEventListener("submit", (e) => {

            e.preventDefault();
        
            // Récupération des input du form
            let searchBar = document.getElementById('bar-search');
            let genre = document.getElementById('genre-input-search');
            let note = document.getElementById('etoile-input-search');
            let dureeMIN = document.getElementById('duree-input-search');
            let dureeMAX = document.getElementById('duree2-input-search');
            let dateMIN = document.getElementById('date-input-search');
            let dateMAX = document.getElementById('date2-input-search');

            // formatage genres
            let listeGenre = "";
            for (let option of genre.options) {
                if (option.selected) {
                    listeGenre = listeGenre + `&listeGenre=${option.value}`;
                }
            }

            var error = document.getElementById("input-error-search");
            if(dateMIN.value> dateMAX.value) {
                error.innerHTML = "Minimum date must be less than maximum date !";
                error.classList.remove('collapse');
            }
            else if(dureeMIN.value> dureeMAX.value){
                error.innerHTML = "Minimum runtime must be less than maximum runtime !";
                error.classList.remove('collapse');
            }
            else{
                //error.classList.remove('collapse')
                error.classList.add('collapse');
                // Suppression du résultat de la recherche précédente
                let sectionSearch = document.getElementById('resultSearch');
                sectionSearch.innerHTML = "";

                // requête API
                let request = `/Advancedsearch?title=${searchBar.value}&runtimeMIN=${dureeMIN.value}&runtimeMAX=${dureeMAX.value}&ratingMIN=${note.value}&yearMIN=${dateMIN.value}&yearMAX=${dateMAX.value}${listeGenre}`;
                data = APIResquest(request);

                // Affichage des résultats de la recherche
                data.then(data => {
                    if(data.length > 0){
                        CreateMovieList(data,"Search result","search-result-movie-list-group",document.getElementById('resultSearch'));
                    }
                    else{
                        let noResSearch = document.createElement("h2");
                        noResSearch.innerHTML = 'No results found !';
                        sectionSearch.appendChild(noResSearch);
                    }
                });
            }

            
        });
    }

    // Réinitialisation des filtres
    var btnReset = document.getElementById("btn-reset");
    btnReset.addEventListener("click", function() {
        // etoiles
        document.getElementById('etoile-input-search').value = "06";
        etoileOut();

        // genres
        $('#genre-input-search').val(null).trigger('change');
    });
}

window.addEventListener('load', function () {

    SetDropdownGenreSearch();
    etoileListener();
    yearPicker();
    search();

    // Search auto if URL contains ?...

});