const user = JSON.parse(localStorage.getItem("user"));

let showTransactions = true;

// =============================
function toggleSection(id) {
    document.querySelectorAll(".wallet-form").forEach(f => f.classList.add("hidden"));
    document.getElementById(id).classList.remove("hidden");
}

function toggleTransactions() {
    showTransactions = !showTransactions;
    document.getElementById("transactions").style.display =
        showTransactions ? "block" : "none";
}

function toggleCartes() {
    document.getElementById("gestion-cartes").classList.toggle("hidden");
}

function toggleForm(id) {
    document.querySelectorAll("#gestion-cartes .wallet-form")
        .forEach(f => f.classList.add("hidden"));

    document.getElementById(id).classList.remove("hidden");
}

// =============================
// 🎯 FORMAT DATE
function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString("fr-CA") + " à " +
        d.toLocaleTimeString("fr-CA", {hour: '2-digit', minute:'2-digit'});
}

// =============================
// 🎯 NOUVEAU DESIGN TRANSACTIONS
function afficherTransactions(transactions) {
    const container = document.getElementById("transactions");

    if (!transactions || transactions.length === 0) {
        container.innerHTML = "<p>Aucune transaction</p>";
        return;
    }

    let retraits = [];
    let paiements = [];
    let receptions = [];

    transactions.forEach(t => {
        if (t.type_operation === "retrait") {
            retraits.push(t);
        } else if (t.type_operation === "paiement") {
            paiements.push(t);
        } else {
            receptions.push(t); // depot + reception
        }
    });

    function renderSection(title, list, type) {
        if (list.length === 0) return "";

        return `
            <div class="transaction-section">
                <h3>${title}</h3>

                ${list.map(t => {

                    let color = "";
                    let sign = "";

                    if (type === "retrait") {
                        color = "red";
                        sign = "-";
                    } else if (type === "paiement") {
                        color = "orange";
                        sign = "-";
                    } else {
                        color = "green";
                        sign = "+";
                    }

                    return `
                        <div class="transaction-card">

                            <div class="transaction-left">
                                <span class="dot ${color}"></span>

                                <div>
                                    <strong>${title.slice(0, -1)}</strong>
                                    <p>${t.description || "Transaction"}</p>
                                    <small>${formatDate(t.date_operation)}</small>
                                </div>
                            </div>

                            <div class="transaction-right ${color}">
                                ${sign}${parseFloat(t.montant_argent).toFixed(2)}$
                            </div>

                        </div>
                    `;
                }).join("")}
            </div>
        `;
    }

    container.innerHTML =
        renderSection("Retraits", retraits, "retrait") +
        renderSection("Paiements", paiements, "paiement") +
        renderSection("Réceptions", receptions, "reception");
}

// =============================
async function chargerWallet() {
    const res = await fetch(`/wallet/${user.id_utilisateur}`);
    const data = await res.json();

    console.log("DATA:", data);

    // ===== SOLDE =====
    document.getElementById("solde").textContent =
        parseFloat(data.wallet.solde_argent).toFixed(2) + "$";

    const liste = document.getElementById("cartes-liste");
    const msg = document.getElementById("no-cartes-msg");
    const selectCredit = document.getElementById("carte-credit-select");
    const selectDebit = document.getElementById("carte-debit-select");

    liste.innerHTML = "";
    selectCredit.innerHTML = "<option value=''>Choisir carte crédit</option>";
    selectDebit.innerHTML = "<option value=''>Choisir carte débit</option>";

    if (data.cartes_credit.length === 0 && data.cartes_debit.length === 0) {
        msg.textContent = "Aucune carte enregistrée pour le moment";
    } else {
        msg.textContent = "";
    }

    // ===== CARTES CREDIT =====
    data.cartes_credit.forEach(c => {
        if (!c.numero_carte) return;

        liste.innerHTML += `
        <div class="carte-premium credit">
            <div class="card-bg"></div>

            <button class="delete-btn" onclick="supprimerCarteCredit(${c.id})">✕</button>

            <div class="carte-header">
                <div class="chip"></div>
                <div class="card-type">VISA</div>
            </div>

            <div class="carte-number">
                •••• •••• •••• ${c.numero_carte.slice(-4)}
            </div>

            <div class="carte-footer">
                <div class="card-holder">${c.titulaire.toUpperCase()}</div>
            </div>
        </div>
        `;

        selectCredit.innerHTML += `
            <option value="${c.id}">
                **** ${c.numero_carte.slice(-4)}
            </option>
        `;
    });

    // ===== CARTES DEBIT =====
    data.cartes_debit.forEach(c => {
        if (!c.numero_compte) return;

        liste.innerHTML += `
        <div class="carte-premium debit">
            <div class="card-bg"></div>

            <button class="delete-btn" onclick="supprimerCarteDebit(${c.id})">✕</button>

            <div class="carte-header">
                <div class="bank-name">DEBIT</div>
            </div>

            <div class="chip"></div>

            <div class="carte-number">
                •••• •••• •••• ${c.numero_compte.slice(-4)}
            </div>

            <div class="carte-footer">
                <div class="card-holder">${c.titulaire.toUpperCase()}</div>
            </div>
        </div>
        `;

        selectDebit.innerHTML += `
            <option value="${c.id}">
                **** ${c.numero_compte.slice(-4)}
            </option>
        `;
    });

    // ===== TRANSACTIONS (NEW UI) =====
    afficherTransactions(data.transactions);
}

// =============================
function depot() {
    const carte = document.getElementById("carte-credit-select").value;
    const montant = document.getElementById("montant-depot").value;

    if (!carte) return alert("Sélectionne une carte");
    if (!montant || montant <= 0) return alert("Montant invalide");

    fetch("/wallet/depot", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id_utilisateur: user.id_utilisateur,
            montant
        })
    }).then(() => chargerWallet());
}

// =============================
function retrait() {
    const carte = document.getElementById("carte-debit-select").value;
    const montant = document.getElementById("montant-retrait").value;

    if (!carte) return alert("Sélectionne une carte");
    if (!montant || montant <= 0) return alert("Montant invalide");

    fetch("/wallet/retrait", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id_utilisateur: user.id_utilisateur,
            montant
        })
    }).then(() => chargerWallet());
}

// =============================
function ajouterCarteCredit() {
    const numero = document.getElementById("cc-numero").value;
    const titulaire = document.getElementById("cc-nom").value;
    const exp = document.getElementById("cc-exp").value;

    if (!numero || numero.length !== 16) {
        alert("Numéro invalide (16 chiffres)");
        return;
    }

    fetch("/wallet/ajouter-carte-credit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id_utilisateur: user.id_utilisateur,
            numero,
            titulaire,
            expiration: exp
        })
    }).then(() => chargerWallet());
}

// =============================
function ajouterCarteDebit() {
    const compte = document.getElementById("cd-compte").value;
    const transit = document.getElementById("cd-transit").value;
    const institution = document.getElementById("cd-institution").value;

    if (!compte || !transit || !institution) {
        alert("Champs invalides");
        return;
    }

    fetch("/wallet/ajouter-carte-debit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id_utilisateur: user.id_utilisateur,
            titulaire: "Compte bancaire",
            compte,
            transit,
            institution
        })
    }).then(() => chargerWallet());
}

// =============================
document.addEventListener("DOMContentLoaded", () => {
    chargerWallet();
});

// =============================
function supprimerCarteCredit(id) {
    if (!confirm("Supprimer cette carte ?")) return;

    fetch(`/wallet/supprimer-carte-credit/${id}`, {
        method: "DELETE"
    }).then(() => chargerWallet());
}

// =============================
function supprimerCarteDebit(id) {
    if (!confirm("Supprimer cette carte ?")) return;

    fetch(`/wallet/supprimer-carte-debit/${id}`, {
        method: "DELETE"
    }).then(() => chargerWallet());
}