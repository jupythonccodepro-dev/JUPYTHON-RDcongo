// JavaScript propre à la page Contact.
// Validation du formulaire de contact.

class ContactPage {
    constructor() {
        this.init();
    }

    init() {
        this.setupFormValidation();
        this.setupFormFeedback();
    }

    // Configurer la validation du formulaire.
    setupFormValidation() {
        const contactForm = document.querySelector('form[action="/contact"]');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => this.validateContactForm(e));
        }
    }

    // Valider et envoyer le formulaire de contact.
    async validateContactForm(e) {
        e.preventDefault();

        const form = e.target;
        const name = form.querySelector('input[name="name"]');
        const email = form.querySelector('input[name="email"]');
        const message = form.querySelector('textarea[name="message"]');
        const submitButton = form.querySelector('button[type="submit"]');

        let isValid = true;

        // Validation du nom.
        if (!name.value.trim()) {
            this.showError(name, 'Le nom est requis');
            isValid = false;
        } else {
            this.clearError(name);
        }

        // Validation de l’adresse e-mail.
        if (!this.isValidEmail(email.value)) {
            this.showError(email, 'Veuillez entrer une adresse email valide');
            isValid = false;
        } else {
            this.clearError(email);
        }

        // Validation du message.
        if (!message.value.trim()) {
            this.showError(message, 'Le message est requis');
            isValid = false;
        } else {
            this.clearError(message);
        }

        if (!isValid) return;

        // Envoyer via l’API.
        try {
            submitButton.disabled = true;
            submitButton.textContent = 'Envoi en cours...';

            await api.sendContact({
                name: name.value,
                email: email.value,
                subject: 'Message de contact Jupython',
                message: message.value
            });

            this.showSuccess(form, 'Message envoyé avec succès!');
            form.reset();
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.textContent = 'Envoyer';
            }, 2000);
        } catch (error) {
            console.error('Erreur envoi contact:', error);
            this.showError(form, 'Erreur lors de l\'envoi. Veuillez réessayer.');
            submitButton.disabled = false;
            submitButton.textContent = 'Envoyer';
        }
    }

    // Fonction utilitaire de validation de l’adresse e-mail.
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Afficher un message d’erreur.
    showError(input, message) {
        this.clearError(input);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-red-500 text-xs mt-1 error-message';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
        input.classList.add('border-red-500');
    }

    // Effacer le message d’erreur.
    clearError(input) {
        const existingError = input.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        input.classList.remove('border-red-500');
    }

    // Afficher un message de réussite.
    showSuccess(form, message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'text-green-500 text-sm mt-4 success-message';
        successDiv.textContent = message;
        form.appendChild(successDiv);

        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    // Configurer les retours du formulaire.
    setupFormFeedback() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function () {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Envoi en cours...';
                }
            });
        });
    }
}

// Initialiser lorsque le DOM est chargé.
document.addEventListener('DOMContentLoaded', () => {
    new ContactPage();
});
