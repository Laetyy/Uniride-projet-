USE uniride;

INSERT INTO Utilisateur (nom_utilisateur, mot_de_passe, email)
VALUES
('laeticia', '123456', 'laeticia@mail.com'),
('user2', '123456', 'user2@mail.com');

INSERT INTO Ville (nom_ville, province)
VALUES
('Montreal', 'QC'),
('Quebec', 'QC');

INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
VALUES
(1, 100.00, 50),
(2, 50.00, 20);

INSERT INTO Vehicule (id_utilisateur, modele, type_vehicule, plaque_immatriculation)
VALUES
(1, 'Toyota Corolla', 'berline', 'ABC123');

INSERT INTO Trajet (
    id_conducteur, id_ville_depart, id_ville_arrivee, id_vehicule,
    date_trajet, heure_trajet, prix, places_disponibles, ambiance
)
VALUES
(1, 1, 2, 1, '2026-03-25', '10:00:00', 25.00, 3, 'calme');

INSERT INTO Reservation (id_trajet, id_passager, nb_places)
VALUES
(1, 2, 1);

INSERT INTO Paiement (id_reservation, montant_argent, mode_paiement)
VALUES
(1, 25.00, 'argent');