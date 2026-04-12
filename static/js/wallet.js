const user = JSON.parse(localStorage.getItem("user"));

let showTransactions = true;

// =============================
// TOGGLE SECTIONS (FIX IMPORTANT)
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
// CHARGEMENT WALLET
async function chargerWallet() {
    const res = await fetch(`/wallet/${user.id_utilisateur}`);
    const data = await res.json();

    // ===== SOLDE =====
    document.getElementById("solde").textContent =
        parseFloat(data.wallet.solde_argent).toFixed(2) + "$";

    // ===== CARTES =====
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

    // CREDIT
    data.cartes_credit.forEach(c => {
        liste.innerHTML += `
            <div class="carte-premium">
                💳 **** ${c.numero_carte.slice(-4)}<br>
                ${c.titulaire}
            </div>
        `;

        selectCredit.innerHTML += `
            <option value="${c.id}">
                **** ${c.numero_carte.slice(-4)}
            </option>
        `;
    });

    // DEBIT
    data.cartes_debit.forEach(c => {
        liste.innerHTML += `
            <div class="carte-premium">
                🏦 **** ${c.numero_compte.slice(-4)}<br>
                ${c.titulaire}
            </div>
        `;

        selectDebit.innerHTML += `
            <option value="${c.id}">
                **** ${c.numero_compte.slice(-4)}
            </option>
        `;
    });

    // ===== TRANSACTIONS =====
    const transDiv = document.getElementById("transactions");
    transDiv.innerHTML = "";

    data.transactions.forEach(t => {
        const color = (t.type_operation === "depot" || t.type_operation === "reception")
            ? "green"
            : "red";

        transDiv.innerHTML += `
            <div class="transaction" style="color:${color}">
                <strong>${t.type_operation.toUpperCase()}</strong> 
                - ${t.montant_argent}$<br>
                <small>${t.description || ""} | ${t.date_operation}</small>
            </div>
        `;
    });
}

// =============================
// DEPOT
function depot() {
    const carte = document.getElementById("carte-credit-select").value;
    const montant = document.getElementById("montant-depot").value;

    document.getElementById("error-credit").textContent = "";
    document.getElementById("error-montant-depot").textContent = "";

    let valid = true;

    if (!carte) {
        document.getElementById("error-credit").textContent =
            "Veuillez sélectionner une carte crédit";
        valid = false;
    }

    if (!montant || montant <= 0) {
        document.getElementById("error-montant-depot").textContent =
            "Le montant doit être supérieur à 0";
        valid = false;
    }

    if (!valid) return;

    fetch("/wallet/depot", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id_utilisateur: user.id_utilisateur,
            montant
        })
    })
    .then(res => res.json())
    .then(() => {
        chargerWallet();
        alert("Dépôt effectué ✅");
    });
}

// =============================
// RETRAIT
function retrait() {
    const carte = document.getElementById("carte-debit-select").value;
    const montant = document.getElementById("montant-retrait").value;

    document.getElementById("error-debit").textContent = "";
    document.getElementById("error-montant-retrait").textContent = "";

    let valid = true;

    if (!carte) {
        document.getElementById("error-debit").textContent =
            "Veuillez sélectionner une carte débit";
        valid = false;
    }

    if (!montant || montant <= 0) {
        document.getElementById("error-montant-retrait").textContent =
            "Montant invalide";
        valid = false;
    }

    if (!valid) return;

    fetch("/wallet/retrait", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id_utilisateur: user.id_utilisateur,
            montant
        })
    })
    .then(res => res.json())
    .then(() => {
        chargerWallet();
        alert("Retrait effectué ✅");
    });
}

// =============================
// AJOUT CARTE CREDIT
function ajouterCarteCredit() {
    const numero = document.getElementById("cc-numero").value;
    const titulaire = document.getElementById("cc-nom").value;
    const exp = document.getElementById("cc-exp").value;

    document.getElementById("error-cc-numero").textContent = "";

    if (!numero || numero.length !== 16) {
        document.getElementById("error-cc-numero").textContent =
            "Le numéro doit contenir 16 chiffres";
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
    })
    .then(res => res.json())
    .then(() => {
        chargerWallet();
        alert("Carte crédit ajoutée ✅");
    });
}

// =============================
// AJOUT CARTE DEBIT
function ajouterCarteDebit() {
    const compte = document.getElementById("cd-compte").value;
    const transit = document.getElementById("cd-transit").value;
    const institution = document.getElementById("cd-institution").value;

    if (!compte || !transit || !institution) {
        alert("Tous les champs sont obligatoires");
        return;
    }

    fetch("/wallet/ajouter-carte-debit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id_utilisateur: user.id_utilisateur,
            compte,
            transit,
            institution
        })
    })
    .then(res => res.json())
    .then(() => {
        chargerWallet();
        alert("Carte débit ajoutée ✅");
    });
}

// =============================
chargerWallet();