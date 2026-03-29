const registerForm = document.getElementById("registerForm");
const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

function motDePasseValide(motDePasse) {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return regex.test(motDePasse);
}

function telephoneCanadienValide(telephone) {
    const regex = /^\+1\d{10}$/;
    return regex.test(telephone);
}

function emailValide(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const nom_utilisateur = document.getElementById("nom_utilisateur").value.trim();
        const email = document.getElementById("email").value.trim().toLowerCase();
        const mot_de_passe = document.getElementById("mot_de_passe").value;
        const nom = document.getElementById("nom").value.trim();
        const prenom = document.getElementById("prenom").value.trim();
        const telephone = document.getElementById("telephone").value.trim();

        if (nom_utilisateur.length > 10) {
            message.textContent = "❌ Le nom d'utilisateur ne doit pas dépasser 10 caractères";
            message.style.color = "red";
            return;
        }

        if (!motDePasseValide(mot_de_passe)) {
            message.textContent = "❌ Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre";
            message.style.color = "red";
            return;
        }

        if (!telephoneCanadienValide(telephone)) {
            message.textContent = "❌ Le numéro doit être au format canadien : +1 suivi de 10 chiffres";
            message.style.color = "red";
            return;
        }

        if (!emailValide(email)) {
            message.textContent = "❌ Adresse email invalide";
            message.style.color = "red";
            return;
        }

        const data = {
            nom_utilisateur,
            email,
            mot_de_passe,
            nom,
            prenom,
            telephone
        };

        try {
            const response = await fetch("/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                message.textContent = "✅ " + (result.message || "Inscription réussie !");
                message.style.color = "green";
                registerForm.reset();
                setTimeout(() => {
                    window.location.href = "/login-page";
                }, 1500);
            } else {
                message.textContent = "❌ " + (result.error || "Erreur");
                message.style.color = "red";
            }
        } catch (error) {
            message.textContent = "❌ Erreur de connexion : " + error.message;
            message.style.color = "red";
        }
    });
}

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            identifiant: document.getElementById("identifiant").value.trim(),
            mot_de_passe: document.getElementById("mot_de_passe").value
        };

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                localStorage.setItem("user", JSON.stringify(result.user));
                message.textContent = "✅ " + result.message;
                message.style.color = "green";
                setTimeout(() => {
                    window.location.href = "/home";
                }, 1000);
            } else {
                message.textContent = "❌ " + (result.error || "Erreur");
                message.style.color = "red";
            }
        } catch (error) {
            message.textContent = "❌ Erreur serveur : " + error.message;
            message.style.color = "red";
        }
    });
}