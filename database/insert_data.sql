USE uniride;

INSERT INTO Utilisateur (nom_utilisateur, mot_de_passe, email)
VALUES
('laeticia', 'scrypt:32768:8:1$mOZJkJWMq4NdWgej$8cd7104ba85c77cfbe95ba8e311a0178d23ac123cafe549ed625e3374de19a39d1702a1ed0beb9f1add1935a3ad92abe838c582e36a340e85f646cfd3d14627e', 'laeticia@mail.com'),
('user2', 'scrypt:32768:8:1$mOZJkJWMq4NdWgej$8cd7104ba85c77cfbe95ba8e311a0178d23ac123cafe549ed625e3374de19a39d1702a1ed0beb9f1add1935a3ad92abe838c582e36a340e85f646cfd3d14627e', 'user2@mail.com');

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

INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
VALUES
(1, 100.00, 50),
(2, 50.00, 20);

INSERT INTO Vehicule (id_utilisateur, modele, type_vehicule, plaque_immatriculation)
VALUES
(1, 'Toyota Corolla', 'berline', 'ABC123');

INSERT INTO Trajet (
    id_conducteur,
    id_ville_depart,
    id_ville_arrivee,
    id_vehicule,
    date_trajet,
    heure_trajet,
    prix,
    places_disponibles,
    ambiance
)
VALUES
(1, 1, 2, 1, '2026-03-25', '10:00:00', 25.00, 3, 'calme');

INSERT INTO Reservation (id_trajet, id_passager, nb_places)
VALUES
(1, 2, 1);

INSERT INTO Paiement (id_reservation, montant_argent, mode_paiement)
VALUES
(1, 25.00, 'argent');