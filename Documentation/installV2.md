# **Les donuts sucrées - Documentation**


## Base de données
La base de donnée fonctionne sous PostresSQL.
Avant la mise en place, il est necessaire d'avoir au préalable une base de donnée fonctionnel sous PostresSQL.


Une fois votre base de donnée prête à être utilisé, vous avez 2 méthode possible pour implémenter et peupler votre base :
- [<u>Automatique</u> : Utiliser la fichier de BackUp](#mise-en-place-automatique) (le fichier a été refait par Allan et le nouveau fichier BackupV3 fonctionne correctement)

- [<u>Manuelle</u> : Executer les scripts SQL de création et peuplement](#mise-en-place-manuelle)

(<u>Attention</u> : La méthode manuelle necessite plus de temps et ressources)

Vous retrouverez les scripts necessaire dans le [dossier Implementation sur Github](https://github.com/8Paprika5/API_RecommandationSys/tree/main/Implementation).


### Mise en place (Automatique)
Pour mettre en place automatiquement la base de données, un fichier de backUp est disponible sur [ici](https://drive.google.com/file/d/1qumphe1AGi2yokk4-T1NRhx8MqgGMXOz/view?usp=drive_link) : 
La backup est à utiliser dans une base vièrge sur un environnement Windows, Linux ou MacOS. 

Si vous avez un problème de schéma avec le précédent vous pouvez utilisez le dumpBackup.sql à jouer sur le terminal du docker contenant le container de PostgreSQL. Vous retrouverez le fichier [ici](https://drive.google.com/file/d/12OorDp8ui2T7JNR7lVPGEmdBmXhp5heQ/view?usp=drive_link). 

Il faut dans un premier temps copier le fichier dans le docker : 

```sh
docker cp /chemin/vers/le/fichier/dumpBackup.sql mon_conteneur:/scripts/
```

Une fois le fichier dans le docker, il faut lancer la commande :

```sh
psql -U postgres -d my_database -a -f /chemin/vers/le/dumpBackup.sql
```

Ce backup permet de créer toutes les tables, relations et contraintes necessaires, ainsi que peupler la base de films et artists. (+ de 500 enregistrements)


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

Liens utiles :
- [Documentation FastApi](https://fastapi.tiangolo.com/)
- [Documentation Conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html)
- [Documentation Pyvenv](https://docs.python.org/fr/3/library/venv.html)

### Lancer les différents outils (Windows)

Nous avons simplifié l'installation et le lancement des différents outils.

Tout d'abord, vous devez lancer le script "installModulesWin.bat" qui se trouve dans le dossier "installModules" dans "Implementation".

Ce fichier sert à installer directement sur la machine tous les modules nécessaires au projet.

Ensuite, une fois cela fait, il faut lancer le script "lancementAppWindows.bat" qui va exécuter ElasticSearch et l'API en même temps.


### Initialiser le projet (MacOs)

Commencez par lier un container de docker avec le SGBD utilisé.

Je conseil ici d'utiliser DBeaver qui permet de créer une connexion simple. Utilisez ce script pour les informations de connexion suivante : 

```sh
version: '3.9'
services:
  db:
    image: postgres
    container_name: docker_postgres
    restart: always
    volumes:
      - cours-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=
      - POSTGRES_USER=
    ports:
      - 8765:5432
    networks:
      - cours-dev


networks:
  cours-dev:

volumes:
  cours-db-data:

```

Enregistrez le fichier avec le nom "docker-compose.yml" et vous devez le lancer avec la commande suivante  :

```sh
docker-compose up -d
```


Une fois la connexion établie, si le fichier BackUpV3 ne fonctionne pas, faire la 2ème partie de la mise en place automatique de la base de données avec le dumpBackup.sql


Une fois, l'environnement initialiser, modifiez le début du fichier de connexion "connect.py" avec les informations suivantes :
```sh
username=''
password=''
host='localhost'
database= ''
schema = ""
port = '8765'  # Spécifiez le port ici

# Connexion SQL
print("-- Database connexion ...")
engine = sql.create_engine(f'postgresql://{username}:{password}@{host}:8765/{database}')
```

<b>Attention les informations "username", "password" et "database" sont à renseigner en fonction des informations du fichier docker-compose.yml</b>


Avant de lancer l'environnement, il faut lancer ElasticSearch avec cette commande : 

```sh
docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.7.0
```



Votre environnement est prêt ! Vous pouvez exécuter le fichier python api.py !
```sh
$ python api.py
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

S'il y a des problèmes d'importation, faire toutes les importations des différents modules obligatoires pour le projet et relancer à chaque fois le fichier api.py.



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
