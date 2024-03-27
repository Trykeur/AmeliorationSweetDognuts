/*----------------------------------------------------------------------------------------------------
----------------------------------------------- _ARTIST (INFORMATIONS) -----------------------------------------------
----------------------------------------------------------------------------------------------------*/
DROP TABLE IF EXISTS TableTemp_Artist_1;
CREATE TEMPORARY TABLE TableTemp_Artist_1(
	nconst	VARCHAR(20) PRIMARY KEY,
	primaryName	VARCHAR(500),
	birthYear	VARCHAR(20),
	deathYear	VARCHAR(20),
	primaryProfession	VARCHAR(200),
	knownForTitles	VARCHAR(200)
);

-- Importation des données 
COPY TableTemp_Artist_1 from 'C:/users/Data/name.basics.tsv' 
WITH 
	DELIMITER E'\t'
	QUOTE E'\b'
CSV HEADER;

ALTER TABLE TableTemp_Artist_1 ADD ID_Artist SERIAL;


-- Les \N deviennent des valeurs NULL.
UPDATE TableTemp_Artist_1 SET deathYear = NULL WHERE deathYear = '\N';
UPDATE TableTemp_Artist_1 SET birthYear = NULL WHERE birthYear = '\N';


ALTER TABLE TableTemp_Artist_1 
	ALTER COLUMN birthYear TYPE SMALLINT
	USING birthYear::SMALLINT,
	
	ALTER COLUMN deathYear TYPE SMALLINT
	USING deathYear::SMALLINT;


/*-------------------------------------------------------------------------------------------------------------
----------------------------------------------- _ARTIST (MOVIE) -----------------------------------------------
---------------------------------------------------------------------------------------------------------------*/
DROP TABLE IF EXISTS TableTemp_Artist_2;
CREATE TEMPORARY TABLE TableTemp_Artist_2(
	tconst 			VARCHAR(20),
	MovieOrdering 	VARCHAR(500),
	nconst			VARCHAR(20),
	category 		VARCHAR(20),
	job 			VARCHAR(500),
	MovieCharacters VARCHAR(500)
);

COPY TableTemp_Artist_2
from 'C:/users/Data/title.principals.tsv' 
WITH 
	DELIMITER E'\t'
	QUOTE E'\b'
	ESCAPE '"'
CSV HEADER;

UPDATE TableTemp_Artist_2 SET MovieCharacters = NULL WHERE MovieCharacters = '\N';





/*----------------------------------------------------------------------------------------------------
----------------------------------------------- _GENRE -----------------------------------------------
------------------------------------------------------------------------------------------------------*/
DROP TABLE IF EXISTS TableTemp_Genre;
CREATE TEMPORARY TABLE TableTemp_Genre(
   tconst			VARCHAR(20),
   genres			VARCHAR(20),
   PRIMARY KEY (tconst,genres)
);




/*----------------------------------------------------------------------------------------------------
----------------------------------------------- _OEUVRE (Rating) -----------------------------------------------
----------------------------------------------------------------------------------------------------*/
DROP TABLE IF EXISTS TableTemp_Rating;
CREATE TEMPORARY TABLE TableTemp_Rating(
   tconst			VARCHAR(20) PRIMARY KEY,
   averageRating	FLOAT,
   numVotes			INTEGER
);

-- Importation des données 
COPY TableTemp_Rating from 'C:/users/Data/title.ratings.tsv' 
WITH 
	DELIMITER E'\t'
CSV HEADER;

/*----------------------------------------------------------------------------------------------------
----------------------------------------------- _OEUVRE -----------------------------------------------
----------------------------------------------------------------------------------------------------*/

DROP TABLE IF EXISTS TableTemp_Oeuvre;
CREATE TEMPORARY TABLE TableTemp_Oeuvre(
	tconst	VARCHAR(20) PRIMARY KEY,
	titleType	VARCHAR(20),
	primaryTitle	VARCHAR(500),
	originalTitle	VARCHAR(500),
	isAdult	VARCHAR(20),
	startYear	VARCHAR(20),
	endYear	VARCHAR(20),
	runtimeMinutes	VARCHAR(20),
	genres	VARCHAR(200)
);

-- Importation des données 
COPY TableTemp_Oeuvre from 'C:/users/Data/title.basics.tsv' 
WITH
	DELIMITER E'\t'
	QUOTE E'\b'
CSV HEADER;


ALTER TABLE TableTemp_Oeuvre ADD ID_Movie SERIAL;

-- On garde seulement les films et series
DELETE FROM TableTemp_Oeuvre WHERE titleType = 'short';

-- Les \N deviennent des valeurs NULL.
UPDATE TableTemp_Oeuvre SET Runtimeminutes = NULL WHERE Runtimeminutes = '\N';
UPDATE TableTemp_Oeuvre SET StartYear = NULL WHERE StartYear = '\N';
UPDATE TableTemp_Oeuvre SET endYear = NULL WHERE endYear = '\N';

ALTER TABLE TableTemp_Oeuvre 
    ALTER COLUMN Runtimeminutes TYPE INTEGER
	USING Runtimeminutes::INTEGER,
    
	ALTER COLUMN StartYear TYPE SMALLINT
	USING StartYear::SMALLINT,
	
	ALTER COLUMN endYear TYPE SMALLINT
	USING endYear::SMALLINT;

INSERT INTO TableTemp_Genre (tconst,genres)
	SELECT tconst,UNNEST(STRING_TO_ARRAY(genres, ',')) AS Genre_Name 
	FROM TableTemp_Oeuvre 
	WHERE genres != '\N';




/*----------------------------------------------------------------------------------------------------
----------------------------------------------- _MOVIE -----------------------------------------------
----------------------------------------------------------------------------------------------------*/
DROP TABLE IF EXISTS TableTemp;
CREATE TEMPORARY TABLE TableTemp AS
	SELECT 	ID_Movie as ID_Oeuvre,
			UNNEST(STRING_TO_ARRAY(genres, ',')) AS Genre_Name 
	FROM TableTemp_Oeuvre
	WHERE titleType = 'movie' AND genres != '\N';

INSERT INTO Movie (	ID_Oeuvre,English_Title,Original_Title,Runtime_Minutes,Realease_Year,Average_Rating,Num_Votes,Genre_Name,
					ID_Artist,Profession,Movie_Characters,Primary_Name,Birth_Year,Death_Year)
	SELECT 	ID_Movie as ID_Oeuvre, 			
			PrimaryTitle as English_Title,
			OriginalTitle as Original_Title,
			Runtimeminutes as Runtime_Minutes,
			StartYear as Realease_Year,
			averageRating as Average_Rating,
			numVotes as Num_Votes,

			split_part(genres, ',', 1)  as Genre_Name,

			ID_Artist,
			category as Profession,
			moviecharacters as Movie_Characters,
			primaryName as Primary_Name,
			birthYear as Birth_Year,
			deathYear as Death_Year

	FROM TableTemp_Oeuvre
	LEFT JOIN TableTemp_Rating ON TableTemp_Oeuvre.tconst = TableTemp_Rating.tconst
	LEFT JOIN TableTemp_Artist_2 ON TableTemp_Oeuvre.tconst = TableTemp_Artist_2.tconst
	LEFT JOIN TableTemp_Artist_1 ON TableTemp_Artist_2.nconst = TableTemp_Artist_1.nconst
	WHERE titleType = 'movie' AND genres != '\N' AND ID_Artist is not NULL;

-- Ajout des genres restants
INSERT INTO Oeuvre_Genre (ID_Oeuvre,Genre_Name)
	SELECT * FROM TableTemp;
	
DROP TABLE TableTemp;


-- Complète la colonne "knownForTitles" de la table "_Oeuvre_Artist"
DO $do$ 
DECLARE Artist_Row RECORD;
BEGIN
	FOR Artist_Row IN (
		SELECT 	ID_Artist,
				ID_Movie,
				UNNEST(STRING_TO_ARRAY(knownForTitles, ',')) AS knownForTitles
		FROM TableTemp_Artist_1
		INNER JOIN TableTemp_Oeuvre ON TableTemp_Artist_1.knownForTitles = TableTemp_Oeuvre.tconst
	)
	LOOP
		UPDATE _Oeuvre_Artist SET Know_For_Title = TRUE 
			WHERE ID_Artist = Artist_Row.ID_Artist AND ID_Oeuvre = Artist_Row.ID_Movie;
	END LOOP;
END; 
$do$;



/*----------------------------------------------------------------------------------------------------
----------------------------------------------- _SERIES -----------------------------------------------
----------------------------------------------------------------------------------------------------*/
DROP TABLE IF EXISTS TableTemp_Episode;
CREATE TEMPORARY TABLE TableTemp_Episode(
   tconst			VARCHAR(20) PRIMARY KEY,
   parentTconst		VARCHAR(20),
   seasonNumber		VARCHAR(10),
   episodeNumber	VARCHAR(10)
);

-- Importation des données 
COPY TableTemp_Episode from 'C:/users/Data/title.episode.tsv' 
WITH 
	DELIMITER E'\t'
CSV HEADER;

-- Les \N deviennent des valeurs NULL.
UPDATE TableTemp_Episode SET seasonNumber = NULL WHERE seasonNumber = '\N';
UPDATE TableTemp_Episode SET episodeNumber = NULL WHERE episodeNumber = '\N';

ALTER TABLE TableTemp_Episode 
    ALTER COLUMN seasonNumber TYPE SMALLINT
	USING seasonNumber::SMALLINT,
    
	ALTER COLUMN episodeNumber TYPE INTEGER
	USING episodeNumber::INTEGER;


-- TEMP EPISODES 
DROP TABLE IF EXISTS TEMP_EPISODE;
CREATE TEMP TABLE TEMP_EPISODE AS
	SELECT 	TableTemp_Episode.tconst,
			parentTconst,
			EpisodeNumber as Episode_Number,
			SeasonNumber as Season_Number,
			PrimaryTitle as English_Title,
			OriginalTitle as Original_Title,
			StartYear as Start_Year,
			EndYear as End_Year,
			Runtimeminutes as Runtime_Minutes,
			split_part(genres, ',', 1)  as Genre_Name
	FROM TableTemp_Oeuvre
	INNER JOIN TableTemp_Episode ON TableTemp_Oeuvre.tconst = TableTemp_Episode.tconst
	WHERE genres != '\N';



-- TEMP SERIES
DROP TABLE IF EXISTS TEMP_SERIE;
CREATE TEMP TABLE TEMP_SERIE AS
	SELECT 	DISTINCT(TableTemp_Oeuvre.tconst),
			PrimaryTitle as English_Serie_Title,
			OriginalTitle as Original_Serie_Title
	FROM TableTemp_Oeuvre
	INNER JOIN TableTemp_Episode ON TableTemp_Oeuvre.tconst = TableTemp_Episode.parentTconst;

ALTER TABLE TEMP_SERIE ADD ID_Serie SERIAL;

INSERT INTO Serie (	ID_Serie,Original_Serie_Title,English_Serie_Title,
					Original_Episode_Title,English_Episode_Title,Episode_Number,Runtime_Minutes,Average_Rating,Num_Votes,Genre_Name,
					Season_Number,Start_Year,
					ID_Artist,Profession,Movie_Characters,Primary_Name,Birth_Year,Death_Year)
	SELECT 	ID_Serie,
			Original_Serie_Title,
			English_Serie_Title,
			Original_Title as Original_Episode_Title,
			English_Title as English_Episode_Title,
			Episode_Number,
			Runtime_Minutes,
			averageRating as Average_Rating,
			NumVotes as Num_Votes,
			Genre_Name,

			Season_Number,
			Start_Year,

			ID_Artist,
			category as Profession,
			moviecharacters as Movie_Characters,
			primaryName as Primary_Name,
			birthYear as Birth_Year,
			deathYear as Death_Year

	FROM TEMP_SERIE
	INNER JOIN TEMP_EPISODE
		ON TEMP_EPISODE.parentTconst = TEMP_SERIE.Tconst
	LEFT JOIN TableTemp_Rating ON TEMP_EPISODE.tconst = TableTemp_Rating.tconst
	LEFT JOIN TableTemp_Artist_2 ON TEMP_EPISODE.tconst = TableTemp_Artist_2.tconst
	LEFT JOIN TableTemp_Artist_1 ON TableTemp_Artist_2.nconst = TableTemp_Artist_1.nconst
	WHERE Episode_Number is not NULL AND ID_Artist is not NULL;

