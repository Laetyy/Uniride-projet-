async function loadTrajets() {
    const container = document.getElementById("trajetsContainer");
    container.innerHTML = "Chargement...";

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
        `;
        container.appendChild(div);
    });
}

loadTrajets();