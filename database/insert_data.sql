USE uniride;

INSERT INTO Utilisateur (nom_utilisateur, mot_de_passe, email, telephone, role)
VALUES
('laeticia', 'scrypt:32768:8:1$mOZJkJWMq4NdWgej$8cd7104ba85c77cfbe95ba8e311a0178d23ac123cafe549ed625e3374de19a39d1702a1ed0beb9f1add1935a3ad92abe838c582e36a340e85f646cfd3d14627e', 'laeticia@mail.com', '+15140000001', 'passager'),

('user2', 'scrypt:32768:8:1$mOZJkJWMq4NdWgej$8cd7104ba85c77cfbe95ba8e311a0178d23ac123cafe549ed625e3374de19a39d1702a1ed0beb9f1add1935a3ad92abe838c582e36a340e85f646cfd3d14627e', 'user2@mail.com', '+15140000002', 'passager'),

('driver1', 'scrypt:hash', 'driver1@gmail.com', '+15140000003', 'conducteur'),
('driver2', 'scrypt:hash', 'driver2@gmail.com', '+15140000004', 'conducteur'),

('client1', 'scrypt:hash', 'client1@gmail.com', '+15140000005', 'passager'),
('client2', 'scrypt:hash', 'client2@gmail.com', '+15140000006', 'passager'),

('admin1', 'scrypt:hash', 'admin@gmail.com', '+15140000007', 'admin');


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

DELETE FROM Wallet;

INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
VALUES
(2, 50.00, 20),
(3, 200.00, 100),
(4, 150.00, 80),
(5, 75.00, 30),
(6, 60.00, 25),
(7, 500.00, 200);


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
    ambiance,
    musique,
    telephone_autorise,
    statut
)
VALUES
(3, 1, 2, 1, '2026-04-01', '10:00:00', 25.00, 3, 'calme', TRUE, TRUE, 'actif'),
(4, 2, 1, 2, '2026-04-02', '14:00:00', 30.00, 2, 'dynamique', TRUE, FALSE, 'actif'),
(3, 1, 2, 1, '2026-04-03', '18:00:00', 20.00, 4, 'calme', FALSE, TRUE, 'actif'),
(4, 2, 1, 2, '2026-04-04', '09:30:00', 28.00, 1, 'dynamique', TRUE, TRUE, 'actif');



INSERT INTO Reservation (id_trajet, id_passager, nb_places)
VALUES
(1, 2, 1);

INSERT INTO Paiement (id_reservation, montant_argent, mode_paiement)
VALUES
(1, 25.00, 'argent');

ALTER TABLE Trajet ADD COLUMN vehicule VARCHAR(100) NOT NULL;

UPDATE Trajet SET vehicule = 'Toyota Corolla' WHERE id_trajet IN (1, 3);
UPDATE Trajet SET vehicule = 'Honda Civic' WHERE id_trajet IN (2, 4);

SHOW CREATE TABLE Trajet;
USE uniride;

ALTER TABLE Trajet DROP FOREIGN KEY trajet_ibfk_4;
ALTER TABLE Trajet DROP COLUMN id_vehicule;

SHOW CREATE TABLE Trajet;
DESCRIBE Trajet;

-- =========================
-- DEMANDES DE CERTIFICATION
-- =========================
INSERT INTO DemandeCertification (
    id_utilisateur,
    numero_permis,
    date_expiration_permis,
    type_identite,
    numero_identite,
    date_expiration_identite,
    statut_demande,
    commentaire_admin
)
VALUES
(2, 'P123456789', '2028-05-20', 'passeport', 'AA123456', '2029-08-15', 'en_attente', NULL),
(5, 'Q987654321', '2027-11-10', 'assurance_maladie', 'RAMQ998877', '2028-02-01', 'refusee', 'Photo du document non claire'),
(6, 'L456789123', '2029-01-12', 'passeport', 'BB998877', '2030-06-30', 'acceptee', 'Certification validée');

-- =========================
-- PLAINTES
-- =========================
INSERT INTO Plainte (
    id_utilisateur,
    sujet,
    description,
    statut_plainte
)
VALUES
(2, 'Problème de paiement', 'Le paiement du trajet ne s’est pas affiché correctement.', 'ouverte'),
(5, 'Conducteur en retard', 'Le conducteur est arrivé avec plus de 30 minutes de retard.', 'traitee'),
(6, 'Comportement inapproprié', 'Un passager a eu un comportement irrespectueux.', 'fermee');

-- =========================
-- REPONSES PLAINTES
-- =========================
INSERT INTO ReponsePlainte (
    id_plainte,
    id_admin,
    message_reponse
)
VALUES
(2, 7, 'La plainte a été analysée et le conducteur a été averti.'),
(3, 7, 'Le dossier est fermé après vérification.');

-- =========================
-- WALLETS MANQUANTS
-- =========================
INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
VALUES
(1, 100.00, 50)
ON DUPLICATE KEY UPDATE
solde_argent = VALUES(solde_argent),
solde_points = VALUES(solde_points);

-- =========================
-- HISTORIQUE WALLET
-- =========================
INSERT INTO HistoriqueWallet (
    id_wallet,
    type_operation,
    montant_argent,
    montant_points,
    description
)
VALUES
(1, 'depot', 100.00, 0, 'Dépôt initial utilisateur 1'),
(2, 'paiement', 25.00, 0, 'Paiement réservation trajet 1'),
(3, 'ajustement', 10.00, 20, 'Ajustement manuel administrateur'),
(4, 'reception', 15.00, 10, 'Récompense après trajet complété'),
(5, 'remboursement', 20.00, 0, 'Remboursement réservation annulée'),
(6, 'paiement', 30.00, 0, 'Paiement réservation trajet 2');

-- =========================
-- EVALUATIONS
-- =========================
INSERT INTO Evaluation (
    id_trajet,
    id_passager,
    id_conducteur,
    note,
    commentaire
)
VALUES
(1, 2, 3, 5, 'Très bon trajet, conducteur ponctuel et sympathique.'),
(2, 5, 4, 4, 'Trajet agréable, voiture propre.'),
(3, 6, 3, 3, 'Correct, mais un peu de retard au départ.');

-- =========================
-- REPONSES AUX AVIS
-- =========================
INSERT INTO ReponseAvis (
    id_evaluation,
    id_conducteur,
    commentaire_reponse
)
VALUES
(1, 3, 'Merci beaucoup pour votre retour !'),
(2, 4, 'Merci, au plaisir de vous revoir pour un autre trajet.');

-- =========================
-- QUESTIONS D’AIDE
-- =========================
INSERT INTO QuestionAide (
    id_utilisateur,
    sujet,
    message,
    statut_question
)
VALUES
(2, 'Problème de connexion', 'Je n’arrive pas à me reconnecter après avoir changé mon mot de passe.', 'ouverte'),
(5, 'Question sur les points', 'Comment utiliser mes points pour payer un trajet ?', 'traitee'),
(6, 'Photo de profil', 'Pourquoi ma photo de profil ne se met pas à jour ?', 'fermee');

-- =========================
-- CONVERSATIONS
-- =========================
INSERT INTO Conversation (
    id_passager,
    id_conducteur,
    id_trajet
)
VALUES
(2, 3, 1),
(5, 4, 2),
(6, 3, 3);

-- =========================
-- MESSAGES
-- =========================
INSERT INTO Message (
    id_conversation,
    id_expediteur,
    contenu
)
VALUES
(1, 2, 'Bonjour, est-ce que le point de départ exact est bien au centre-ville ?'),
(1, 3, 'Bonjour, oui exactement près de la gare.'),
(2, 5, 'Bonsoir, avez-vous encore une place pour demain ?'),
(2, 4, 'Oui, il reste une place disponible.'),
(3, 6, 'Est-ce que vous acceptez les valises ?'),
(3, 3, 'Oui, une valise cabine sans problème.');