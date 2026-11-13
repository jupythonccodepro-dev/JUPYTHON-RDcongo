/**
 * Catalogue Jupython : découverte des cours, filtres et inscriptions.
 */
class CoursesPage {
    constructor() {
        this.courses = [];
        this.enrolledFormationIds = new Set();
        this.container = document.getElementById('courses-list');
        this.status = document.getElementById('courses-status');
        this.init();
    }

    async init() {
        this.container?.addEventListener('click', (event) => this.handleCourseAction(event));
        this.setupFilters();

        if (!this.container) return;
        this.setMessage('Chargement des cours…');

        try {
            const data = await api.getFormations();
            if (Array.isArray(data)) {
                this.courses = data;
            } else if (data && Array.isArray(data.results)) {
                this.courses = data.results;
            } else {
                throw new Error('Réponse de catalogue invalide');
            }
            if (api.isAuthenticated()) {
                const enrollments = await api.getMyEnrollments();
                this.enrolledFormationIds = new Set(
                    enrollments.map((enrollment) => String(enrollment.formation.id)),
                );
            }
            this.populateFilters();
            this.displayCourses(this.courses);
        } catch (error) {
            console.error('Erreur chargement API formations:', error);
            this.setMessage('Le catalogue est temporairement indisponible. Réessayez dans quelques instants.');
        }
    }

    setupFilters() {
        document.querySelector('[data-course-search]')?.addEventListener('input', () => this.applyFilters());
        document.querySelectorAll('[data-course-filter]').forEach((filter) => {
            filter.addEventListener('change', () => this.applyFilters());
        });
    }

    populateFilters() {
        document.querySelectorAll('[data-course-filter]').forEach((select) => {
            const field = select.dataset.courseFilter;
            const values = [...new Set(this.courses.map((course) => course[field]).filter(Boolean))].sort();
            values.forEach((value) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = value;
                select.appendChild(option);
            });
        });
    }

    applyFilters() {
        const search = document.querySelector('[data-course-search]')?.value.trim().toLocaleLowerCase('fr') || '';
        const selected = Object.fromEntries(
            [...document.querySelectorAll('[data-course-filter]')]
                .map((filter) => [filter.dataset.courseFilter, filter.value]),
        );
        const filtered = this.courses.filter((course) => {
            const searchable = [
                course.title,
                course.platform,
                course.domain,
                course.description,
                ...(Array.isArray(course.skills) ? course.skills : []),
            ].join(' ').toLocaleLowerCase('fr');
            return searchable.includes(search)
                && Object.entries(selected).every(([field, value]) => !value || course[field] === value);
        });
        this.displayCourses(filtered);
    }

    displayCourses(courses) {
        if (!this.container) return;
        this.container.replaceChildren();
        if (this.status) this.status.textContent = `${courses.length} cours trouvés`;

        if (courses.length === 0) {
            this.setMessage(this.courses.length
                ? 'Aucun cours ne correspond à ces filtres.'
                : 'Les cours seront ajoutés au catalogue prochainement.');
            return;
        }

        courses.forEach((course) => this.container.appendChild(this.createCourseCard(course)));
    }

    createCourseCard(course) {
        const card = document.createElement('article');
        card.className = 'jp-course-card flex flex-col p-6';

        const visual = document.createElement('div');
        visual.className = 'jp-course-card__visual';
        const coverUrl = course.hosted_by_jupython
            ? (course.cover_image || '/images/technology-lab.webp')
            : course.cover_image_url;
        if (coverUrl) {
            const cover = document.createElement('img');
            cover.className = 'jp-course-card__image';
            cover.alt = `Visuel du cours ${course.title}`;
            cover.loading = 'lazy';
            cover.src = coverUrl;
            cover.addEventListener('error', () => {
                cover.remove();
                visual.classList.add('jp-course-card__visual--fallback');
            }, { once: true });
            visual.appendChild(cover);
        } else {
            visual.classList.add('jp-course-card__visual--fallback');
        }

        const source = document.createElement('div');
        source.className = 'jp-course-card__source';
        const sourceName = course.hosted_by_jupython ? 'Jupython Academy' : course.platform;
        const logoUrl = course.hosted_by_jupython
            ? '/images/logo%20jupython.png'
            : course.provider_logo_url;
        if (logoUrl) {
            const logo = document.createElement('img');
            logo.className = 'jp-course-card__source-logo';
            logo.src = logoUrl;
            logo.alt = '';
            logo.loading = 'lazy';
            logo.addEventListener('error', () => logo.remove(), { once: true });
            source.appendChild(logo);
        } else {
            const monogram = document.createElement('span');
            monogram.className = 'jp-course-card__source-monogram';
            monogram.setAttribute('aria-hidden', 'true');
            monogram.textContent = sourceName.split(/\s+/).map((word) => word[0]).join('').slice(0, 2).toUpperCase();
            source.appendChild(monogram);
        }
        const sourceLabel = document.createElement('span');
        sourceLabel.textContent = sourceName;
        source.appendChild(sourceLabel);
        visual.appendChild(source);
        card.appendChild(visual);

        const domain = document.createElement('p');
        domain.className = 'jp-feature-card__label mb-3';
        domain.textContent = course.domain || 'Compétences numériques';
        card.appendChild(domain);

        const title = document.createElement('h3');
        title.className = 'font-bold text-xl text-white mb-2';
        title.textContent = course.title;
        card.appendChild(title);

        const description = document.createElement('p');
        description.className = 'text-gray-300 text-sm leading-relaxed mb-4';
        description.textContent = course.description || '';
        card.appendChild(description);

        const details = document.createElement('dl');
        details.className = 'grid grid-cols-2 gap-x-3 gap-y-2 text-sm text-gray-400 mb-4';
        [
            ['Niveau', course.level],
            ['Durée', course.duration],
            ['Langue', course.language],
            ['Accès', course.is_free ? 'Cours gratuit' : 'Accès payant'],
            ...(course.hosted_by_jupython && Array.isArray(course.modules)
                ? [['Modules', `${course.modules.length} modules · ${course.modules.reduce((count, module) => count + module.lesson_count, 0)} leçons`]]
                : []),
        ].forEach(([label, value]) => {
            if (!value) return;
            const term = document.createElement('dt');
            term.textContent = label;
            const definition = document.createElement('dd');
            definition.className = 'text-gray-200';
            definition.textContent = value;
            details.append(term, definition);
        });
        card.appendChild(details);

        if (Array.isArray(course.skills) && course.skills.length) {
            const skills = document.createElement('p');
            skills.className = 'text-gray-300 text-sm mb-4';
            skills.textContent = `Compétences : ${course.skills.join(', ')}`;
            card.appendChild(skills);
        }

        if (course.hosted_by_jupython && course.project_outcome) {
            const project = document.createElement('p');
            project.className = 'rounded-lg border border-orange-400/25 bg-orange-400/5 p-3 text-sm text-orange-100 mb-4';
            project.textContent = `Projet de sortie : ${course.project_outcome}`;
            card.appendChild(project);
        }

        if (course.credential_info) {
            const credential = document.createElement('p');
            credential.className = 'text-gray-400 text-sm border-t border-gray-700 pt-4 mt-auto';
            credential.textContent = `Informations sur la reconnaissance : ${course.credential_info}`;
            card.appendChild(credential);
        }

        if (!course.hosted_by_jupython) {
            const checked = document.createElement('p');
            checked.className = 'text-xs text-gray-500 mt-4';
            checked.textContent = course.last_verified_at
                ? `Lien et informations du cours vérifiés par Jupython le ${new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium' }).format(new Date(course.last_verified_at))}`
                : 'Date de vérification à confirmer';
            card.appendChild(checked);
        }

        const actions = document.createElement('div');
        actions.className = 'flex flex-wrap gap-3 mt-5';
        const alreadyEnrolled = this.enrolledFormationIds.has(String(course.id));
        const courseUrl = this.getSafeCourseUrl(course.link);
        if (course.hosted_by_jupython) {
            const learnLink = document.createElement('a');
            learnLink.href = `academy/learn.html?formation=${encodeURIComponent(course.id)}`;
            learnLink.className = 'jp-button-primary';
            learnLink.textContent = alreadyEnrolled ? 'Continuer le parcours' : 'Découvrir le parcours';
            actions.appendChild(learnLink);
        } else if (courseUrl) {
            const accessLink = document.createElement('a');
            accessLink.href = courseUrl;
            accessLink.target = '_blank';
            accessLink.rel = 'noopener noreferrer';
            accessLink.className = 'jp-button-primary';
            accessLink.textContent = 'Accéder au cours';
            actions.appendChild(accessLink);
        }

        if (!alreadyEnrolled) {
            const enrollButton = document.createElement('button');
            enrollButton.type = 'button';
            enrollButton.dataset.enrollFormation = course.id;
            enrollButton.className = 'rounded-lg border border-orange-400/50 px-4 py-2 font-semibold text-orange-200 hover:bg-orange-400/10';
            enrollButton.textContent = course.hosted_by_jupython ? 'S’inscrire une fois et suivre ici' : 'Ajouter à mon espace';
            actions.appendChild(enrollButton);
        } else if (!course.hosted_by_jupython) {
            const enrolledLabel = document.createElement('span');
            enrolledLabel.className = 'rounded-lg border border-white/10 px-4 py-2 text-sm text-gray-300';
            enrolledLabel.textContent = 'Déjà dans mon espace';
            actions.appendChild(enrolledLabel);
        }
        card.appendChild(actions);
        return card;
    }

    getSafeCourseUrl(value) {
        try {
            const url = new URL(value);
            return url.protocol === 'https:' ? url.href : null;
        } catch {
            return null;
        }
    }

    async handleCourseAction(event) {
        const button = event.target.closest('[data-enroll-formation]');
        if (!button) return;

        if (!api.isAuthenticated()) {
            window.location.href = `/academy/login.html?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;
            return;
        }

        button.disabled = true;
        try {
            const result = await api.enrollCourse(button.dataset.enrollFormation);
            if (!result) return;
            const course = this.courses.find((item) => String(item.id) === String(button.dataset.enrollFormation));
            this.enrolledFormationIds.add(String(course.id));
            button.textContent = result.enrolled
                ? (course.hosted_by_jupython ? 'Inscription enregistrée' : 'Cours ajouté à mon espace')
                : 'Déjà dans mon espace';
            button.disabled = true;
            button.setAttribute('aria-pressed', 'true');
            if (course.hosted_by_jupython) {
                const learnLink = button.parentElement.querySelector(`a[href="academy/learn.html?formation=${encodeURIComponent(course.id)}"]`);
                if (learnLink) {
                    learnLink.textContent = 'Commencer le parcours';
                    learnLink.className = 'jp-button-secondary';
                }
            }
        } catch (error) {
            console.error('Impossible d’ajouter le cours à votre espace:', error);
            button.disabled = false;
            button.textContent = 'Erreur — réessayer';
        }
    }

    setMessage(message) {
        if (this.status) this.status.textContent = message;
        if (!this.container) return;
        this.container.replaceChildren();
        const notice = document.createElement('p');
        notice.className = 'jp-academy-panel p-6 text-gray-300 sm:col-span-2 lg:col-span-3';
        notice.textContent = message;
        this.container.appendChild(notice);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new CoursesPage());
} else {
    new CoursesPage();
}
