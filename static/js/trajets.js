async function loadTrajets() {
    const container = document.getElementById("trajetsContainer");

    if (!container) return;

    container.innerHTML = "Chargement...";

    try {
        const response = await fetch("/trajets");
        const trajets = await response.json();

        container.innerHTML = "";

        if (!response.ok) {
            container.innerHTML = `<p>Erreur : ${trajets.error || "Impossible de charger les trajets."}</p>`;
            return;
        }

        if (!trajets.length) {
            container.innerHTML = "<p>Aucun trajet disponible.</p>";
            return;
        }

        trajets.forEach(trajet => {
            const div = document.createElement("div");
            div.className = "trajet-card";

            const photoProfil = trajet.photo_profil && trajet.photo_profil.trim() !== ""
                ? `/${trajet.photo_profil}`
                : "/static/images/default-profile.png";

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

            container.appendChild(div);
        });

    } catch (error) {
        container.innerHTML = `<p>Erreur de chargement : ${error.message}</p>`;
        console.error(error);
    }
}

function voirProfilConducteur(idConducteur) {
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
            loadTrajets();
        } else {
            alert("❌ " + (result.error || "Erreur"));
        }

    } catch (error) {
        console.error(error);
        alert("Erreur serveur");
    }
}

loadTrajets();