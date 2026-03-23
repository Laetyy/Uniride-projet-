
DROP TABLE IF EXISTS Evaluation;
DROP TABLE IF EXISTS HistoriqueWallet;
DROP TABLE IF EXISTS Paiement;
DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Trajet;
DROP TABLE IF EXISTS DemandeCertification;
DROP TABLE IF EXISTS Vehicule;
DROP TABLE IF EXISTS ProfilPreference;
DROP TABLE IF EXISTS Ville;
DROP TABLE IF EXISTS Wallet;
DROP TABLE IF EXISTS Utilisateur;

CREATE TABLE Utilisateur (
    id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
    nom_utilisateur VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    telephone VARCHAR(20) UNIQUE,
    role ENUM('passager', 'conducteur', 'admin') NOT NULL DEFAULT 'passager',
    statut ENUM('actif', 'suspendu', 'inactif') NOT NULL DEFAULT 'actif',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Wallet (
    id_wallet INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT UNIQUE NOT NULL,
    solde_argent DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    solde_points INT NOT NULL DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

CREATE TABLE Ville (
    id_ville INT AUTO_INCREMENT PRIMARY KEY,
    nom_ville VARCHAR(100) NOT NULL,
    province VARCHAR(100) NOT NULL
);

CREATE TABLE ProfilPreference (
    id_preference INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT UNIQUE NOT NULL,
    ambiance_preferee ENUM('calme', 'dynamique'),
    musique_preferee BOOLEAN DEFAULT TRUE,
    telephone_autorise BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

CREATE TABLE Vehicule (
    id_vehicule INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    modele VARCHAR(100) NOT NULL,
    type_vehicule VARCHAR(50) NOT NULL,
    couleur VARCHAR(50),
    annee INT,
    plaque_immatriculation VARCHAR(20) UNIQUE NOT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

CREATE TABLE DemandeCertification (
    id_demande INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_demande ENUM('en_attente', 'acceptee', 'refusee') NOT NULL DEFAULT 'en_attente',
    commentaire_admin TEXT,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);

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
    ambiance ENUM('calme', 'dynamique') NOT NULL,
    musique BOOLEAN DEFAULT TRUE,
    telephone_autorise BOOLEAN DEFAULT TRUE,
    statut ENUM('actif', 'complet', 'annule', 'termine') NOT NULL DEFAULT 'actif',
    FOREIGN KEY (id_conducteur) REFERENCES Utilisateur(id_utilisateur),
    FOREIGN KEY (id_ville_depart) REFERENCES Ville(id_ville),
    FOREIGN KEY (id_ville_arrivee) REFERENCES Ville(id_ville),
    FOREIGN KEY (id_vehicule) REFERENCES Vehicule(id_vehicule),
    CHECK (prix >= 0),
    CHECK (places_disponibles > 0)
);

CREATE TABLE Reservation (
    id_reservation INT AUTO_INCREMENT PRIMARY KEY,
    id_trajet INT NOT NULL,
    id_passager INT NOT NULL,
    nb_places INT NOT NULL DEFAULT 1,
    date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut ENUM('en_attente', 'confirmee', 'annulee') NOT NULL DEFAULT 'en_attente',
    FOREIGN KEY (id_trajet) REFERENCES Trajet(id_trajet),
    FOREIGN KEY (id_passager) REFERENCES Utilisateur(id_utilisateur),
    CHECK (nb_places > 0)
);

CREATE TABLE Paiement (
    id_paiement INT AUTO_INCREMENT PRIMARY KEY,
    id_reservation INT UNIQUE NOT NULL,
    montant_argent DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    montant_points INT NOT NULL DEFAULT 0,
    mode_paiement ENUM('argent', 'points', 'mixte') NOT NULL,
    date_paiement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_paiement ENUM('en_attente', 'valide', 'refuse') NOT NULL DEFAULT 'en_attente',
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
    FOREIGN KEY (id_wallet) REFERENCES Wallet(id_wallet)
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
    CHECK (note BETWEEN 1 AND 5)
);
