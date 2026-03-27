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

        try {
            const response = await fetch("/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok) {
                message.textContent = "✅ " + (result.message || "Inscription réussie!");
                message.style.color = "green";
                registerForm.reset();
                setTimeout(() => {
                    window.location.href = "/login-page";
                }, 2000);
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
            identifiant: document.getElementById("identifiant").value,
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