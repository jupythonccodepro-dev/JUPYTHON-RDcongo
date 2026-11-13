/**
 * Page de connexion Jupython
 * Gère la connexion des utilisateurs
 */

class LoginPage {
    constructor() {
        this.init();
    }

    init() {
        this.preserveReturnPath();
        this.setupFormValidation();
        this.setupGoogleLogin();
    }

    preserveReturnPath() {
        const next = new URLSearchParams(window.location.search).get('next');
        if (!next) return;
        const accountLink = document.querySelector(`a[href="register.html"]`);
        if (accountLink) accountLink.href = `register.html?next=${encodeURIComponent(next)}`;
    }

    getPostAuthDestination() {
        const requested = new URLSearchParams(window.location.search).get('next');
        if (!requested) return '/academy/dashboard.html';
        try {
            const destination = new URL(requested, window.location.origin);
            const authPages = ['/academy/login.html', '/academy/register.html'];
            if (destination.origin === window.location.origin && !authPages.includes(destination.pathname)) {
                return `${destination.pathname}${destination.search}${destination.hash}`;
            }
        } catch (error) {
            console.warn('Destination de retour ignor?e:', error);
        }
        return '/academy/dashboard.html';
    }

    /**
     * Configure la validation du formulaire
     */
    setupFormValidation() {
        const loginForm = document.querySelector('form');
        if (!loginForm) {
            console.warn('Formulaire de connexion non trouvé');
            return;
        }

        loginForm.addEventListener('submit', (e) => this.handleLoginSubmit(e));
    }

    setupGoogleLogin() {
        const googleButton = document.getElementById('googleLoginBtn');
        if (!googleButton) return;

        window.setupGoogleAuthButton(
            googleButton,
            this.handleGoogleCredentialResponse.bind(this),
        );
    }

    async handleGoogleCredentialResponse(response) {
        try {
            const result = await api.request('/accounts/google-login/', {
                method: 'POST',
                body: JSON.stringify({ id_token: response.credential }),
            });

            if (result && result.access) {
                localStorage.setItem('access_token', result.access);
                localStorage.setItem('refresh_token', result.refresh);
                if (result.user) {
                    localStorage.setItem('user', JSON.stringify(result.user));
                }
                api.token = result.access;
                this.showSuccess(document.querySelector('form'), 'Connexion Google réussie.');
                setTimeout(() => {
                    window.location.href = this.getPostAuthDestination();
                }, 1200);
            } else {
                throw new Error(result?.error || 'Connexion Google impossible');
            }
        } catch (error) {
            console.error('Erreur connexion Google:', error);
            this.showError(null, error?.message || 'Connexion Google impossible');
        }
    }

    /**
     * Gère la soumission du formulaire de connexion
     */
    async handleLoginSubmit(e) {
        e.preventDefault();

        const form = e.target;
        const username = form.querySelector('input[name="username"]') || form.querySelector('input[name="email"]') || form.querySelector('input[type="email"]');
        const password = form.querySelector('input[name="password"]') || form.querySelector('input[type="password"]');
        const submitButton = form.querySelector('button[type="submit"]');

        // Validation
        let isValid = true;

        if (!username || !username.value.trim()) {
            this.showError(username, 'Nom d\'utilisateur ou email requis');
            isValid = false;
        }

        if (!password || !password.value.trim()) {
            this.showError(password, 'Mot de passe requis');
            isValid = false;
        }

        if (!isValid) return;

        // Tentative de connexion
        try {
            submitButton.disabled = true;
            submitButton.textContent = 'Connexion en cours...';

            const result = await api.login(username.value, password.value);

            if (result && result.access) {
                this.showSuccess(form, 'Connexion réussie.');
                setTimeout(() => {
                    window.location.href = this.getPostAuthDestination();
                }, 1200);
            } else {
                throw new Error('Erreur de connexion');
            }
        } catch (error) {
            console.error('Erreur connexion:', error);
            const backendMessage = error?.data?.detail || error?.message || 'Identifiants invalides ou erreur serveur';
            this.showError(form, backendMessage);
            submitButton.disabled = false;
            submitButton.textContent = 'Se connecter';
        }
    }

    /**
     * Affiche une erreur
     */
    showError(element, message) {
        const existing = element?.parentNode?.querySelector('.error-message');
        if (existing) existing.remove();

        if (element) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'text-red-500 text-sm mt-1 error-message';
            errorDiv.textContent = message;
            element.parentNode.insertBefore(errorDiv, element.nextSibling);
            element.classList.add('border-red-500');
        } else {
            // Afficher comme message d'erreur du formulaire
            const errorDiv = document.createElement('div');
            errorDiv.className = 'bg-red-500/20 border border-red-500 text-red-400 px-4 py-2 rounded-lg mb-4';
            errorDiv.textContent = message;
            document.querySelector('form').insertBefore(errorDiv, document.querySelector('form').firstChild);
        }
    }

    /**
     * Affiche un message de succès
     */
    showSuccess(element, message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'bg-green-500/20 border border-green-500 text-green-400 px-4 py-2 rounded-lg mt-4';
        successDiv.textContent = message;
        element.appendChild(successDiv);

        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }
}

// Initialiser au chargement du DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new LoginPage();
    });
} else {
    new LoginPage();
}
