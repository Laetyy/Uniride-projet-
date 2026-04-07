function utilisateurConnecte() {
    return !!JSON.parse(localStorage.getItem("user"));
}

async function loadTrajets(filteredTrajets = null) {
    const container = document.getElementById("trajetsContainer");

    if (!container) return;

    container.innerHTML = "Chargement...";

    try {
        let trajets = filteredTrajets;

        if (!trajets) {
            const response = await fetch("/trajets");
            const data = await response.json();

            if (!response.ok) {
                container.innerHTML = `<p>Erreur : ${data.error || "Impossible de charger les trajets."}</p>`;
                return;
            }

            trajets = data;
        }

        container.innerHTML = "";

        if (!trajets.length) {
            container.innerHTML = `
                <div class="dashboard-card">
                    <h3>Aucun trajet trouvé</h3>
                    <p>
                        Nous sommes désolés, aucun trajet n’est disponible pour le moment
                        pour cet itinéraire. Essaie avec d’autres villes ou reviens un peu plus tard.
                    </p>
                </div>
            `;
            return;
        }

        const isConnected = utilisateurConnecte();

        trajets.forEach(trajet => {
            const div = document.createElement("div");
            div.className = "trajet-card";

            const photoProfil = trajet.photo_profil && trajet.photo_profil.trim() !== ""
                ? `/static/${trajet.photo_profil}`
                : "/static/images/default-profile.png";

            if (isConnected) {
                div.innerHTML = `
                    <div class="trajet-conducteur-box" onclick="voirProfilConducteur(${trajet.id_conducteur})">
                        <img src="${photoProfil}" alt="Photo du conducteur" class="trajet-conducteur-photo">
                        <div class="trajet-conducteur-info">
                            <strong>${trajet.conducteur || "Non indiqué"}</strong>
                            <span>Voir le profil</span>
                        </div>
                    </div>

                    <h3>${trajet.ville_depart} → ${trajet.ville_arrivee}</h3>
                    <p><strong>Véhicule :</strong> ${trajet.vehicule || "Non indiqué"}</p>
                    <p><strong>Date :</strong> ${trajet.date_trajet || "Non indiquée"}</p>
                    <p><strong>Heure :</strong> ${trajet.heure_trajet || "Non indiquée"}</p>
                    <p><strong>Prix :</strong> ${trajet.prix} $</p>
                    <p><strong>Places disponibles :</strong> ${trajet.places_disponibles}</p>

                    <button class="btn" onclick="reserver(${trajet.id_trajet})">
                        Réserver
                    </button>
                `;
            } else {
                div.innerHTML = `
                    <h3>${trajet.ville_depart} → ${trajet.ville_arrivee}</h3>
                    <p><strong>Date :</strong> ${trajet.date_trajet || "Non indiquée"}</p>
                    <p><strong>Heure :</strong> ${trajet.heure_trajet || "Non indiquée"}</p>
                    <p><strong>Prix :</strong> ${trajet.prix} $</p>
                    <p><strong>Places disponibles :</strong> ${trajet.places_disponibles}</p>
                    <p class="small-text">Connecte-toi pour voir plus de détails sur le conducteur et réserver ce trajet.</p>
                    <a class="btn" href="/login-page">Se connecter</a>
                `;
            }

            container.appendChild(div);
        });

    } catch (error) {
        container.innerHTML = `<p>Erreur de chargement : ${error.message}</p>`;
        console.error(error);
    }
}

function voirProfilConducteur(idConducteur) {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) {
        alert("Connecte-toi pour consulter le profil du conducteur.");
        window.location.href = "/login-page";
        return;
    }

    window.location.href = `/profil-conducteur-page?id=${idConducteur}`;
}

async function reserver(id_trajet) {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) {
        alert("❌ Connecte-toi d'abord");
        return;
    }

    const data = {
        id_trajet: id_trajet,
        id_passager: user.id_utilisateur,
        nb_places: 1
    };

    try {
        const response = await fetch("/reservation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            alert("✅ Réservation réussie");
            lancerRechercheOuToutRecharger();
        } else {
            alert("❌ " + (result.error || "Erreur"));
        }

    } catch (error) {
        console.error(error);
        alert("Erreur serveur");
    }
}

function normaliserTexte(texte) {
    return (texte || "")
        .trim()
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}

async function rechercherTrajets() {
    const departInput = document.getElementById("departInput");
    const destinationInput = document.getElementById("destinationInput");
    const container = document.getElementById("trajetsContainer");

    if (!container) return;

    const depart = departInput ? normaliserTexte(departInput.value) : "";
    const destination = destinationInput ? normaliserTexte(destinationInput.value) : "";

    try {
        const response = await fetch("/trajets");
        const trajets = await response.json();

        if (!response.ok) {
            container.innerHTML = `<p>Erreur : ${trajets.error || "Impossible de charger les trajets."}</p>`;
            return;
        }

        let filteredTrajets = trajets;

        if (depart) {
            filteredTrajets = filteredTrajets.filter(trajet =>
                normaliserTexte(trajet.ville_depart) === depart
            );
        }

        if (destination) {
            filteredTrajets = filteredTrajets.filter(trajet =>
                normaliserTexte(trajet.ville_arrivee) === destination
            );
        }

        loadTrajets(filteredTrajets);

    } catch (error) {
        console.error(error);
        container.innerHTML = `<p>Erreur : ${error.message}</p>`;
    }
}

function lancerRechercheOuToutRecharger() {
    const departInput = document.getElementById("departInput");
    const destinationInput = document.getElementById("destinationInput");

    if (!departInput || !destinationInput) {
        loadTrajets();
        return;
    }

    const depart = departInput.value.trim();
    const destination = destinationInput.value.trim();

    if (depart || destination) {
        rechercherTrajets();
    } else {
        loadTrajets();
    }
}

function initialiserChampsVille() {
    const departInput = document.getElementById("departInput");
    const destinationInput = document.getElementById("destinationInput");
    const searchBtn = document.getElementById("searchTrajetsBtn");

    [departInput, destinationInput].forEach(input => {
        if (!input) return;

        input.addEventListener("focus", function () {
            this.select();
        });

        input.addEventListener("click", function () {
            this.select();
        });

        input.addEventListener("input", function () {
            if (this.value.trim() === "") {
                lancerRechercheOuToutRecharger();
            }
        });

        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                rechercherTrajets();
            }
        });
    });

    if (searchBtn) {
        searchBtn.addEventListener("click", rechercherTrajets);
    }
}

initialiserChampsVille();
loadTrajets();