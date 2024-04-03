# **Les donuts sucrées - Documentation**


## Base de données
Le SGBD que nous avons choisi d'utiliser est PostegreSQL.
La base de données que nous possédons a été importée à partir de la base d'un site Web nommé IMDB.
Possédant des centaines de milliers de films, certaines tables comptent plusieurs millions de lignes.
 
La base de données possède en tout douze tables au nom explicite: _artist, _client, _episode, _genre, _movie, _oeuvre, _oeuvre_artist, _oeuvre_genre, _profil, _profil_oeuvre, _saison, _serie.


Elle a à la base été importée grâce aux fichiers .tsv fourni par IMDB disponible sur cette page: https://datasets.imdbws.com/ , à l'exception de la table profil qui elle doit être généré manuellement, ou à l'aide d'un script de génération aléatoire comme nous l'avons fait.
L'instanciation de la base de données peut être réalisé à partir du fichier scriptSQLSAE.sql dans le dossier implémentation.
Cependant, la manière la plus simple de l'implémenter est de se servir de la backup nommée BackupV3, utilisable sur pgAdmin4. A noter que pour pouvoir utiliser la fonction restore de pgAdmin4 et d'utiliser la backup, il faudra préciser à pgAdmin4 l'emplacement de l'exécutable de PostgreSQL dans les préférences.




## Système de recommandations
Le système de recommandation par ACM à été créé en deux versions. Une première version dans laquelle la gestion des données est faite avec SQL et une seconde dans laquelle la gestion des données est faite par des Dataframe Panda préchargés. A l'origine faite pour économiser des ressources à l'aide de données chargées une fois seulement par l'API, cette seconde a finalement révélé des performances déplorables, dû au fait que Python est un langage très lent, non adapté à traiter des centaines de milliers de lignes de données. Pour cette raison, l'ancienne version est actuellement d'usage.


Le système est réparti dans trois fichiers:
- old_fonction_recommandation_ACM.py, old_profil.py, old_fonctions.py pour la première version
- Recommandation.py, Profil.py, MathFunction.py pour la seconde version


- Le fichier principal contient la fonction de recommandation de contenu à laquelle on soumet un id de profil utilisateur, grâce auquel elle va renvoyer une liste de recommandations sous forme d'un tableau d'Id de films.
- Le fichier de profil contient la classe Profil, représentant le profil d'un utilisateur, dans laquelle de nombreuses requêtes et pré-traitements sont faits.
- Le fichier de fonctions contient quelques fonctions mathématiques ainsi qu'un moteur de requêtes SQL pour la première version. Ce fichier est le plus anecdotique des trois, il est court et très fonctionnel et donc n'attirera pas nécessairement votre attention.


### Principe de l'algorithme
Le principe de l'algorithme n'est pas très complexe, bien que ce dernier soit très étendu.
L'algorithme part d'un postulat de base: Les informations les plus pertinentes dont nous disposons pour recommander des films sont les artistes (acteurs, réalisateurs, scénaristes, ect...) qui y participent.


Les artistes sont notés en fonction de la moyenne des scores de désirabilité obtenus par les films dans lesquels ils ont joués.
A noter que le score de désirabilité des films est calculé à partir d'une fonction logée dans le fichier de fonctions. La formule de la fonction à laquelle on soumet la note est censée augmenter de façon exponentielle la valeur des films les mieux notés et de baisser drastiquement ceux possédant des notes médiocres. A noter que si l'utilisateur n'a pas conféré de note à un film qu'il a regardé, une note par défaut de 6 lui est attribuée dans l'algorithme.
Tous ces pré-traitement sont effectués dans le fichier de Profil.


A l'aide de ces données, comprenant les films sélectionnés, les artistes associés, et leur genre, l'algorithme va réaliser une Analyse en Composantes Multiples pondérée par les scores de désirabilité des films participant dans ces dernières. Ainsi, les éléments qui ont la plus petite distance (dans le graphique de l'ACM) avec les films les mieux notés arriveront en tête du classement, qui dans le cadre de cette fonction a été limité à dix entrées.


### Fonctionnement du coeur de l'algorithme de recommandation par ACM
Pour pouvoir être effectuée, l'ACM opère sur un Dataframe créé tout le long du script. Chaque ligne du DataFrame correspond à un film à analyser.
La première partie du script a pour rôle de compter le nombre maximal de colonnes que peut avoir chaque type d'artiste et de colonnes de genre qu'un film peut contenir. Par exemple, si un film contient le plus grand nombre de réalisateurs, mettons quatre, alors le DataFrame contiendra les colonnes Réalisateur 1, Réalisateur 2, Réalisateur 3 et Réalisateur 4. Pour la majorité des films qui ne contiennent qu'un ou deux réalisateurs, les colonnes inutiles seront remplies par un None. Il en va de même pour le nombre de colonnes de genre.
La deuxième partie du script a pour fonction de remplir ce DataFrame avec les données à notre disposition.
La troisième et dernière partie a pour fonction de réaliser l'ACM et de classer les Film de le tableau mis à disposition. Les films seront triés entre ceux déjà visionnés, et ceux qui ne le sont pas. Les premiers serviront grâce à leur score de désirabilité d'étalon pour les second. Les films non regardés ayant la distance la plus courte avec les films déjà regardés sont propulsés en haut du classement. La distance en question sera pondérée de manière inversement proportionnelle au score de désirabilité des films déjà vus. Ainsi, les films les moins bien notés seront artificiellement éloignés des films en cours d'évaluation.


Certaines erreurs dû au cache Python pouvant survenir de manière fortuites, nécessitant juste la relance de la fonction, la fonction de recommandation est elle-même introduite dans une autre fonction qui a pour but de la relancer au cas où une erreur fortuite se produirait. Si jamais une erreur se produit quatre fois (ce qui est très peu probable), la fonction arrête de relancer la fonction de recommandation et considère cela comme un blocage.



## API
L'API Donuts sucrée fonctionne sous python avec le module FastApi ([Documentation FastApi](https://fastapi.tiangolo.com/)).C'est elle qui permet de faire le lien entre la base de donnée et le site web. Elle est lancé en local grâce au module uvicorn (http://127.0.0.1:8000/).

Les fonctionnalitées de l'API sont divisées en plusieurs parties :
- [les clients](#api---)
- [les films](#api---films)
- [les artistes](#api---Artistes)
- [les recommandations](#api---Recommandations)
- [la recherche Elastic-search](#api---elastic-search)


### API - Clients
---
```POST``` <u>/login</u> : Permet au clients de se connecter avec leur compte.
> ```POST PARAMETRES``` : email, password

> ```HTTP_200_OK``` Renvoie les identifiants du client et du premier profil.

> ```HTTP_400_BAD_REQUEST```S'il manque l'email et/ou le mot de passe.

> ```HTTP_401_UNAUTHORIZED``` Si le login et mot de passe ne correspondent pas avec un compte client.

> ```HTTP_404_NOT_FOUND``` Si aucun client n'est enregistré.

---
```POST``` <u>/register</u> : Permet aux internautes de se créer un nouveau compte.

> ```POST PARAMETRES``` : name, email, password

> ```HTTP_200_OK``` Si le compte a bien été créé.

> ```HTTP_400_BAD_REQUEST``` S'il manque un champ ou plusieurs (nom, email, mot de passe).

> ```HTTP_401_UNAUTHORIZED``` Si l'email est déjà utilisé.



---
```POST``` <u>/client/add/movie</u> : Permet d'ajouter un film à la liste de films d'un profil existant

> ```POST PARAMETRES``` : id_client, id_profil, id_oeuvre

> ```HTTP_200_OK``` Si le film a bien été ajouté

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant du profil ou du film est invalide (nombre entier positif). Si le film est déja enregistré.

> ```HTTP_401_UNAUTHORIZED``` Si l'identifiant du profil ou du film est inexistant.



---
```POST``` <u>/client/remove/movie</u> : Permet de supprimer un film de la liste de films d'un profil existant.

> ```POST PARAMETRES``` : id_client, id_profil, id_oeuvre

> ```HTTP_200_OK``` Si le film a bien été supprimé.

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant du profil ou du film est invalide (nombre entier positif). Si le film n'est pas déjà enregistré.

> ```HTTP_401_UNAUTHORIZED``` Si l'identifiant du profil ou du film est inexistant.



---
```GET``` <u>/client/*{id_profil}*/get/movie</u> : Permet de récupérer tous les films enregistrés sur un profil.

> ```GET PARAMETRES``` : id_profil, id_profil, id_oeuvre

> ```CHAMPS OPTIONNELS``` : field, limit

> ```HTTP_200_OK``` Renvoie la liste des films enregistrés.

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant du profil ou du film est invalide (nombre entier positif).

> ```HTTP_404_NOT_FOUND``` Si aucun client n'est enregistré. Si aucun film n'est enregistré pour ce profil


### API - Films
---
```GET``` <u>/movie</u> : Permet de récupérer tous les films.

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` Renvoie la liste des films.

> ```HTTP_400_BAD_REQUEST``` Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

> ```HTTP_404_NOT_FOUND```Si aucun film n'est enregistré.


---
```GET``` <u>/movie/id/{id_oeuvre}</u> : Permet de récupérer un film avec son identifiant.

> ```GET PARAMETRES``` : id_oeuvre.

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` Renvoie les informations du film.

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant est invalide (nombre entier positif). Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

> ```HTTP_404_NOT_FOUND``` Si aucun film n'est enregistré à cet identifiant.


---
```GET``` <u>/movie/id/{id_oeuvre}/artists</u> : Permet de récupérer un film avec son identifiant ainsi que ces artistes associés.

> ```GET PARAMETRES``` : id_oeuvre

> ```HTTP_200_OK``` Renvoie les informations du film et ses artistes

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant est invalide (nombre entier positif). Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

> ```HTTP_404_NOT_FOUND``` Si aucun film n'est enregistré à cet identifiant.


---
```GET``` <u>/genres</u> : Permet de récuperer tous les genres.

> ```CHAMPS OPTIONNELS``` : limit.

> ```HTTP_200_OK``` Renvoie la liste des genres (trié par nombre de films (décroissant)).

> ```HTTP_400_BAD_REQUEST``` Si un champ optionnel est invalide (limit : nombre entier positif).

> ```HTTP_404_NOT_FOUND```Si aucun genres n'est enregistré.

### API - Artistes
---
```GET``` <u>/artist</u> : Permet de récupérer tous les artistes.

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` Renvoie la liste des artistes.

> ```HTTP_400_BAD_REQUEST``` Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

> ```HTTP_404_NOT_FOUND```Si aucun artiste n'est enregistré.


---
```GET``` <u>/artist/id/{id_artist}</u> : Permet de récupérer un artist avec son identifiant.

> ```GET PARAMETRES``` : id_artist

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` Renvoie les informations de l'artiste.

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant est invalide (nombre entier positif). Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

> ```HTTP_404_NOT_FOUND``` Si aucun artiste n'est enregistré à cet identifiant.

---
```GET``` <u>/artist/id/{id_artist}/movies</u> : : Permet de récupérer un artiste avec son identifiant ainsi que ces films associés.

> ```GET PARAMETRES``` : id_artist

> ```HTTP_200_OK``` Renvoie les informations de l'artiste et ses films

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant est invalide (nombre entier positif).

> ```HTTP_404_NOT_FOUND``` Si aucun artiste n'est enregistré à cet identifiant.


### API - Recommandations
---
```GET``` <u>/recommandation/by/id_oeuvre/*{id_oeuvre}*/id_profil/*{id_profil}*</u> : Permet de recommander une liste de film à partir d'un seul film. Système user-based : le système propose des films aimé par d'autres utilisateurs qui ont également aimé le film renseigné (id_oeuvre).

> ```GET PARAMETRES``` : id_oeuvre, id_profil (si l'utilisateur est connecté, l'id_profil est renseigné afin d'éviter de proposer les films qu'il à déjà regardé).

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` Renvoie une liste de films aimé par d'autres utilisateurs

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant est invalide (nombre entier positif). Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

> ```HTTP_404_NOT_FOUND``` Si aucun film n'est enregistré à cet identifiant.



---
```GET``` <u>/old_recommandation/by/id_profil/*{id_profil}*</u> : Permet de recommander une liste de film à partir de la liste de films enregistré sur un profil.

> ```GET PARAMETRES``` : id_profil.

> ```HTTP_200_OK``` Renvoie une liste de films recommandés

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant est invalide (nombre entier positif).

> ```HTTP_404_NOT_FOUND``` Si aucun film n'est enregistré à cet identifiant.



---
```GET``` <u>/recommandation/nextMovie/{movieID}</u> : Permet de recherche les suite d'un film donnée (ElasticSearch).

> ```GET PARAMETRES``` : movieID.

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` Renvoie une liste de films

> ```HTTP_400_BAD_REQUEST``` Si l'identifiant est invalide (nombre entier positif). Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).



---
```GET``` <u>/recommandation/by/genre/{id_genre}</u> : Permet de recommander une liste de film à partir d'un genre donnée. 

> ```GET PARAMETRES``` : id_genre.

> ```CHAMPS OPTIONNELS``` : limit.

> ```HTTP_200_OK```Renvoie une liste de films appartenant à ce genre (trié par nombre de votes (popularité))

> ```HTTP_400_BAD_REQUEST```Si l'identifiant est invalide (nombre entier positif). Si un champ optionnel est invalide (limit : nombre entier positif).

> ```HTTP_404_NOT_FOUND``` Si aucun genre n'est enregistré. Si aucun film n'est enregistré.


### API - Statistiques

---
```GET``` <u> /recommandation/TopRatedMovies</u> : Permet de faire un classement de films selon leur note moyenne puis leur nombre de votes.

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` renvoie la liste des films les mieux notés.

> ```HTTP_400_BAD_REQUEST``` Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

---
```GET``` <u> /recommandation/TopPopularMovies</u> : Permet de faire un classement de films selon leur nombre de votes .

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` renvoie la liste des films les plus populaires.

> ```HTTP_400_BAD_REQUEST``` Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).

---
```GET``` <u> /recommandation/TopYears</u> Permet de faire un classement des films les mieux notées sur une période de 10 ans. Un partitionnement est effectuer pour selectionner la période la plus pertinante (basée sur le nombre de film et les notes moyennes).

> ```CHAMPS OPTIONNELS``` : field, limit.

> ```HTTP_200_OK``` renvoie une liste de films les mieux notées sur une période de 10 ans.

> ```HTTP_400_BAD_REQUEST``` Si un champ optionnel est invalide (limit : nombre entier positif et field doit être un/des champs existant(s)).: 





### API - Elastic search
---
```GET``` <u>/Advancedsearch</u> : permet d'effectuer une recherche de film selon certains critère (champs optionnels). (ElasticSearch)

> ```CHAMPS OPTIONNELS``` : title, regex, runtimeMIN, runtimeMAX, ratingMIN, ratingMAX, yearMIN, yearMAX, listeGenre, field, limit.

> ```HTTP_200_OK``` Renvoie une liste de films (résulat de la recherche)

> ```HTTP_400_BAD_REQUEST```Si un champ optionnel est invalide.








