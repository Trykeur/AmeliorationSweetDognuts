function SetDropdownGenreSearch(){
    let dropdownGenre = $('#genre-input-search');

    dropdownGenre.select2({
        theme: "bootstrap-5",
        width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
        placeholder: $(this).data('placeholder'),
        closeOnSelect: false,
        allowClear: true,
    });

    LISTE_GENRE = APIResquest(`/genres?limit=${LIMIT}`);
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



function etoileListener() {
    function colorEtoileHover(etoile){
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
    function etoileOut(){
        for (let i = 0; i < etoiles.length; i++) {
            if(etoiles[i].getAttribute('data-value') == document.getElementById('etoile-input-search').value){
                colorEtoileHover(etoiles[i]);
            }
        }
    }

    var etoiles = document.getElementsByClassName("etoile");

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

function search(){
    var searchForm = document.getElementById("search-form");
    if(searchForm){
        searchForm.addEventListener("submit", (e) => {
            let sectionSearch = document.getElementById('resultSearch');

            sectionSearch.innerHTML = "";

            e.preventDefault();
        
            let searchBar = document.getElementById('bar-search');
            let genre = document.getElementById('genre-input-search');
            let note = document.getElementById('etoile-input-search');
            let dureeMIN = document.getElementById('duree-input-search');
            let dureeMAX = document.getElementById('duree2-input-search');
            let dateMIN = document.getElementById('date-input-search');
            let dateMAX = document.getElementById('date2-input-search');
            //let submitButton = searchForm.querySelector("button[type='submit']");

            let listeGenre = "";

            for (let option of genre.options) {
                if (option.selected) {
                    listeGenre = listeGenre + `&listeGenre=${option.value}`;
                }
            }

            let request = `/Advancedsearch?title=${searchBar.value}&runtimeMIN=${dureeMIN.value}&runtimeMAX=${dureeMAX.value}&ratingMIN=${note.value}&yearMIN=${dateMIN.value}&yearMAX=${dateMAX.value}${listeGenre}`;//&listeGenre=5&listeGenre=17
            
            data = APIResquest(request);
            data.then(data => {
                if(data.length > 0){
                    CreateMovieList(data,"Résultat de recherche","search-result-movie-list-group",document.getElementById('resultSearch'));
                }
                else{
                    let noResSearch = document.createElement("h2");
                    noResSearch.innerHTML = 'Aucun résultat pour votre recherche !';
                    sectionSearch.appendChild(noResSearch);
                }
            });
        });
    }
}

window.addEventListener('load', function () {

    SetDropdownGenreSearch();
    etoileListener();
    yearPicker();
    search();

});