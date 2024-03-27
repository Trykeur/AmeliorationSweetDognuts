
# **Les donuts sucrées - Guide d'installation**

## Base de données
La base de donnée fonctionne sous PostresSQL.
Avant la mise en place, il est necessaire d'avoir au préalable une base de donnée fonctionnel sous PostresSQL.


Une fois votre base de donnée prête à être utilisé, vous avez 2 méthode possible pour implémenter et peupler votre base :
- [<u>Automatique</u> : Utiliser la fichier de BackUp](#mise-en-place-automatique) 
- [<u>Manuelle</u> : Executer les scripts SQL de création et peuplement](#mise-en-place-manuelle)

(<u>Attention</u> : La méthode manuelle necessite plus de temps et ressources)

Vous retrouverez les scripts necessaire dans le [dossier Implementation sur Github](https://github.com/8Paprika5/API_RecommandationSys/tree/main/Implementation).


### Mise en place (Automatique)
Pour mettre en place automatiquement la base de données, un fichier de backUp est disponible sur [ici](https://drive.google.com/file/d/1qumphe1AGi2yokk4-T1NRhx8MqgGMXOz/view?usp=drive_link) : 
La backup est à utiliser dans une base vièrge. Elle permet de créer toutes les tables, relations et contraintes necessaires, ainsi que peupler la base de films et artists. (+ de 500 enregistrements)
-- TODO : nombre d'enregistrements


### Mise en place (Manuelle)
Pour mettre en place manuellement la base de données, commencez par executer le script _"scriptSQLSAE.sql"_. Ce scripts permet de créer toutes les tables, relations et contraintes necessaires.

Afin de peupler la base, vous aurez besoin de récuperer les fichiers CSV suivants récupérable sur GIT: 
- CSV 1
- CSV 2.
-- TODO : noms et emplacement des CSV.
-- TODO : vérifier les scripts SQL et l'ordre.

Vous pourrez en suite executer le script _"Peuplement.sql"_. Ce script permet de remplir la base en utilisant les fichiers CSV téléchargé précèdemmant.



## Elastic search

## API
L'API Donuts sucrées fonctionne sous python avec le module FastApi. Voici les étapes à suivre pour créer un environnement virtuel :

---

Liens utils :
- [Documentation FastApi](https://fastapi.tiangolo.com/)
- [Documentation Conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html)
- [Documentation Pyvenv](https://docs.python.org/fr/3/library/venv.html)

### Initialiser un environnement virtuel (Windows)
<u>Avec conda :</u>
```sh
PS> conda create --name SweetDonuts
PS> conda activate SweetDonuts
(SweetDonuts) PS>
```

<u>Avec pyvenv :</u>
```sh
PS> python -m venv SweetDonuts
PS> venv\Scripts\activate
(SweetDonuts) PS>
```

Une fois, l'environnement initialisé et lancé, copiez-y les fichiers du [dossier API sur Github](https://github.com/8Paprika5/API_RecommandationSys/tree/main/API). Téléchargez ensuite les dépendances nécessaires.

```sh
(SweetDonuts) PS> pip install -r requirements.txt
```

Votre environnement est prêt ! Vous pouvez exécuter le fichier python api.py !
```sh
(SweetDonuts) PS> python api.py
-- Database connexion ...
-- ElasticSearch connexion ...
-- Data initialisation ...
-- Data formating ...
-- API starting ...
INFO:     Started server process [9704]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Pour quitter l'environnement virtuel : 
<u>Avec conda :</u>
```sh
(SweetDonuts) PS> conda deactivate
```

<u>Avec pyvenv :</u>
```sh
(SweetDonuts) PS> deactivate
```



### Initialiser un environnement virtuel (Linux & MacOs)
<u>Avec conda :</u>

```sh
$ conda create --name SweetDonuts
$ conda activate SweetDonuts
(SweetDonuts) $
```

<u>Avec pyvenv :</u>

```sh
$ python -m venv SweetDonuts
$ source SweetDonuts/bin/activate
(SweetDonuts) $
```

Une fois, l'environnement initialisé et lancé, copiez-y les fichiers du [dossier API sur Github](https://github.com/8Paprika5/API_RecommandationSys/tree/main/API). Téléchargez ensuite les dépendances nécessaires.

```sh
(SweetDonuts) $ pip install -r requirements.txt
```

Votre environnement est prêt ! Vous pouvez exécuter le fichier python api.py !
```sh
(SweetDonuts) $ python api.py
-- Database connexion ...
-- ElasticSearch connexion ...
-- Data initialisation ...
-- Data formating ...
-- API starting ...
INFO:     Started server process [9704]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Pour quitter l'environnement virtuel : 
<u>Avec conda :</u>

```sh
(SweetDonuts) $ conda deactivate
```

<u>Avec pyvenv :</u>

```sh
(SweetDonuts) $ deactivate
```








## Aide Python
### Générer la liste des dépendances 
La liste des dépendances (fichier requirements.txt) permet d'installer en une seule fois tous les paquets d'installation nécessaires au bon fonctionnement de l'application.

Il est nécessaire au préalable de se situer dans un environnement virtuel python.

Pour générer la liste des dépendances dans un fichier 'requirements.txt', vous pouvez exécuter la commande suivante (Window/Linux/MacOS):

```sh
(SweetDonuts) $ pip freeze > requirements.txt
```

Pour installer les modules nécessaires, éxécutez le script suivant
- Pour windows : lancer installModulesWin
- Pour Linux/Mac : lancer installModuleLinux