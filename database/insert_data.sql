USE uniride;

-- =========================
-- UTILISATEURS
-- =========================
INSERT INTO Utilisateur
(nom_utilisateur, mot_de_passe, nom, prenom, email, telephone, photo_profil, role, statut, bio)
VALUES
('sarah01', 'scrypt:hash1', 'Benali', 'Sarah', 'sarah01@gmail.com', '+15145550001', 'uploads/sarah.jpg', 'conducteur', 'actif', 'Conductrice sérieuse, aime les trajets Montréal-Québec.'),
('nadir02', 'scrypt:hash2', 'Ait Said', 'Nadir', 'nadir02@gmail.com', '+15145550002', 'uploads/nadir.jpg', 'conducteur', 'actif', 'Toujours ponctuel, ambiance calme.'),
('ines03', 'scrypt:hash3', 'Bouchard', 'Ines', 'ines03@gmail.com', '+15145550003', 'uploads/ines.jpg', 'passager', 'actif', 'Étudiante, voyage souvent la fin de semaine.'),
('yacine4', 'scrypt:hash4', 'Messaoud', 'Yacine', 'yacine04@gmail.com', '+15145550004', 'uploads/yacine.jpg', 'passager', 'actif', 'Recherche des trajets économiques.'),
('admin001', 'scrypt:hash5', 'Tremblay', 'Julie', 'admin01@gmail.com', '+15145550005', 'uploads/admin.jpg', 'admin', 'actif', 'Administration UniRide.'),
('amal005', 'scrypt:hash6', 'Rahmani', 'Amal', 'amal005@gmail.com', '+15145550006', 'uploads/amal.jpg', 'passager', 'actif', 'Préfère voyager avec musique.'),
('karim06', 'scrypt:hash7', 'Zeroual', 'Karim', 'karim06@gmail.com', '+15145550007', 'uploads/karim.jpg', 'conducteur', 'actif', 'Conduit souvent entre Laval et Ottawa.');

-- =========================
-- WALLETS
-- =========================
INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
VALUES
(1, 145.00, 20),
(2, 82.50, 15),
(3, 60.00, 40),
(4, 25.00, 10),
(5, 0.00, 0),
(6, 95.00, 55),
(7, 130.00, 5);

-- =========================
-- PROFIL PREFERENCE
-- =========================
INSERT INTO ProfilPreference (id_utilisateur, ambiance_preferee, musique_preferee, telephone_autorise)
VALUES
(1, 'calme', TRUE, TRUE),
(2, 'calme', FALSE, TRUE),
(3, 'dynamique', TRUE, TRUE),
(4, 'calme', FALSE, FALSE),
(6, 'dynamique', TRUE, TRUE),
(7, 'calme', TRUE, FALSE);

-- =========================
-- VEHICULES
-- =========================
INSERT INTO Vehicule
(id_utilisateur, modele, type_vehicule, couleur, annee, plaque_immatriculation)
VALUES
(1, 'Hyundai Elantra', 'Berline', 'Gris', 2021, 'UNI123'),
(2, 'Nissan Rogue', 'SUV', 'Noir', 2020, 'RIDE456'),
(7, 'Mazda 3', 'Berline', 'Rouge', 2022, 'GO789QC');

-- =========================
-- DEMANDES DE CERTIFICATION
-- =========================
INSERT INTO DemandeCertification
(id_utilisateur, numero_permis, date_expiration_permis, type_identite, numero_identite, date_expiration_identite, statut_demande, commentaire_admin)
VALUES
(1, 'QC12345001', '2028-09-15', 'passeport', 'DZP998811', '2030-03-20', 'acceptee', 'Dossier complet et validé.'),
(2, 'QC12345002', '2027-12-01', 'assurance_maladie', 'RAMQ112233', '2028-06-11', 'en_attente', NULL),
(7, 'QC12345003', '2029-01-09', 'passeport', 'CAP554433', '2031-02-14', 'refusee', 'Pièce d’identité floue, veuillez renvoyer une image lisible.');

-- =========================
-- TRAJETS
-- =========================
INSERT INTO Trajet
(id_conducteur, id_ville_depart, id_ville_arrivee, id_vehicule, date_trajet, heure_trajet, prix, places_disponibles, ambiance, musique, telephone_autorise, statut)
VALUES
(1, 1, 2, 1, '2026-04-18', '08:30:00', 27.50, 3, 'calme', TRUE, TRUE, 'actif'),
(2, 2, 17, 2, '2026-04-19', '13:15:00', 42.00, 2, 'calme', FALSE, TRUE, 'actif'),
(7, 3, 17, 3, '2026-04-20', '07:45:00', 35.00, 4, 'dynamique', TRUE, FALSE, 'actif'),
(1, 2, 3, 1, '2026-04-21', '17:00:00', 18.00, 2, 'calme', TRUE, TRUE, 'actif');

-- =========================
-- ARRETS TRAJET
-- =========================
INSERT INTO ArretTrajet (id_trajet, id_ville, ordre_arret)
VALUES
(1, 3, 1),
(2, 1, 1),
(3, 2, 1);

-- =========================
-- RESERVATIONS
-- =========================
INSERT INTO Reservation (id_trajet, id_passager, nb_places, statut)
VALUES
(1, 3, 1, 'confirmee'),
(1, 6, 1, 'en_attente'),
(2, 4, 1, 'confirmee'),
(3, 3, 2, 'confirmee'),
(4, 6, 1, 'annulee');

-- =========================
-- PAIEMENTS
-- =========================
INSERT INTO Paiement (id_reservation, montant_argent, montant_points, mode_paiement, statut_paiement)
VALUES
(1, 27.50, 0, 'argent', 'valide'),
(2, 0.00, 15, 'points', 'en_attente'),
(3, 42.00, 0, 'argent', 'valide'),
(4, 20.00, 15, 'mixte', 'valide'),
(5, 18.00, 0, 'argent', 'refuse');

-- =========================
-- HISTORIQUE WALLET
-- =========================
INSERT INTO HistoriqueWallet
(id_wallet, type_operation, montant_argent, montant_points, description)
VALUES
(1, 'depot', 145.00, 0, 'Dépôt initial du conducteur Sarah'),
(3, 'paiement', 27.50, 0, 'Paiement réservation trajet 1'),
(6, 'paiement', 0.00, 15, 'Paiement partiel en points pour réservation 2'),
(4, 'paiement', 42.00, 0, 'Paiement réservation trajet 2'),
(3, 'reception', 0.00, 10, 'Bonus fidélité après trajet confirmé'),
(7, 'retrait', 50.00, 0, 'Demande de retrait vers compte bancaire');

-- =========================
-- RETRAITS
-- =========================
INSERT INTO Retrait
(id_wallet, numero_transit, numero_institution, numero_compte, montant, statut_retrait)
VALUES
(7, '54321', '815', '4567890', 50.00, 'en_attente');

-- =========================
-- EVALUATIONS
-- =========================
INSERT INTO Evaluation
(id_trajet, id_passager, id_conducteur, note, commentaire)
VALUES
(1, 3, 1, 5, 'Très bon trajet, départ à l’heure et voiture propre.'),
(2, 4, 2, 4, 'Conducteur respectueux et trajet confortable.'),
(3, 3, 7, 5, 'Super expérience, je recommande ce conducteur.');

-- =========================
-- REPONSES AVIS
-- =========================
INSERT INTO ReponseAvis
(id_evaluation, id_conducteur, commentaire_reponse)
VALUES
(1, 1, 'Merci beaucoup pour votre retour positif.'),
(2, 2, 'Merci, heureux que le trajet vous ait plu.');

-- =========================
-- QUESTIONS AIDE
-- =========================
INSERT INTO QuestionAide
(id_utilisateur, sujet, message, statut_question)
VALUES
(3, 'Réservation invisible', 'Ma réservation confirmée ne s’affiche pas dans mon profil.', 'ouverte'),
(6, 'Paiement en points', 'Je voudrais savoir combien de points il faut pour payer un trajet.', 'traitee'),
(4, 'Annulation trajet', 'Comment annuler un trajet sans perdre mon argent ?', 'ouverte');

-- =========================
-- PLAINTES
-- =========================
INSERT INTO Plainte
(id_utilisateur, sujet, description, statut_plainte)
VALUES
(4, 'Retard conducteur', 'Le conducteur est arrivé 25 minutes en retard sans prévenir.', 'ouverte'),
(6, 'Erreur de paiement', 'Le montant payé ne correspond pas au prix affiché.', 'traitee');

-- =========================
-- REPONSES PLAINTES
-- =========================
INSERT INTO ReponsePlainte
(id_plainte, id_admin, message_reponse)
VALUES
(1, 5, 'Nous avons contacté le conducteur et ouvert un suivi.'),
(2, 5, 'Le paiement a été vérifié et une correction a été appliquée.');

-- =========================
-- CONVERSATIONS
-- =========================
INSERT INTO Conversation
(id_passager, id_conducteur, id_trajet)
VALUES
(3, 1, 1),
(4, 2, 2),
(6, 1, 4);

-- =========================
-- MESSAGES
-- =========================
INSERT INTO Message
(id_conversation, id_expediteur, contenu)
VALUES
(1, 3, 'Bonjour, le départ se fait bien à Montréal centre ?'),
(1, 1, 'Oui, exactement près du métro Berri-UQAM.'),
(2, 4, 'Bonsoir, avez-vous de la place pour un petit sac en plus ?'),
(2, 2, 'Oui bien sûr, aucun souci.'),
(3, 6, 'Salut, est-ce que vous pouvez attendre 10 minutes si jamais je suis en retard ?'),
(3, 1, 'Oui, mais prévenez-moi à l’avance.');

