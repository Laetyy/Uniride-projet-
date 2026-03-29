async function loadTrajets() {
    const container = document.getElementById("trajetsContainer");
    container.innerHTML = "Chargement...";

    try {
        const response = await fetch("/trajets");
        const trajets = await response.json();

        container.innerHTML = "";

        if (!trajets.length) {
            container.innerHTML = "<p>Aucun trajet disponible.</p>";
            return;
        }

        trajets.forEach(trajet => {
            const div = document.createElement("div");
            div.className = "card";

            div.innerHTML = `
                <h3>${trajet.ville_depart} → ${trajet.ville_arrivee}</h3>
                <p><strong>Conducteur :</strong> ${trajet.conducteur}</p>
                <p><strong>Date :</strong> ${trajet.date_trajet}</p>
                <p><strong>Heure :</strong> ${trajet.heure_trajet}</p>
                <p><strong>Prix :</strong> ${trajet.prix} $</p>
                <p><strong>Places :</strong> ${trajet.places_disponibles}</p>
                <p><strong>Ambiance :</strong> ${trajet.ambiance}</p>

                <button class="btn" onclick="reserver(${trajet.id_trajet})">
                    Réserver
                </button>
            `;

            container.appendChild(div);
        });

    } catch (error) {
        container.innerHTML = "<p>Erreur de chargement : " + error.message + "</p>";
    }
}

// 🔥 fonction réservation
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
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            alert("✅ Réservation réussie");
            loadTrajets(); // recharge les trajets (places mises à jour)
        } else {
            alert("❌ " + (result.error || "Erreur"));
        }

    } catch (error) {
        alert("Erreur serveur");
        console.error(error);
    }
}

loadTrajets();