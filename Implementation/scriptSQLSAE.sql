/*NOTES : 
	NOMBRE DE FILMS TOTAL : 					658 606
		NOMBRE DE FILMS (avec 1 genre min) : 		584 990
		NOMBRE DE FILMS (supprimées (sans genre)) :  73 616
*/


-- Database: SAE

-- DROP DATABASE IF EXISTS "SAE";
CREATE DATABASE "SAE"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

/*------------------------------- GENRE -------------------------------*/
DROP TABLE IF EXISTS _Genre CASCADE;
CREATE TABLE _Genre (
    ID_Genre SERIAL PRIMARY KEY,
    Genre_Name VARCHAR(128) UNIQUE
);

DROP TABLE IF EXISTS _Oeuvre_Genre;
CREATE TABLE _Oeuvre_Genre (
	ID_Oeuvre INT,
	ID_Genre INT,
	PRIMARY KEY(ID_Oeuvre, ID_Genre),
    CONSTRAINT FK_Genre FOREIGN KEY(ID_Genre) REFERENCES _Genre(ID_Genre)
);


DROP VIEW IF EXISTS Oeuvre_Genre;
CREATE VIEW Oeuvre_Genre AS
SELECT 	ID_Oeuvre,
		_Genre.ID_Genre,
		Genre_Name
FROM _Oeuvre_Genre
INNER JOIN _Genre ON _Oeuvre_Genre.ID_Genre = _Genre.ID_Genre;


CREATE OR REPLACE FUNCTION TRIGGER_Oeuvre_Genre_INSERT() RETURNS trigger
LANGUAGE plpgsql 
AS $$
DECLARE
	Now_ID_Genre INTEGER;
BEGIN
	SELECT ID_Genre INTO Now_ID_Genre FROM _Genre WHERE Genre_Name = NEW.Genre_Name;
	IF (Now_ID_Genre IS NULL) THEN
		INSERT INTO _Genre (Genre_Name) VALUES(NEW.Genre_Name) RETURNING ID_Genre INTO Now_ID_Genre;
	END IF;

	IF (NOT EXISTS (SELECT FROM _Oeuvre_Genre WHERE ID_Oeuvre = NEW.ID_Oeuvre AND ID_Genre = Now_ID_Genre)) THEN
		INSERT INTO _Oeuvre_Genre (ID_Oeuvre,ID_Genre) VALUES (NEW.ID_Oeuvre,Now_ID_Genre);
	END IF;
	RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER TRIGGER_Oeuvre_Genre
INSTEAD OF INSERT ON Oeuvre_Genre 
FOR EACH ROW
EXECUTE PROCEDURE TRIGGER_Oeuvre_Genre_INSERT();
/*------------------------------- ARTIST -------------------------------*/
DROP TABLE IF EXISTS _Artist CASCADE;
CREATE TABLE _Artist (
	ID_Artist SERIAL PRIMARY KEY,
	Primary_Name VARCHAR(256),
	Birth_Year SMALLINT,
	Death_Year SMALLINT
);

DROP TABLE IF EXISTS _Oeuvre_Artist;
CREATE TABLE _Oeuvre_Artist (
	ID_Oeuvre INT,
	ID_Artist INT,
	Movie_Characters VARCHAR(1024),
	Profession VARCHAR(128),
	Know_For_Title BOOLEAN DEFAULT FALSE,
	PRIMARY KEY (ID_oeuvre, ID_artist),
    CONSTRAINT FK_Artist FOREIGN KEY(ID_artist) REFERENCES _Artist(ID_artist)
);

/*------------------------------- OEUVRE -------------------------------*/
DROP TABLE IF EXISTS _Oeuvre CASCADE;
CREATE TABLE _Oeuvre(
	ID_Oeuvre 			SERIAL PRIMARY KEY,
	Original_Title 		VARCHAR(500),
	English_Title 		VARCHAR(500),
	Runtime_Minutes 	INTEGER,
	Num_Votes 			INTEGER,
	Average_Rating 		FLOAT
);

/*---------------- OEUVRE_CONSTRAINT ----------------*/
/*
ALTER TABLE _Oeuvre
	ADD CONSTRAINT CHECK_Runtime_Minutes 
	CHECK (Runtime_Minutes >= 0);

ALTER TABLE _Oeuvre
	ADD CONSTRAINT CHECK_NumVotes 
	CHECK (Num_Votes >= 0);

ALTER TABLE _Oeuvre
	ADD CONSTRAINT CHECK_AverageRating
	CHECK ((Average_Rating >= 0) AND (Average_Rating <= 10));*/

/*---------------- OEUVRE_TRIGGER ----------------*/
/*CREATE OR REPLACE TRIGGER TRIGGER_Oeuvre 
BEFORE INSERT OR DELETE OR UPDATE ON _Oeuvre 
FOR EACH STATEMENT
EXECUTE PROCEDURE TRIGGER_RAISE_EXCEPTION();*/



/*------------------------------- MOVIE -------------------------------*/
DROP TABLE IF EXISTS _Movie CASCADE;
CREATE TABLE _Movie(
    Realease_Year      	SMALLINT
) INHERITS (_Oeuvre);

/*---------------- MOVIE_CONSTRAINT ----------------*/
/*	
ALTER TABLE _Movie
	ADD CONSTRAINT CHECK_Realease_Year
	CHECK ((Realease_Year >= 1000) AND (Realease_Year <= date_part('year', CURRENT_DATE)));*/





/*------------------------------- _EPISODE -------------------------------*/
DROP TABLE IF EXISTS _Episode CASCADE;
CREATE TABLE _Episode (
	Episode_Number	INTEGER,
	ID_Saison		SERIAL,
	PRIMARY KEY (ID_Saison,Episode_Number)
) INHERITS (_Oeuvre);

/*---------------- _EPISODE_CONSTRAINT ----------------*/
/*ALTER TABLE _Episode
	ADD CONSTRAINT CHECK_Episode_Number 
	CHECK (Episode_Number >= 0);*/





/*------------------------------- _SAISON -------------------------------*/
DROP TABLE IF EXISTS _Saison CASCADE;
CREATE TABLE _Saison (
	ID_Saison		SERIAL PRIMARY KEY,
	Season_Number	SMALLINT,
	Start_Year 		SMALLINT,
	End_Year 		SMALLINT,
	ID_Serie 		SERIAL,
	UNIQUE (ID_Serie,Season_Number)
);

/*---------------- _SAISON_CONSTRAINT ----------------*/



/*----------------------------------------------------------------------------------------------------
----------------------------------------------- _SERIE -----------------------------------------------
----------------------------------------------------------------------------------------------------*/
DROP TABLE IF EXISTS _Serie CASCADE;
CREATE TABLE _Serie (
	ID_Serie 				SERIAL PRIMARY KEY,
	Original_Serie_Title 	VARCHAR(300),
	English_Serie_Title 	VARCHAR(300)
);

/*---------------- _SERIE_CONSTRAINT ----------------*/





/*------------------------------- CONSTRAINT EPISODE-SAISON-SERIE -------------------------------*/
ALTER TABLE _Episode
	ADD CONSTRAINT FK_Episode 
		FOREIGN KEY (ID_Saison) 
		REFERENCES _Saison(ID_Saison);

ALTER TABLE _Saison
	ADD CONSTRAINT FK_Saison
		FOREIGN KEY (ID_Serie) 
		REFERENCES _Serie(ID_Serie);

/*------------------------------- _CLIENT -------------------------------*/
DROP TABLE IF EXISTS _Client CASCADE;
CREATE TABLE _Client(
	id_client	SERIAL PRIMARY KEY,
	email		VARCHAR(64) not null,
	pwd 	VARCHAR(64) not null
);

/*---------------- _CLIENT_CONSTRAINT ----------------*/
ALTER TABLE _Client
	ADD CONSTRAINT CHECK_email
	CHECK ( email ~ '^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$' );

/*---------------- _CLIENT_TRIGGER ----------------*/
CREATE OR REPLACE FUNCTION DELETE_CLIENT() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM _Profil WHERE _Profil.id_client = OLD.id_client;
	Return OLD;
END;
$$;

CREATE OR REPLACE TRIGGER TRIGGER_DELETE_CLIENT
BEFORE DELETE ON _Client
FOR EACH ROW
EXECUTE PROCEDURE DELETE_CLIENT();

/*------------------------------- PROFIL -------------------------------*/
DROP TABLE IF EXISTS _Profil CASCADE;
CREATE TABLE _Profil(
	id_profil	SERIAL PRIMARY KEY,
	id_client	INTEGER not null,
	profil_name	VARCHAR(64) not null,
	Adult_restriction BOOLEAN DEFAULT FALSE
);

/*---------------- _PROFIL_CONSTRAINT ----------------*/
ALTER TABLE _Profil
	ADD CONSTRAINT fk_client
	FOREIGN KEY(id_client)
	REFERENCES _Client(id_client);

/*---------------- _PROFIL_TRIGGER ----------------*/
CREATE OR REPLACE FUNCTION DELETE_PROFIL() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
	nb_profil INTEGER;
BEGIN
	SELECT COUNT(*) FROM _Profil WHERE _Profil.id_client = OLD.id_client iNTO nb_profil;
	IF (nb_profil>1) THEN
    	DELETE FROM _Profil_Oeuvre WHERE _Profil_Oeuvre.id_profil = OLD.id_profil;
		Return OLD;
	ELSE
		RAISE EXCEPTION 'Client must have at least 1 Profil';
		RETURN NULL;
	END IF;
END;
$$;

CREATE OR REPLACE TRIGGER TRIGGER_DELETE_PROFIL
BEFORE DELETE ON _Profil
FOR EACH ROW
EXECUTE PROCEDURE DELETE_PROFIL();

/*------------------------------- _PROFIL_OEUVRE -------------------------------*/
DROP TABLE IF EXISTS _Profil_Oeuvre CASCADE;
CREATE TABLE _Profil_Oeuvre(
	id_profil INTEGER,
	id_oeuvre INTEGER,
	rating FLOAT,
	PRIMARY KEY(id_profil, id_oeuvre)
);

/*---------------- _PROFIL_OEUVRE_CONSTRAINT ----------------*/
ALTER TABLE _Profil_Oeuvre
	ADD CONSTRAINT fk_profil
	FOREIGN KEY(id_profil)
	REFERENCES _Profil(id_profil);

/*ALTER TABLE _Profil_Oeuvre
	ADD CONSTRAINT fk_oeuvre
	FOREIGN KEY(id_oeuvre)
	REFERENCES _Oeuvre(id_oeuvre);*/

/*---------------- _PROFIL_OEUVRE_TRIGGER ----------------*/
CREATE OR REPLACE FUNCTION id_oeuvre_exists() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
	id_oeuvre_exists boolean;
BEGIN
	SELECT (id_oeuvre IS NOT NULL) FROM _Oeuvre WHERE id_oeuvre = NEW.id_oeuvre INTO id_oeuvre_exists;
	IF (id_oeuvre_exists) THEN
		RETURN NEW;
	ELSE
		RAISE EXCEPTION 'Nonexistent ID --> %', NEW.id_oeuvre;
		RETURN NULL;
	END IF;
END;
$$;

CREATE OR REPLACE TRIGGER id_oeuvre_fk_check
BEFORE INSERT OR UPDATE ON _Profil_Oeuvre
FOR EACH ROW
EXECUTE FUNCTION id_oeuvre_exists();

/*--------------------------------------------------------------------------------------------------------
----------------------------------------------- VIEW_MOVIE -----------------------------------------------
----------------------------------------------------------------------------------------------------------*/
DROP VIEW IF EXISTS Movie;
CREATE VIEW Movie AS
SELECT 	_Movie.ID_Oeuvre,Original_Title,English_Title,Genre_Name,Realease_Year,Runtime_Minutes,Num_Votes,Average_Rating,
		_Artist.ID_Artist,Movie_Characters,Primary_Name,Birth_Year,Death_Year,Profession,Know_For_Title
FROM _Movie
INNER JOIN _oeuvre_genre ON _Oeuvre_Genre.ID_Oeuvre = _Movie.ID_Oeuvre
INNER JOIN _genre ON _Oeuvre_Genre.id_genre = _genre.id_genre
INNER JOIN _Oeuvre_Artist ON _Oeuvre_Artist.ID_Oeuvre = _Movie.ID_Oeuvre
INNER JOIN _Artist ON _Artist.ID_Artist = _Artist.ID_Artist;


CREATE OR REPLACE FUNCTION TRIGGER_MOVIE_INSERT() RETURNS trigger
LANGUAGE plpgsql 
AS $$
DECLARE
	Now_ID_Movie INTEGER;
	Now_ID_Genre INTEGER;
	Now_ID_Artist INTEGER;
BEGIN

	-- INSERT _Movie
	IF (NEW.ID_Oeuvre IS NULL) THEN
		INSERT INTO _Movie (Original_Title,English_Title,Realease_Year,Runtime_Minutes,Num_Votes,Average_Rating) 
		VALUES (NEW.Original_Title,NEW.English_Title,NEW.Realease_Year,NEW.Runtime_Minutes,NEW.Num_Votes,NEW.Average_Rating)
		RETURNING ID_Oeuvre INTO Now_ID_Movie;
	ELSE
		IF (NOT EXISTS (SELECT FROM _Movie WHERE ID_Oeuvre = NEW.ID_Oeuvre)) THEN
			INSERT INTO _Movie (ID_Oeuvre,Original_Title,English_Title,Realease_Year,Runtime_Minutes,Num_Votes,Average_Rating) 
			VALUES (NEW.ID_Oeuvre,NEW.Original_Title,NEW.English_Title,NEW.Realease_Year,NEW.Runtime_Minutes,NEW.Num_Votes,NEW.Average_Rating);
		END IF;
		Now_ID_Movie = NEW.ID_Oeuvre;
	END IF;


	-- INSERT _Genre
	IF (NEW.Genre_Name is NULL) THEN
		IF (NOT EXISTS (SELECT FROM Oeuvre_Genre WHERE ID_Oeuvre = Now_ID_Movie)) THEN
			RAISE EXCEPTION 'A movie must have one genre';
		END IF;
	ELSE
		
		SELECT ID_Genre INTO Now_ID_Genre FROM _Genre WHERE Genre_Name = NEW.Genre_Name;
		IF (Now_ID_Genre IS NULL) THEN
			INSERT INTO _Genre (Genre_Name) VALUES(NEW.Genre_Name) RETURNING ID_Genre INTO Now_ID_Genre;
		END IF;
		IF (NOT EXISTS (SELECT FROM _Oeuvre_Genre WHERE ID_Oeuvre = Now_ID_Movie AND ID_Genre = Now_ID_Genre)) THEN
			INSERT INTO _Oeuvre_Genre (ID_Oeuvre,ID_Genre) VALUES (Now_ID_Movie,Now_ID_Genre);
		END IF;
	END IF;

	-- INSERT _Artist
	IF (NEW.ID_Artist IS NULL) THEN
		INSERT INTO _Artist (Primary_Name,Birth_Year,Death_Year) 
		VALUES (NEW.Primary_Name,NEW.Birth_Year,NEW.Death_Year)
		RETURNING ID_Artist INTO Now_ID_Artist;
	ELSE
		IF (NOT EXISTS (SELECT FROM _Artist WHERE ID_Artist = NEW.ID_Artist)) THEN
			INSERT INTO _Artist (ID_Artist,Primary_Name,Birth_Year,Death_Year) 
			VALUES (NEW.ID_Artist,NEW.Primary_Name,NEW.Birth_Year,NEW.Death_Year);
		END IF;
		Now_ID_Artist = NEW.ID_Artist;
	END IF;

	IF (NOT EXISTS (SELECT FROM _Oeuvre_Artist WHERE ID_Artist = Now_ID_Artist AND ID_Oeuvre = Now_ID_Movie)) THEN
		INSERT INTO _Oeuvre_Artist (ID_Oeuvre,ID_Artist,Movie_Characters,Profession,Know_For_Title) 
		VALUES (Now_ID_Movie,Now_ID_Artist,NEW.Movie_Characters,NEW.Profession,NEW.Know_For_Title);
	END IF;
	RETURN NEW;
END;
$$;


CREATE OR REPLACE TRIGGER TRIGGER_MOVIE
INSTEAD OF INSERT ON Movie 
FOR EACH ROW
EXECUTE PROCEDURE TRIGGER_MOVIE_INSERT();



/*--------------------------------------------------------------------------------------------------------
----------------------------------------------- VIEW_SERIE -----------------------------------------------
----------------------------------------------------------------------------------------------------------*/
CREATE OR REPLACE VIEW Serie AS
SELECT 	_Episode.ID_Oeuvre,
		_Serie.ID_Serie,Original_Serie_Title,
		English_Serie_Title,
		_saison.ID_Saison,
		Season_Number,
		Episode_Number,
		_Episode.Original_Title as Original_Episode_Title,
		_Episode.English_Title as English_Episode_Title,
		Start_Year,
		End_Year,
		Runtime_Minutes,
		Num_Votes,
		Average_Rating,
		Genre_Name,

		_Artist.ID_Artist,
		Movie_Characters,
		Primary_Name,
		Birth_Year,
		Death_Year,
		Profession,
		Know_For_Title
FROM _episode
INNER JOIN _saison ON _episode.ID_Saison = _saison.ID_Saison 
INNER JOIN _Serie ON _saison.ID_Serie = _Serie.ID_Serie
INNER JOIN _oeuvre_genre ON _Oeuvre_Genre.ID_Oeuvre = _Episode.ID_Oeuvre
INNER JOIN _genre ON _Oeuvre_Genre.id_genre = _genre.id_genre
INNER JOIN _Oeuvre_Artist ON _Oeuvre_Artist.ID_Oeuvre = _Episode.ID_Oeuvre
INNER JOIN _Artist ON _Artist.ID_Artist = _Artist.ID_Artist;


CREATE OR REPLACE FUNCTION TRIGGER_SERIE_INSERT() RETURNS trigger
LANGUAGE plpgsql 
AS $$
DECLARE
	Now_ID_Serie INTEGER;
	Now_ID_Saison INTEGER;
	Now_ID_Episode INTEGER;
	Now_ID_Genre INTEGER;
	Now_Start_Year SMALLINT;
	Now_End_Year SMALLINT;
BEGIN
	-- NEW _Serie
	IF (NEW.ID_Serie is NULL) THEN
		INSERT INTO _Serie (Original_Serie_Title,English_Serie_Title)
		VALUES (NEW.Original_Serie_Title,NEW.English_Serie_Title) 
		RETURNING ID_Serie INTO Now_ID_Serie;
	
	ELSE
		Now_ID_Serie = NEW.ID_Serie;
		IF (SELECT COUNT(*) FROM _Serie WHERE ID_Serie = Now_ID_Serie) < 1 THEN
			INSERT INTO _Serie (ID_Serie,Original_Serie_Title,English_Serie_Title)
			VALUES (Now_ID_Serie,NEW.Original_Serie_Title,NEW.English_Serie_Title);
		END IF;
	END IF;


	-- NEW _Saison
	SELECT ID_Saison,Start_Year,End_Year INTO Now_ID_Saison,Now_Start_Year,Now_End_Year FROM _Saison WHERE Season_Number = NEW.Season_Number AND ID_Serie = Now_ID_Serie;
	IF (Now_ID_Saison is NULL) THEN
		INSERT INTO _Saison (Season_Number,ID_Serie,Start_Year,End_Year)
		VALUES (NEW.Season_Number,Now_ID_Serie,NEW.Start_Year,NEW.Start_Year) 
		RETURNING ID_Saison INTO Now_ID_Saison;
		SELECT Start_Year,End_Year INTO Now_Start_Year,Now_End_Year FROM _Saison WHERE Season_Number = NEW.Season_Number AND ID_Serie = Now_ID_Serie;
	ELSE
		IF (NEW.Start_Year is not NULL) THEN
			IF (NEW.Start_Year < Now_Start_Year) THEN
				UPDATE _Saison SET Start_Year = NEW.Start_Year WHERE ID_Saison = Now_ID_Saison;
			END IF;

			IF (NEW.Start_Year > Now_End_Year) THEN
				UPDATE _Saison SET End_Year = NEW.Start_Year WHERE ID_Saison = Now_ID_Saison;
			END IF;
		END IF;
	END IF;

	-- NEW _Episode
	SELECT ID_Oeuvre FROM _Episode INTO Now_ID_Episode WHERE Episode_Number = NEW.Episode_Number AND ID_Saison = Now_ID_Saison;
	IF (Now_ID_Episode IS NULL) THEN
		INSERT INTO _Episode (Episode_Number,Original_Title,English_Title,Runtime_Minutes,Num_Votes,Average_Rating,ID_Saison)
		VALUES (NEW.Episode_Number,NEW.Original_Episode_Title,NEW.English_Episode_Title,NEW.Runtime_Minutes,NEW.Num_Votes,NEW.Average_Rating,Now_ID_Saison)
		RETURNING ID_Oeuvre INTO Now_ID_Episode ;
	END IF;
	
	-- INSERT _Genre
	IF (NEW.Genre_Name is NULL) THEN
		IF (NOT EXISTS (SELECT FROM Oeuvre_Genre WHERE ID_Oeuvre = Now_ID_Episode)) THEN
			RAISE EXCEPTION 'A Episode must have one genre';
		END IF;
	ELSE
		SELECT ID_Genre INTO Now_ID_Genre FROM _Genre WHERE Genre_Name = NEW.Genre_Name;
		IF (Now_ID_Genre IS NULL) THEN
			INSERT INTO _Genre (Genre_Name) VALUES(NEW.Genre_Name) RETURNING ID_Genre INTO Now_ID_Genre;
		END IF;
		IF (NOT EXISTS (SELECT FROM _Oeuvre_Genre WHERE ID_Oeuvre = Now_ID_Episode AND ID_Genre = Now_ID_Genre)) THEN
			INSERT INTO _Oeuvre_Genre (ID_Oeuvre,ID_Genre) VALUES (Now_ID_Episode,Now_ID_Genre);
		END IF;
	END IF;

	-- INSERT _Artist
	

	RETURN NEW;
END;
$$;


CREATE OR REPLACE TRIGGER TRIGGER_Serie 
INSTEAD OF INSERT ON Serie 
FOR EACH ROW
EXECUTE PROCEDURE TRIGGER_SERIE_INSERT();



/*--------------------------------------------------------------------------------------------------------
----------------------------------------------- VIEW_SAISON -----------------------------------------------
----------------------------------------------------------------------------------------------------------*/

CREATE OR REPLACE VIEW Saison AS
SELECT ID_Serie, _saison.ID_Saison,Season_Number,Episode_Number,Original_Title as Original_Episode_Title,English_Title as English_Episode_Title,Runtime_Minutes 
FROM _saison
INNER JOIN _episode ON _episode.ID_Saison = _saison.ID_Saison ;



CREATE OR REPLACE FUNCTION TRIGGER_SAISON_INSERT() RETURNS trigger
LANGUAGE plpgsql 
AS $$
DECLARE
	New_ID_Saison INTEGER;
BEGIN
	INSERT INTO _Saison (Season_Number,ID_Serie)
	VALUES (NEW.Season_Number,New.ID_Serie) 
	RETURNING ID_Saison INTO New_ID_Saison;
	
	INSERT INTO _Episode (Episode_Number,Original_Title,English_Title,Runtime_Minutes,ID_Saison)
	VALUES (NEW.Episode_Number,NEW.Original_Episode_Title,NEW.English_Episode_Title,NEW.Runtime_Minutes,New_ID_Saison);
	
	RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER TRIGGER_Saison
INSTEAD OF INSERT ON Saison 
FOR EACH ROW
EXECUTE PROCEDURE TRIGGER_SAISON_INSERT();

/*--------------------------------------------------------------------------------------------------------
----------------------------------------------- VIEW_CLIENT -----------------------------------------------
----------------------------------------------------------------------------------------------------------*/
DROP VIEW IF EXISTS Client_;
CREATE VIEW Client_ AS
SELECT email, pwd, profil_name, adult_restriction 
FROM _Client 
INNER JOIN _Profil ON _Client.id_client = _Profil.id_client;

CREATE OR REPLACE FUNCTION TRIGGER_CLIENT_INSERT() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
	Now_id_client INTEGER;
BEGIN
	INSERT INTO _Client (email, pwd) VALUES (NEW.email, NEW. pwd) RETURNING id_client INTO Now_id_client;
	INSERT INTO _Profil (id_client, profil_name, adult_restriction) VALUES (Now_id_client, NEW.profil_name, NEW.adult_restriction);
	RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER TRIGGER_Client
INSTEAD OF INSERT ON Client_
FOR EACH ROW
EXECUTE PROCEDURE TRIGGER_CLIENT_INSERT();


/*--------------------------------------------------------------------------------------------------------
----------------------------------------------- TESTS ----------------------------------------------------
----------------------------------------------------------------------------------------------------------*/
/*COPY Client_ from 'C:/users/clients.csv' 
WITH 
	DELIMITER ','
CSV HEADER;*/

DELETE FROM _Movie;
ALTER SEQUENCE _oeuvre_id_oeuvre_seq RESTART WITH 1;

DELETE FROM _Oeuvre_Artist;
DELETE FROM _Artist;
ALTER SEQUENCE _artist_id_artist_seq RESTART WITH 1;

DELETE FROM _Oeuvre_Genre;
DELETE FROM _Genre;
ALTER SEQUENCE _genre_id_genre_seq RESTART WITH 1;


/*
INSERT INTO Movie 
	(Original_Title,English_Title,Genre_Name,Realease_Year,Runtime_Minutes,
	Movie_Characters,Primary_Name,Birth_Year,Death_Year,Profession,Know_For_Title)
VALUES (
	'Iron Man','Iron Man','Super-héros',2008,126,
	'Tony Stark','Downey Robert',1965,NULL,'acteur',TRUE);

INSERT INTO Movie 
	(Original_Title,English_Title,Genre_Name,Realease_Year,Runtime_Minutes,
	Movie_Characters,Primary_Name,Birth_Year,Death_Year,Profession,Know_For_Title)
VALUES (
	'Captain America: First Avenger','Captain America: First Avenger','Science Fiction',2011,124,
	'Steve Rogers','Evans Christopher Robert',1981,NULL,'Acteur',TRUE);

INSERT INTO Movie 
	(Original_Title,English_Title,Genre_Name,Realease_Year,Runtime_Minutes,
	ID_Artist,Movie_Characters,Profession,Know_For_Title)
VALUES (
	'Captain America: The Winter Soldier','Captain America: The Winter Soldier','Action',2014,136,
	2,'Steve Rogers','Acteur',TRUE);

INSERT INTO Movie 
	(Original_Title,English_Title,Genre_Name,Realease_Year,Runtime_Minutes,
	ID_Artist,Movie_Characters,Profession,Know_For_Title)
VALUES (
	'Avengers','Avengers','Science Fiction',2012,135,
	1,'Iron Man','Acteur',TRUE);

INSERT INTO Movie (ID_Oeuvre,ID_Artist,Movie_Characters,Profession,Know_For_Title)
VALUES (4,2,'Steve Rogers','Acteur',FALSE);

INSERT INTO Oeuvre_Genre (ID_Oeuvre,Genre_Name)
VALUES (4,'Super héros');

*/

DELETE FROM _Serie;
ALTER SEQUENCE _serie_id_serie_seq RESTART WITH 1;

DELETE FROM _Saison;
ALTER SEQUENCE _saison_id_serie_seq RESTART WITH 1;

DELETE FROM _Episode;
ALTER SEQUENCE _genre_id_genre_seq RESTART WITH 1;


/*
INSERT INTO Serie (Original_Serie_Title,English_Serie_Title,Original_Episode_Title,English_Episode_Title,Season_Number,Episode_Number,Runtime_Minutes,Start_Year,Genre_Name,
					Movie_Characters,Primary_Name,Birth_Year,Profession,Know_For_Title)
VALUES ('Obi-Wan Kenobi','Obi-Wan Kenobi','Épisode 1 : Partie I','Épisode 1 : Partie I',1,1,62,2022,'Science-fiction',
		'Obi-Wan Kenobi','Ewan McGregor',1971,'Acteur',FALSE);
*/