// JavaScript propre à la page d’accueil.
// Défilement fluide et fonctionnalités générales.

class IndexPage {
    constructor() {
        this.init();
    }

    init() {
        this.setupSmoothScrolling();
    }

    // Activer le défilement fluide pour les liens d’ancrage.
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const selector = this.getAttribute('href');
                if (!selector || selector === '#') return;

                const target = document.querySelector(selector);
                if (!target) return;

                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    }
}

// Initialiser lorsque le DOM est chargé.
document.addEventListener('DOMContentLoaded', () => {
    new IndexPage();
});
