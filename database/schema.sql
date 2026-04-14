DROP DATABASE uniride;
CREATE DATABASE IF NOT EXISTS uniride;
USE uniride;
-- ===============================
-- TABLE UTILISATEUR
-- ===============================
CREATE TABLE Utilisateur (
    id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
    nom_utilisateur VARCHAR(10) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    telephone VARCHAR(12) UNIQUE,
    photo_profil VARCHAR(255),
    role ENUM('passager','conducteur','admin') DEFAULT 'passager',
    statut ENUM('actif','suspendu','inactif') DEFAULT 'actif',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bio TEXT
);

-- ===============================
-- TABLE WALLET
-- ===============================
CREATE TABLE Wallet (
    id_wallet INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT UNIQUE NOT NULL,
    solde_argent DECIMAL(10,2) DEFAULT 0.00,
    solde_points INT DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur),
    CHECK (solde_argent >= 0),
    CHECK (solde_points >= 0)
);

-- ===============================
-- TABLE VILLE
-- ===============================

CREATE TABLE Ville (
    id_ville INT AUTO_INCREMENT PRIMARY KEY,
    nom_ville VARCHAR(100) NOT NULL,
    province VARCHAR(100) NOT NULL,
    UNIQUE (nom_ville, province)
);

INSERT INTO Ville (nom_ville, province)
VALUES
('Montreal', 'QC'),
('Quebec', 'QC'),
('Laval', 'QC'),
('Gatineau', 'QC'),
('Sherbrooke', 'QC'),
('Trois-Rivieres', 'QC'),
('Longueuil', 'QC'),
('Saguenay', 'QC'),
('Levis', 'QC'),
('Terrebonne', 'QC'),
('Saint-Jean-sur-Richelieu', 'QC'),
('Drummondville', 'QC'),
('Granby', 'QC'),
('Blainville', 'QC'),
('Saint-Jerome', 'QC'),
('Toronto', 'ON'),
('Ottawa', 'ON'),
('Mississauga', 'ON'),
('Brampton', 'ON'),
('Hamilton', 'ON'),
('London', 'ON'),
('Markham', 'ON'),
('Vaughan', 'ON'),
('Kitchener', 'ON'),
('Windsor', 'ON'),
('Richmond Hill', 'ON'),
('Oakville', 'ON'),
('Burlington', 'ON'),
('Vancouver', 'BC'),
('Surrey', 'BC'),
('Burnaby', 'BC'),
('Richmond', 'BC'),
('Abbotsford', 'BC'),
('Coquitlam', 'BC'),
('Kelowna', 'BC'),
('Victoria', 'BC'),
('Calgary', 'AB'),
('Edmonton', 'AB'),
('Red Deer', 'AB'),
('Lethbridge', 'AB'),
('Winnipeg', 'MB'),
('Brandon', 'MB'),
('Halifax', 'NS'),
('Sydney', 'NS'),
('Saskatoon', 'SK'),
('Regina', 'SK'),
('St. John''s', 'NL'),
('Moncton', 'NB'),
('Fredericton', 'NB'),
('Saint John', 'NB'),
('Charlottetown', 'PE');

-- ===============================
-- TABLE PREFERENCES
-- ===============================

CREATE TABLE ProfilPreference (
    id_preference INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT UNIQUE NOT NULL,
    ambiance_preferee ENUM('calme','dynamique'),
    musique_preferee BOOLEAN DEFAULT TRUE,
    telephone_autorise BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

-- ===============================
-- TABLE VEHICULE
-- ===============================
CREATE TABLE Vehicule (
    id_vehicule INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    modele VARCHAR(100) NOT NULL,
    type_vehicule VARCHAR(50) NOT NULL,
    couleur VARCHAR(50),
    annee INT,
    plaque_immatriculation VARCHAR(20) UNIQUE NOT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur),
    CHECK (annee IS NULL OR annee >= 1900)
);

CREATE TABLE DemandeCertification (
    id_demande INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,

    numero_permis VARCHAR(50) NOT NULL,
    date_expiration_permis DATE NOT NULL,

    type_identite ENUM('passeport', 'assurance_maladie') NOT NULL,
    numero_identite VARCHAR(50) NOT NULL,
    date_expiration_identite DATE NOT NULL,

    date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_demande ENUM('en_attente', 'acceptee', 'refusee') NOT NULL DEFAULT 'en_attente',
    commentaire_admin TEXT,

    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

-- ===============================
-- TABLE TRAJET
-- ===============================
CREATE TABLE Trajet (
    id_trajet INT AUTO_INCREMENT PRIMARY KEY,
    id_conducteur INT NOT NULL,
    id_ville_depart INT NOT NULL,
    id_ville_arrivee INT NOT NULL,
    id_vehicule INT NOT NULL,
    date_trajet DATE NOT NULL,
    heure_trajet TIME NOT NULL,
    prix DECIMAL(10,2) NOT NULL,
    places_disponibles INT NOT NULL,
    ambiance ENUM('calme','dynamique') NOT NULL,
    musique BOOLEAN DEFAULT TRUE,
    telephone_autorise BOOLEAN DEFAULT TRUE,
    statut ENUM('actif','complet','annule','termine') DEFAULT 'actif',

    FOREIGN KEY (id_conducteur) REFERENCES Utilisateur(id_utilisateur),
    FOREIGN KEY (id_ville_depart) REFERENCES Ville(id_ville),
    FOREIGN KEY (id_ville_arrivee) REFERENCES Ville(id_ville),
    FOREIGN KEY (id_vehicule) REFERENCES Vehicule(id_vehicule),

    CHECK (prix >= 0),
    CHECK (places_disponibles >= 0),
    CHECK (id_ville_depart <> id_ville_arrivee)
);
CREATE TABLE ArretTrajet (
    id_arret INT AUTO_INCREMENT PRIMARY KEY,
    id_trajet INT NOT NULL,
    id_ville INT NOT NULL,
    ordre_arret INT NOT NULL,
    FOREIGN KEY (id_trajet) REFERENCES Trajet(id_trajet),
    FOREIGN KEY (id_ville) REFERENCES Ville(id_ville),
    UNIQUE (id_trajet, ordre_arret)
);

-- ===============================
-- TABLE RESERVATION
-- ===============================
CREATE TABLE Reservation (
    id_reservation INT AUTO_INCREMENT PRIMARY KEY,
    id_trajet INT NOT NULL,
    id_passager INT NOT NULL,
    nb_places INT DEFAULT 1,
    date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut ENUM('en_attente','confirmee','annulee') DEFAULT 'en_attente',

    FOREIGN KEY (id_trajet) REFERENCES Trajet(id_trajet),
    FOREIGN KEY (id_passager) REFERENCES Utilisateur(id_utilisateur),
    CHECK (nb_places > 0)
);

-- ===============================
-- TABLE PAIEMENT
-- ===============================

CREATE TABLE Paiement (
    id_paiement INT AUTO_INCREMENT PRIMARY KEY,
    id_reservation INT UNIQUE NOT NULL,
    montant_argent DECIMAL(10,2) DEFAULT 0.00,
    montant_points INT DEFAULT 0,
    mode_paiement ENUM('argent','points','mixte') NOT NULL,
    date_paiement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_paiement ENUM('en_attente','valide','refuse') DEFAULT 'en_attente',

    FOREIGN KEY (id_reservation) REFERENCES Reservation(id_reservation),
    CHECK (montant_argent >= 0),
    CHECK (montant_points >= 0)
);

CREATE TABLE HistoriqueWallet (
    id_operation INT AUTO_INCREMENT PRIMARY KEY,
    id_wallet INT NOT NULL,
    type_operation ENUM('depot', 'paiement', 'reception', 'retrait', 'remboursement', 'ajustement') NOT NULL,
    montant_argent DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    montant_points INT NOT NULL DEFAULT 0,
    date_operation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (id_wallet) REFERENCES Wallet(id_wallet),
    CHECK (montant_argent >= 0),
    CHECK (montant_points >= 0)
);

CREATE TABLE Retrait (
    id_retrait INT AUTO_INCREMENT PRIMARY KEY,
    id_wallet INT NOT NULL,
    numero_transit VARCHAR(5) NOT NULL,
    numero_institution VARCHAR(3) NOT NULL,
    numero_compte VARCHAR(7) NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    date_retrait TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_retrait ENUM('en_attente', 'valide', 'refuse') NOT NULL DEFAULT 'en_attente',
    FOREIGN KEY (id_wallet) REFERENCES Wallet(id_wallet),
    CHECK (montant > 0)
);

CREATE TABLE Evaluation (
    id_evaluation INT AUTO_INCREMENT PRIMARY KEY,
    id_trajet INT NOT NULL,
    id_passager INT NOT NULL,
    id_conducteur INT NOT NULL,
    note INT NOT NULL,
    commentaire TEXT,
    date_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_trajet) REFERENCES Trajet(id_trajet),
    FOREIGN KEY (id_passager) REFERENCES Utilisateur(id_utilisateur),
    FOREIGN KEY (id_conducteur) REFERENCES Utilisateur(id_utilisateur),
    CHECK (note BETWEEN 1 AND 5),
    UNIQUE (id_trajet, id_passager)
);

CREATE TABLE ReponseAvis (
    id_reponse_avis INT AUTO_INCREMENT PRIMARY KEY,
    id_evaluation INT UNIQUE NOT NULL,
    id_conducteur INT NOT NULL,
    commentaire_reponse TEXT NOT NULL,
    date_reponse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_evaluation) REFERENCES Evaluation(id_evaluation),
    FOREIGN KEY (id_conducteur) REFERENCES Utilisateur(id_utilisateur)
);

CREATE TABLE Conversation (
    id_conversation INT AUTO_INCREMENT PRIMARY KEY,
    id_passager INT NOT NULL,
    id_conducteur INT NOT NULL,
    id_trajet INT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_passager) REFERENCES Utilisateur(id_utilisateur),
    FOREIGN KEY (id_conducteur) REFERENCES Utilisateur(id_utilisateur),
    FOREIGN KEY (id_trajet) REFERENCES Trajet(id_trajet)
);

CREATE TABLE Message (
    id_message INT AUTO_INCREMENT PRIMARY KEY,
    id_conversation INT NOT NULL,
    id_expediteur INT NOT NULL,
    contenu TEXT NOT NULL,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_conversation) REFERENCES Conversation(id_conversation),
    FOREIGN KEY (id_expediteur) REFERENCES Utilisateur(id_utilisateur)
);
ALTER TABLE Message
ADD COLUMN lu BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE QuestionAide (
    id_question INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    sujet VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    date_question TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_question ENUM('ouverte', 'traitee', 'fermee') NOT NULL DEFAULT 'ouverte',
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

CREATE TABLE Plainte (
    id_plainte INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    sujet VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    date_plainte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_plainte ENUM('ouverte', 'traitee', 'fermee') NOT NULL DEFAULT 'ouverte',
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

CREATE TABLE ReponsePlainte (
    id_reponse_plainte INT AUTO_INCREMENT PRIMARY KEY,
    id_plainte INT NOT NULL,
    id_admin INT NOT NULL,
    message_reponse TEXT NOT NULL,
    date_reponse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_plainte) REFERENCES Plainte(id_plainte),
    FOREIGN KEY (id_admin) REFERENCES Utilisateur(id_utilisateur)
);
-- =============================
-- CARTE DE CRÉDIT
-- =============================
CREATE TABLE IF NOT EXISTS CarteCredit (
    id_carte_credit INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    titulaire VARCHAR(100),
    numero_carte VARCHAR(20),
    date_expiration VARCHAR(7),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

-- =============================
-- CARTE DE DÉBIT (infos bancaires)
-- =============================
CREATE TABLE IF NOT EXISTS CarteDebit (
    id_carte_debit INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    titulaire VARCHAR(100),
    numero_compte VARCHAR(30),
    numero_transit VARCHAR(10),
    institution VARCHAR(10),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

-- =============================
-- ROUTINE RÉSERVATION
-- =============================
DELIMITER //

CREATE TRIGGER diminuer_places
AFTER INSERT ON Reservation
FOR EACH ROW
BEGIN
    UPDATE Trajet
    SET places_disponibles = places_disponibles - 1
    WHERE id_trajet = NEW.id_trajet;
END//

DELIMITER ;


-- =============================
-- ROUTINE NOTE CONDUCTEUR
-- =============================
DELIMITER //

CREATE TRIGGER update_moyenne_conducteur
AFTER INSERT ON Evaluation
FOR EACH ROW
BEGIN
    UPDATE Utilisateur u
    SET u.bio = u.bio  -- (juste pour forcer update si besoin)
    WHERE u.id_utilisateur = NEW.id_conducteur;
END//

DELIMITER ;


-- INDEX UTILISATEUR
CREATE INDEX idx_user_email ON Utilisateur(email);
CREATE INDEX idx_user_username ON Utilisateur(nom_utilisateur);

-- INDEX TRAJET
CREATE INDEX idx_trajet_villes ON Trajet(id_ville_depart, id_ville_arrivee);

-- INDEX MESSAGE
CREATE INDEX idx_message_conversation ON Message(id_conversation);

-- INDEX RESERVATION
CREATE INDEX idx_reservation_trajet ON Reservation(id_trajet);