CREATE TABLE `Metrage` (
  `ID_Metrage` varchar(255) PRIMARY KEY,
  `Titre` varchar(255),
  `Annee` int,
  `Categorie` varchar(255)
);

CREATE TABLE `Film` (
  `ID_Film` varchar(255) PRIMARY KEY,
  `Realisateur` varchar(255),
  `note_moyenne` int
);

CREATE TABLE `Serie` (
  `ID_Serie` varchar(255) PRIMARY KEY,
  `NombreSaisons` int,
  `Realisateur` varchar(255),
  `note_moyenne` int
);

CREATE TABLE `Episode` (
  `ID_Episode` varchar(255) PRIMARY KEY,
  `ID_Serie` varchar(255),
  `TitreEpisode` varchar(255),
  `NumeroSaison` int,
  `NumeroEpisode` int
);

CREATE TABLE `Distribution` (
  `ID_Distribution` int PRIMARY KEY,
  `ID_Metrage` varchar(255)
);

CREATE TABLE `Distribution_Personne` (
  `ID_Distribution` int,
  `ID_personne` varchar(255),
  `Role` varchar(255)
);

CREATE TABLE `Personne` (
  `ID_Personne` varchar(255) PRIMARY KEY,
  `Nom` varchar(255),
  `DateNaissance` date,
  `DateMort` date
);

CREATE TABLE `Critique` (
  `ID_Critique` int PRIMARY KEY,
  `ID_Metrage` varchar(255),
  `ID_Utilisateur` int,
  `Note_utilisateur` int,
  `Commentaire` text
);

CREATE TABLE `Utilisateur` (
  `ID_Utilisateur` int PRIMARY KEY,
  `Nom` varchar(255),
  `Email` varchar(255),
  `MotDePasse` varchar(255)
);

CREATE TABLE `ListeMettrages_Mettrages` (
  `ID_Liste` int,
  `ID_Metrage` varchar(255)
);

CREATE TABLE `ListeMettrages` (
  `ID_Liste` int PRIMARY KEY,
  `ID_Utilisateur` int,
  `NomListe` varchar(255)
);

ALTER TABLE `Film` ADD FOREIGN KEY (`ID_Film`) REFERENCES `Metrage` (`ID_Metrage`);

ALTER TABLE `Serie` ADD FOREIGN KEY (`ID_Serie`) REFERENCES `Metrage` (`ID_Metrage`);

ALTER TABLE `Episode` ADD FOREIGN KEY (`ID_Serie`) REFERENCES `Serie` (`ID_Serie`);

ALTER TABLE `Distribution` ADD FOREIGN KEY (`ID_Metrage`) REFERENCES `Metrage` (`ID_Metrage`);

ALTER TABLE `Distribution_Personne` ADD FOREIGN KEY (`ID_Distribution`) REFERENCES `Distribution` (`ID_Distribution`);

ALTER TABLE `Distribution_Personne` ADD FOREIGN KEY (`ID_personne`) REFERENCES `Personne` (`ID_Personne`);

ALTER TABLE `Critique` ADD FOREIGN KEY (`ID_Metrage`) REFERENCES `Metrage` (`ID_Metrage`);

ALTER TABLE `Critique` ADD FOREIGN KEY (`ID_Utilisateur`) REFERENCES `Utilisateur` (`ID_Utilisateur`);

ALTER TABLE `ListeMettrages_Mettrages` ADD FOREIGN KEY (`ID_Liste`) REFERENCES `ListeMettrages` (`ID_Liste`);

ALTER TABLE `ListeMettrages_Mettrages` ADD FOREIGN KEY (`ID_Metrage`) REFERENCES `Metrage` (`ID_Metrage`);

ALTER TABLE `ListeMettrages` ADD FOREIGN KEY (`ID_Utilisateur`) REFERENCES `Utilisateur` (`ID_Utilisateur`);
