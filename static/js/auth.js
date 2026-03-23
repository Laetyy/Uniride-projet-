const registerForm = document.getElementById("registerForm");
const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            nom_utilisateur: document.getElementById("nom_utilisateur").value,
            email: document.getElementById("email").value,
            mot_de_passe: document.getElementById("mot_de_passe").value,
            nom: document.getElementById("nom").value,
            prenom: document.getElementById("prenom").value,
            telephone: document.getElementById("telephone").value
        };

        const response = await fetch("/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        message.textContent = result.message || result.error;
    });
}

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            identifiant: document.getElementById("identifiant").value,
            mot_de_passe: document.getElementById("mot_de_passe").value
        };

        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        message.textContent = result.message || result.error;
    });
}