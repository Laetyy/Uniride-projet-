async function chargerProfilConducteur() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");

    const container = document.getElementById("profil-conducteur-container");

    if (!container) return;

    if (!id) {
        container.innerHTML = "<p>Conducteur introuvable.</p>";
        return;
    }

    container.innerHTML = "<p>Chargement du profil...</p>";

    try {
        const response = await fetch(`/profil-conducteur/${id}`);
        const data = await response.json();

        if (!response.ok) {
            container.innerHTML = `<p>${data.error || "Erreur lors du chargement."}</p>`;
            return;
        }

        const conducteur = data.conducteur;
        const stats = data.stats;
        const avis = data.avis;

        const photo = conducteur.photo_profil
            ? `/static/${conducteur.photo_profil}`
            : "/static/images/default-profile.png";

        // ===== AVIS =====
        let avisHtml = "";
        if (!avis || avis.length === 0) {
            avisHtml = "<p>Aucun avis pour le moment.</p>";
        } else {
            avisHtml = avis.map(a => `
                <div class="avis-card">
                    <p><strong>${a.auteur}</strong> — ⭐ ${a.note}/5</p>
                    <p>${a.commentaire || "Aucun commentaire"}</p>
                </div>
            `).join("");
        }

        // ===== DESCRIPTION TRAJET =====
        let descriptionVoyage = "<p>Aucune info disponible.</p>";

        if (stats.trajet_info) {
            descriptionVoyage = `
                <p><strong>Ambiance :</strong> ${stats.trajet_info.ambiance || "Non indiquée"}</p>
                <p><strong>Musique :</strong> ${stats.trajet_info.musique ? "Oui" : "Non"}</p>
                <p><strong>Appels autorisés :</strong> ${stats.trajet_info.telephone_autorise ? "Oui" : "Non"}</p>
                <p><strong>Date dernier trajet :</strong> ${stats.trajet_info.date_trajet || "Non indiquée"}</p>
                <p><strong>Heure :</strong> ${stats.trajet_info.heure_trajet || "Non indiquée"}</p>
            `;
        }

        // ===== HTML FINAL =====
        container.innerHTML = `
            <div class="profil-card">

                <div class="profil-top">
                    <img src="${photo}" class="profil-photo-large">

                    <div class="profil-info">
                        <h2>${conducteur.prenom || ""} ${conducteur.nom || ""}</h2>
                        <p><strong>Username :</strong> ${conducteur.nom_utilisateur}</p>
                        <p><strong>Bio :</strong> ${conducteur.bio || "Aucune bio"}</p>
                        <p><strong>Note :</strong> ⭐ ${stats.moyenne_avis} (${stats.nb_avis} avis)</p>
                    </div>
                </div>

                <div class="profil-stats">
                    <h3>Infos conducteur</h3>
                    <p><strong>Trajets :</strong> ${stats.nb_trajets}</p>
                    <p><strong>Places totales :</strong> ${stats.total_places}</p>
                    <p><strong>Voiture :</strong> ${stats.vehicule}</p>

                    ${descriptionVoyage}
                </div>

                <div class="profil-avis">
                    <h3>Avis clients</h3>
                    ${avisHtml}
                </div>

            </div>
        `;

    } catch (error) {
        console.error(error);
        container.innerHTML = "<p>Erreur serveur.</p>";
    }
}

// lancer automatiquement
chargerProfilConducteur();