# Uniride-projet-
Projet GLO-2005 - plateforme de covoiturage


Équipe:\
Laeticia AOULAICHE \
laeticia.aoulaiche.1@ulaval.ca

Lydia MAACHI\
lydia.maachi.1@ulaval.ca

Amir GABSI\
amir.gabsi.1@ulaval.ca

## Installation et exécution

1. Créer un environnement virtuel (recommandé) :
   - `python -m venv venv`
   - `venv\Scripts\activate` (Windows)
2. Installer les dépendances :
   - `pip install -r requirements.txt`
3. Configurer la base de données MySQL :
   - créer la DB `uniride`
   - exécuter `database/schema.sql`
4. Lancer le serveur :
   - `python app.py`

## Points de correction appliqués

- Ajout de `requirements.txt` pour l’installation des modules.
- Validation et gestion des erreurs dans les routes existantes (auth, trajets, reservation).
- Correction du workflow `register/login` côté front (conforme aux routes API).
