// JavaScript propre à la page À propos.
// Interactions de base de la page À propos.

class AboutPage {
    constructor() {
        this.init();
    }

    init() {
        // Ajouter ici les fonctionnalités propres à la page À propos.
        this.setupTimelineAnimation();
    }

    // Configurer l’animation de la chronologie, si nécessaire.
    setupTimelineAnimation() {
        // Ajouter une animation d’apparition progressive aux éléments de la chronologie.
        const timelineItems = document.querySelectorAll('.bg-gray-800.rounded-xl');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        });

        timelineItems.forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(item);
        });
    }
}

// Initialiser lorsque le DOM est chargé.
document.addEventListener('DOMContentLoaded', () => {
    new AboutPage();
});
