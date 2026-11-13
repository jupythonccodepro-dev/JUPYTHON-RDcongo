/**
 * Menu mobile — amélioration de l’affichage adaptatif
 */

class MobileMenu {
    constructor() {
        this.init();
    }

    init() {
        // Créer le bouton de menu mobile si aucune navigation mobile n’existe.
        this.setupMobileMenu();
    }

    setupMobileMenu() {
        const header = document.querySelector('header');
        if (!header) return;

        // Vérifier si le menu mobile existe déjà
        const existingToggle = header.querySelector('[data-mobile-menu-toggle]');
        if (existingToggle) return;

        // Créer le bouton de menu à trois barres.
        const nav = header.querySelector('nav');
        if (!nav) return;

        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.setAttribute('data-mobile-menu-toggle', 'true');
        toggle.setAttribute('aria-label', 'Ouvrir le menu de navigation');
        toggle.setAttribute('aria-controls', 'mobile-nav');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.className = 'md:hidden flex flex-col gap-1 focus:outline-none';
        toggle.innerHTML = `
            <span class="w-6 h-0.5 bg-white transition-transform"></span>
            <span class="w-6 h-0.5 bg-white transition-opacity"></span>
            <span class="w-6 h-0.5 bg-white transition-transform"></span>
        `;

        // Insérer avant la navigation.
        nav.parentNode.insertBefore(toggle, nav);

        // Adapter la navigation aux différentes tailles d’écran.
        nav.classList.add('hidden', 'absolute', 'top-full', 'left-0', 'right-0', 'bg-gray-900', 'flex-col', 'p-4', 'gap-2', 'md:flex', 'md:flex-row', 'md:static', 'md:bg-transparent', 'md:p-0', 'md:gap-6');
        nav.id = 'mobile-nav';

        // Ajouter le gestionnaire d’événement.
        toggle.addEventListener('click', () => this.toggleMenu());
    }

    toggleMenu() {
        const nav = document.getElementById('mobile-nav');
        const toggle = document.querySelector('[data-mobile-menu-toggle]');
        
        if (nav.classList.contains('hidden')) {
            nav.classList.remove('hidden');
            nav.classList.add('flex');
            toggle.classList.add('active');
            toggle.setAttribute('aria-expanded', 'true');
            toggle.setAttribute('aria-label', 'Fermer le menu de navigation');
        } else {
            nav.classList.add('hidden');
            nav.classList.remove('flex');
            toggle.classList.remove('active');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.setAttribute('aria-label', 'Ouvrir le menu de navigation');
        }
    }
}

// Initialiser au chargement du DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new MobileMenu();
    });
} else {
    new MobileMenu();
}
