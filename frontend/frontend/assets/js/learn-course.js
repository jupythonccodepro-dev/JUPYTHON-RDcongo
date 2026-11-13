class JupythonLearningPage {
    constructor() {
        this.formationId = new URLSearchParams(window.location.search).get('formation');
        this.formation = null;
        this.enrollment = null;
        this.completedLessonIds = new Set();
        this.passedModuleIds = new Set();
        this.quizByModule = new Map();
        this.loadingQuizModuleIds = new Set();
        this.modulesContainer = document.querySelector('[data-course-modules]');
        this.feedback = document.querySelector('[data-course-feedback]');
        this.journeyContainer = document.querySelector('[data-course-journey]');
        this.motivation = document.querySelector('[data-learning-motivation]');
        this.init();
    }

    async init() {
        if (!this.formationId || !/^\d+$/.test(this.formationId)) {
            this.showError('Le cours demandé est introuvable.');
            return;
        }

        try {
            if (localStorage.getItem('refresh_token')) {
                await api.restoreSession();
            }
            this.formation = await api.getFormation(this.formationId);
            if (!this.formation || !this.formation.hosted_by_jupython) {
                this.showError('Ce cours ne dispose pas encore de leçons hébergées par Jupython.');
                return;
            }

            if (api.isAuthenticated()) {
                const enrollments = await api.getMyEnrollments();
                this.enrollment = enrollments.find(
                    (item) => String(item.formation.id) === String(this.formation.id),
                );
                this.completedLessonIds = new Set(this.enrollment?.progress?.completed_lesson_ids || []);
                this.passedModuleIds = new Set(this.enrollment?.progress?.passed_module_ids || []);
            }

            this.render();
            this.modulesContainer.addEventListener('click', (event) => this.handleLessonAction(event));
            this.modulesContainer.addEventListener('submit', (event) => this.handleQuizSubmit(event));
            this.modulesContainer.addEventListener('toggle', (event) => {
                const lessonCard = event.target.closest('.jp-lesson-card');
                if (!lessonCard) return;
                const expandLabel = lessonCard.querySelector('.jp-lesson-card__expand');
                if (expandLabel) expandLabel.textContent = lessonCard.open ? 'Réduire' : 'Lire';
            }, true);
            document.title = `${this.formation.title} - Jupython Academy`;
        } catch (error) {
            console.error('Impossible de charger le cours Jupython:', error);
            this.showError('Impossible de charger ce cours pour le moment. Réessaie plus tard.');
        }
    }

    render() {
        document.querySelector('[data-course-title]').textContent = this.formation.title;
        document.querySelector('[data-course-description]').textContent = this.formation.description;
        document.querySelector('[data-course-level]').textContent =
            `${this.formation.level || 'Parcours'} · ${this.formation.duration || 'À votre rythme'} · ${this.formation.modules.length} modules`;
        const prerequisites = document.querySelector('[data-course-prerequisites]');
        prerequisites.replaceChildren();
        if (this.formation.prerequisites) {
            const label = document.createElement('strong');
            label.className = 'text-white';
            label.textContent = 'Avant de commencer : ';
            prerequisites.append(label, document.createTextNode(this.formation.prerequisites));
        } else {
            prerequisites.classList.add('hidden');
        }
        const project = document.querySelector('[data-course-project]');
        project.replaceChildren();
        if (this.formation.project_outcome) {
            const label = document.createElement('strong');
            label.className = 'text-orange-200';
            label.textContent = 'Projet de sortie : ';
            project.append(label, document.createTextNode(this.formation.project_outcome));
        } else {
            project.classList.add('hidden');
        }

        const enrollmentBox = document.querySelector('[data-course-enrollment]');
        enrollmentBox.className = 'mt-5';
        enrollmentBox.replaceChildren();
        if (!this.enrollment) {
            const enrollButton = document.createElement('button');
            enrollButton.type = 'button';
            enrollButton.className = 'jp-button-primary';
            enrollButton.textContent = api.isAuthenticated() ? 'M’inscrire à ce parcours' : 'Se connecter pour suivre ma progression';
            enrollButton.addEventListener('click', async () => {
                if (!api.isAuthenticated()) {
                    window.location.href = `/academy/login.html?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;
                    return;
                }
                enrollButton.disabled = true;
                try {
                    await api.enrollCourse(this.formation.id);
                    this.enrollment = (await api.getMyEnrollments()).find(
                        (item) => String(item.formation.id) === String(this.formation.id),
                    );
                    this.formation = await api.getFormation(this.formation.id);
                    this.completedLessonIds = new Set(this.enrollment?.progress?.completed_lesson_ids || []);
                    this.passedModuleIds = new Set(this.enrollment?.progress?.passed_module_ids || []);
                    this.feedback.textContent = 'Inscription enregistrée. Tu peux maintenant suivre tes leçons.';
                    this.render();
                } catch (error) {
                    console.error('Impossible de s’inscrire au parcours:', error);
                    enrollButton.disabled = false;
                    this.feedback.textContent = error.message || 'L’inscription a échoué. Réessaie.';
                }
            });
            enrollmentBox.appendChild(enrollButton);
        } else {
            const label = document.createElement('p');
            label.className = 'rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-4 text-sm font-semibold text-emerald-200';
            label.textContent = 'Tu es inscrit à ce parcours. Termine les leçons et réussis le test de chaque module pour débloquer le suivant.';
            enrollmentBox.appendChild(label);
        }

        this.modulesContainer.replaceChildren();
        this.formation.modules.forEach((module, moduleIndex) => {
            const section = document.createElement('section');
            section.id = `course-module-${module.id}`;
            section.className = 'jp-academy-panel jp-learning-module p-5 md:p-8';
            const moduleUnlocked = this.isModuleUnlocked(moduleIndex);
            const moduleLessonsDone = module.lessons.length > 0
                && module.lessons.every((lesson) => this.completedLessonIds.has(lesson.id));
            const modulePassed = this.passedModuleIds.has(module.id);
            const moduleHeader = document.createElement('div');
            moduleHeader.className = 'jp-learning-module__header';
            const moduleNumber = document.createElement('span');
            moduleNumber.className = modulePassed
                ? 'jp-learning-module__number jp-learning-module__number--done'
                : 'jp-learning-module__number';
            moduleNumber.textContent = modulePassed ? '✓' : String(moduleIndex + 1).padStart(2, '0');
            const moduleCopy = document.createElement('div');
            moduleCopy.className = 'min-w-0 flex-1';
            const moduleEyebrow = document.createElement('p');
            moduleEyebrow.className = modulePassed
                ? 'text-xs font-bold uppercase tracking-[0.16em] text-emerald-300'
                : 'text-xs font-bold uppercase tracking-[0.16em] text-orange-300';
            moduleEyebrow.textContent = modulePassed
                ? 'Module validé'
                : moduleLessonsDone ? 'Leçons terminées · test à réussir' : `Étape ${moduleIndex + 1} sur ${this.formation.modules.length}`;
            const heading = document.createElement('h2');
            heading.className = 'mt-1 text-xl font-bold text-white md:text-2xl';
            heading.textContent = module.title;
            moduleCopy.append(moduleEyebrow, heading);
            const moduleCount = document.createElement('span');
            moduleCount.className = 'jp-learning-module__count';
            moduleCount.textContent = `${this.completedLessonCount(module)}/${module.lesson_count || module.lessons.length} leçons`;
            moduleHeader.append(moduleNumber, moduleCopy, moduleCount);
            const description = document.createElement('p');
            description.className = 'mb-5 mt-3 text-sm leading-relaxed text-gray-400';
            description.textContent = module.description;
            section.append(moduleHeader, description);
            this.renderModuleVisual(section, module);

            if (!module.lessons.length && module.lesson_count) {
                const loading = document.createElement('p');
                loading.className = 'text-gray-300';
                loading.textContent = 'Chargement du contenu du module…';
                section.appendChild(loading);
                this.modulesContainer.appendChild(section);
                return;
            }

            module.lessons.forEach((lesson) => {
                const completed = this.completedLessonIds.has(lesson.id);
                const card = document.createElement('details');
                card.className = completed
                    ? 'jp-lesson-card jp-lesson-card--done'
                    : 'jp-lesson-card';
                card.open = this.shouldOpenLesson(module, lesson, moduleIndex);
                const title = document.createElement('h3');
                title.className = 'jp-lesson-card__title';
                title.textContent = lesson.title;
                const duration = document.createElement('p');
                duration.className = 'jp-lesson-card__duration';
                duration.textContent = `${lesson.duration_minutes} min`;
                const summary = document.createElement('summary');
                summary.className = 'jp-lesson-card__summary';
                const lessonStatus = document.createElement('span');
                lessonStatus.className = completed
                    ? 'jp-lesson-card__status jp-lesson-card__status--done'
                    : 'jp-lesson-card__status';
                lessonStatus.textContent = completed ? '✓' : String(lesson.order).padStart(2, '0');
                lessonStatus.setAttribute('aria-label', completed ? 'Leçon terminée' : `Leçon ${lesson.order}`);
                const lessonCopy = document.createElement('span');
                lessonCopy.className = 'min-w-0 flex-1';
                lessonCopy.append(title, duration);
                const expandLabel = document.createElement('span');
                expandLabel.className = 'jp-lesson-card__expand';
                expandLabel.textContent = card.open ? 'Réduire' : 'Lire';
                summary.append(lessonStatus, lessonCopy, expandLabel);
                const lessonBody = document.createElement('div');
                lessonBody.className = 'jp-lesson-card__body';
                const content = document.createElement('p');
                content.className = 'text-gray-300 leading-relaxed whitespace-pre-line mt-4';
                content.textContent = lesson.content || lesson.content_preview || '';
                lessonBody.appendChild(content);
                if (completed) {
                    const completedLabel = document.createElement('p');
                    completedLabel.className = 'mt-3 text-sm font-semibold text-emerald-300';
                    completedLabel.textContent = 'Bien joué, cette étape est validée.';
                    lessonBody.appendChild(completedLabel);
                }

                if (lesson.content_locked) {
                    const previewNotice = document.createElement('p');
                    previewNotice.className = 'mt-4 rounded-lg border border-orange-400/25 bg-orange-400/5 p-4 text-sm text-orange-100';
                    previewNotice.textContent = 'Aperçu de la leçon. Connecte-toi pour lire le contenu complet, les objectifs et l’exercice.';
                    const loginLink = document.createElement('a');
                    loginLink.href = '/academy/login.html';
                    loginLink.className = 'mt-3 inline-block text-sm font-semibold text-orange-200 underline hover:text-white';
                    loginLink.textContent = 'Se connecter ou créer un compte';
                    lessonBody.append(previewNotice, loginLink);
                }

                if (lesson.learning_objectives?.length) {
                    const objectives = document.createElement('ul');
                    objectives.className = 'jp-lesson-objectives';
                    lesson.learning_objectives.forEach((objective) => {
                        const item = document.createElement('li');
                        item.textContent = objective;
                        objectives.appendChild(item);
                    });
                    lessonBody.appendChild(objectives);
                }

                if (lesson.exercise) {
                    const exercise = document.createElement('p');
                    exercise.className = 'jp-lesson-exercise';
                    const exerciseLabel = document.createElement('strong');
                    exerciseLabel.className = 'block text-orange-200';
                    exerciseLabel.textContent = 'Atelier pratique';
                    const exerciseText = document.createElement('span');
                    exerciseText.textContent = lesson.exercise;
                    exercise.append(exerciseLabel, exerciseText);
                    lessonBody.appendChild(exercise);
                }

                const button = document.createElement('button');
                button.type = 'button';
                button.dataset.lessonProgress = lesson.id;
                button.dataset.completed = String(completed);
                button.className = completed
                    ? 'jp-lesson-complete jp-lesson-complete--done'
                    : 'jp-lesson-complete';
                button.textContent = completed ? 'Étape terminée ✓ · Reprendre' : 'J’ai terminé cette leçon';
                button.disabled = !this.enrollment || !moduleUnlocked;
                lessonBody.appendChild(button);
                card.append(summary, lessonBody);
                section.appendChild(card);
            });
            if (!this.enrollment) {
                const locked = document.createElement('p');
                locked.className = 'mt-5 rounded-lg border border-orange-400/25 bg-orange-400/5 p-4 text-orange-100';
                locked.textContent = 'Les leçons sont consultables. Inscris-toi gratuitement pour enregistrer ta progression et passer les tests.';
                section.appendChild(locked);
            } else if (!this.isModuleUnlocked(moduleIndex)) {
                const locked = document.createElement('p');
                locked.className = 'mt-5 rounded-lg border border-white/10 bg-black/20 p-4 text-gray-300';
                locked.textContent = 'Tu peux consulter ces leçons. Termine les leçons du module précédent et réussis son test pour poursuivre ta progression.';
                section.appendChild(locked);
            }
            if (
                this.enrollment
                && this.isModuleUnlocked(moduleIndex)
                &&
                module.lessons.length
                && module.lessons.every((lesson) => this.completedLessonIds.has(lesson.id))
            ) {
                this.renderModuleQuiz(section, module);
            }
            this.modulesContainer.appendChild(section);
        });
        this.updateProgress();
    }

    renderModuleVisual(section, module) {
        const lessonCount = module.lesson_count || module.lessons.length || 2;
        const steps = Array.from({ length: lessonCount }, (_, index) => (
            module.lessons[index]?.title || `Leçon ${index + 1}`
        ));
        steps.push('Réussir le test du module', 'Débloquer le module suivant');

        const rowHeight = 62;
        const top = 48;
        const height = top + steps.length * rowHeight + 18;
        const escapeXml = (value) => String(value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&apos;');
        const rows = steps.map((step, index) => {
            const y = top + index * rowHeight;
            const isMilestone = index >= lessonCount;
            const color = isMilestone ? '#f97316' : '#fb923c';
            const label = isMilestone
                ? (index === lessonCount ? 'VALIDATION' : 'ÉTAPE SUIVANTE')
                : `LEÇON ${index + 1}`;
            return `
                <rect x="26" y="${y}" width="708" height="52" rx="13" fill="#111827" stroke="#334155"/>
                <circle cx="56" cy="${y + 26}" r="16" fill="${color}" fill-opacity=".16" stroke="${color}" stroke-opacity=".65"/>
                <text x="56" y="${y + 31}" text-anchor="middle" fill="#fed7aa" font-size="14" font-weight="700">${index + 1}</text>
                <text x="88" y="${y + 21}" fill="${color}" font-size="12" font-weight="700" letter-spacing="1">${label}</text>
                <text x="88" y="${y + 40}" fill="#f8fafc" font-size="16" font-weight="600">${escapeXml(step)}</text>
            `;
        }).join('');
        const svg = `
            <svg xmlns="http://www.w3.org/2000/svg" width="760" height="${height}" viewBox="0 0 760 ${height}" font-family="Inter, Segoe UI, Arial, sans-serif" role="img">
                <defs>
                    <linearGradient id="course-visual-bg" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0" stop-color="#0f172a"/>
                        <stop offset="1" stop-color="#1e293b"/>
                    </linearGradient>
                </defs>
                <rect width="760" height="${height}" rx="20" fill="url(#course-visual-bg)"/>
                <text x="28" y="30" fill="#cbd5e1" font-size="13" font-weight="700" letter-spacing="1.5">REPÈRES VISUELS DU MODULE</text>
                ${rows}
            </svg>
        `;
        const figure = document.createElement('figure');
        figure.className = 'mb-6 overflow-hidden rounded-2xl border border-white/10';
        const image = document.createElement('img');
        image.className = 'block h-auto w-full';
        image.alt = `Schéma du module ${module.order} : ${steps.join(', puis ')}`;
        image.loading = 'lazy';
        image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
        figure.appendChild(image);
        section.appendChild(figure);
    }

    isModuleUnlocked(moduleIndex) {
        if (!this.enrollment || moduleIndex === 0) return Boolean(this.enrollment && moduleIndex === 0);
        const previousModule = this.formation.modules[moduleIndex - 1];
        return this.passedModuleIds.has(previousModule.id)
            && previousModule.lessons.length > 0
            && previousModule.lessons.every((lesson) => this.completedLessonIds.has(lesson.id));
    }

    completedLessonCount(module) {
        return module.lessons.filter((lesson) => this.completedLessonIds.has(lesson.id)).length;
    }

    shouldOpenLesson(module, lesson, moduleIndex) {
        if (!this.enrollment) return moduleIndex === 0 && module.lessons[0]?.id === lesson.id;
        if (!this.isModuleUnlocked(moduleIndex)) return false;
        const firstIncomplete = module.lessons.find(
            (item) => !this.completedLessonIds.has(item.id),
        );
        return firstIncomplete?.id === lesson.id;
    }

    renderJourney() {
        if (!this.journeyContainer) return;
        this.journeyContainer.replaceChildren();
        const heading = document.createElement('h2');
        heading.className = 'mb-3 text-sm font-bold uppercase tracking-[0.16em] text-gray-400';
        heading.textContent = 'Ton parcours en un coup d’œil';
        const steps = document.createElement('div');
        steps.className = 'jp-learning-journey';
        const currentIndex = this.formation.modules.findIndex((module) => !this.passedModuleIds.has(module.id));

        this.formation.modules.forEach((module, index) => {
            const passed = this.passedModuleIds.has(module.id);
            const current = !passed && (currentIndex === -1 ? index === 0 : index === currentIndex);
            const step = document.createElement('a');
            step.href = `#course-module-${module.id}`;
            step.className = passed
                ? 'jp-learning-journey__step jp-learning-journey__step--done'
                : current ? 'jp-learning-journey__step jp-learning-journey__step--current' : 'jp-learning-journey__step';
            const number = document.createElement('span');
            number.className = 'jp-learning-journey__number';
            number.textContent = passed ? '✓' : String(index + 1);
            const text = document.createElement('span');
            text.className = 'jp-learning-journey__text';
            const title = document.createElement('strong');
            title.textContent = module.title;
            const status = document.createElement('small');
            status.textContent = passed ? 'Validé' : current ? 'À continuer' : 'À découvrir';
            text.append(title, status);
            step.append(number, text);
            steps.appendChild(step);
        });
        this.journeyContainer.append(heading, steps);
    }

    updateMotivation() {
        if (!this.motivation) return;
        if (!this.enrollment) {
            this.motivation.textContent = 'Commence par une leçon à ton rythme. Inscris-toi gratuitement pour enregistrer tes étapes et débloquer les tests.';
            return;
        }

        const lessons = this.formation.modules.flatMap((module) => module.lessons);
        const completed = lessons.filter((lesson) => this.completedLessonIds.has(lesson.id)).length;
        const nextLesson = lessons.find((lesson) => !this.completedLessonIds.has(lesson.id));
        const allModulesPassed = this.formation.modules.every((module) => this.passedModuleIds.has(module.id));
        if (completed === lessons.length && allModulesPassed) {
            this.motivation.textContent = 'Parcours terminé ! Tu as avancé leçon après leçon et validé chaque module. Prends un instant pour célébrer ce que tu as appris.';
        } else if (nextLesson) {
            this.motivation.textContent = completed === 0
                ? `Prêt à commencer ? Ouvre « ${nextLesson.title} », avance à ton rythme, puis valide la leçon quand tu as terminé.`
                : `Belle progression : ${completed} leçon${completed > 1 ? 's' : ''} terminée${completed > 1 ? 's' : ''}. Prochaine étape : « ${nextLesson.title} ».`;
        } else {
            this.motivation.textContent = 'Toutes les leçons sont terminées. Réussis les tests restants pour valider ton parcours.';
        }
    }

    renderModuleQuiz(section, module) {
        const quiz = this.quizByModule.get(module.id);
        const panel = document.createElement('div');
        panel.className = 'mt-6 rounded-xl border border-orange-400/30 bg-orange-400/5 p-5';
        const heading = document.createElement('h3');
        heading.className = 'text-lg font-bold text-white';
        heading.textContent = `Test du module ${module.order}`;
        panel.appendChild(heading);

        if (!quiz) {
            const loading = document.createElement('p');
            loading.className = 'mt-3 text-sm text-gray-300';
            loading.textContent = 'Chargement du test…';
            panel.appendChild(loading);
            section.appendChild(panel);
            if (!this.loadingQuizModuleIds.has(module.id)) {
                this.loadingQuizModuleIds.add(module.id);
                api.getModuleQuiz(module.id).then((data) => {
                    this.quizByModule.set(module.id, data);
                    this.render();
                }).catch((error) => {
                    console.error('Impossible de charger le test du module:', error);
                    this.quizByModule.set(module.id, { error: error.message || 'Test momentanément indisponible.' });
                    this.render();
                }).finally(() => this.loadingQuizModuleIds.delete(module.id));
            }
            return;
        }

        if (quiz.error) {
            const errorMessage = document.createElement('p');
            errorMessage.className = 'mt-3 text-sm text-red-200';
            errorMessage.textContent = quiz.error;
            const retry = document.createElement('button');
            retry.type = 'button';
            retry.dataset.retryModuleQuiz = module.id;
            retry.className = 'mt-3 rounded-lg border border-white/20 px-4 py-2 text-sm text-white';
            retry.textContent = 'Réessayer';
            panel.append(errorMessage, retry);
            section.appendChild(panel);
            return;
        }

        const instructions = document.createElement('p');
        instructions.className = 'mt-2 text-sm text-gray-300';
        instructions.textContent = `Réponds aux ${quiz.questions.length} questions. Il faut au moins 2 bonnes réponses sur 3 pour débloquer le module suivant. Tu peux retenter le test.`;
        panel.appendChild(instructions);
        if (quiz.passed) {
            const passedLabel = document.createElement('p');
            passedLabel.className = 'mt-3 text-sm font-semibold text-green-300';
            passedLabel.textContent = `Test réussi · meilleur résultat : ${quiz.best_score}%`;
            panel.appendChild(passedLabel);
        } else if (quiz.attempts > 0) {
            const previousResult = document.createElement('p');
            previousResult.className = 'mt-3 text-sm text-orange-200';
            previousResult.textContent = `Meilleur résultat : ${quiz.best_score}% · nouvelle tentative disponible`;
            panel.appendChild(previousResult);
        }

        const form = document.createElement('form');
        form.dataset.moduleQuiz = module.id;
        form.className = 'mt-4 space-y-5';
        quiz.questions.forEach((question, questionIndex) => {
            const fieldset = document.createElement('fieldset');
            fieldset.className = 'space-y-2';
            const legend = document.createElement('legend');
            legend.className = 'font-semibold text-white';
            legend.textContent = `${questionIndex + 1}. ${question.prompt}`;
            fieldset.appendChild(legend);
            question.choices.forEach((choice, choiceIndex) => {
                const label = document.createElement('label');
                label.className = 'flex cursor-pointer items-start gap-2 text-sm text-gray-200';
                const input = document.createElement('input');
                input.type = 'radio';
                input.name = `quiz-${module.id}-${question.id}`;
                input.value = choiceIndex;
                input.required = true;
                input.className = 'mt-1 accent-orange-400';
                label.append(input, document.createTextNode(choice));
                fieldset.appendChild(label);
            });
            form.appendChild(fieldset);
        });
        const submit = document.createElement('button');
        submit.type = 'submit';
        submit.className = 'jp-button-primary';
        submit.textContent = quiz.passed ? 'Refaire le test' : 'Valider mes réponses';
        form.appendChild(submit);
        panel.appendChild(form);
        section.appendChild(panel);
    }

    async handleLessonAction(event) {
        const retryButton = event.target.closest('[data-retry-module-quiz]');
        if (retryButton) {
            const moduleId = Number(retryButton.dataset.retryModuleQuiz);
            this.quizByModule.delete(moduleId);
            this.render();
            return;
        }
        const button = event.target.closest('[data-lesson-progress]');
        if (!button || !this.enrollment) return;
        button.disabled = true;
        try {
            const lessonId = Number(button.dataset.lessonProgress);
            const wasCompleted = button.dataset.completed === 'true';
            const result = wasCompleted
                ? await api.reopenLesson(lessonId)
                : await api.completeLesson(lessonId);
            if (result.completed) {
                this.completedLessonIds.add(lessonId);
            } else {
                this.completedLessonIds.delete(lessonId);
            }
            this.enrollment.progress = {
                completed_lessons: result.completed_lessons,
                total_lessons: result.total_lessons,
                percent: result.percent,
                has_curriculum: true,
                completed_lesson_ids: [...this.completedLessonIds],
                passed_module_ids: [...this.passedModuleIds],
            };
            this.enrollment.status = result.status;
            this.feedback.textContent = result.percent === 100
                ? 'Bravo, tu as terminé toutes les leçons de ce parcours Jupython.'
                : 'Ta progression a été enregistrée.';
            this.render();
        } catch (error) {
            console.error('Impossible d’enregistrer la progression de la leçon:', error);
            button.disabled = false;
            this.feedback.textContent = error.message || 'La progression n’a pas pu être enregistrée. Réessaie.';
        }
    }

    async handleQuizSubmit(event) {
        const form = event.target.closest('[data-module-quiz]');
        if (!form) return;
        event.preventDefault();
        const moduleId = Number(form.dataset.moduleQuiz);
        const quiz = this.quizByModule.get(moduleId);
        const answers = {};
        for (const question of quiz.questions) {
            const selected = form.querySelector(`input[name="quiz-${moduleId}-${question.id}"]:checked`);
            if (!selected) {
                this.feedback.textContent = 'Réponds à toutes les questions avant de valider.';
                return;
            }
            answers[question.id] = Number(selected.value);
        }

        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        try {
            const result = await api.submitModuleQuiz(moduleId, answers);
            this.quizByModule.set(moduleId, {
                ...quiz,
                passed: result.passed,
                best_score: result.best_score,
                attempts: result.attempts,
            });
            this.passedModuleIds = new Set(result.passed_module_ids);
            this.enrollment.progress.passed_module_ids = result.passed_module_ids;
            this.enrollment.status = result.status;
            if (result.passed) {
                this.formation = await api.getFormation(this.formation.id);
                this.feedback.textContent = `Test réussi avec ${result.score}%. Le module suivant est débloqué.`;
            } else {
                this.feedback.textContent = `Résultat : ${result.score}%. Il faut au moins 67% pour réussir. Tu peux réessayer.`;
            }
            this.render();
        } catch (error) {
            console.error('Impossible de valider le test du module:', error);
            submitButton.disabled = false;
            this.feedback.textContent = error.message || 'Le test n’a pas pu être envoyé. Réessaie.';
        }
    }

    updateProgress() {
        const totalLessons = this.formation.modules.reduce(
            (count, module) => count + (module.lesson_count || module.lessons.length),
            0,
        );
        const totalQuizzes = this.formation.modules.filter((module) => module.quiz_count > 0).length;
        const completedLessons = Math.min(this.completedLessonIds.size, totalLessons);
        const completedQuizzes = this.formation.modules.filter(
            (module) => this.passedModuleIds.has(module.id) && module.quiz_count > 0,
        ).length;
        const totalUnits = totalLessons + totalQuizzes;
        const completedUnits = completedLessons + completedQuizzes;
        const percent = totalUnits
            ? Math.round(completedUnits * 100 / totalUnits)
            : 0;
        document.querySelector('[data-course-progress-label]').textContent =
            `${completedLessons}/${totalLessons} leçons · ${completedQuizzes}/${totalQuizzes} tests — ${percent} %`;
        document.querySelector('[data-course-progress-bar]').style.width = `${percent}%`;
        document.querySelector('[role="progressbar"]').setAttribute('aria-valuenow', String(percent));
        this.renderJourney();
        this.updateMotivation();
    }

    showError(message) {
        this.modulesContainer.replaceChildren();
        const error = document.createElement('p');
        error.className = 'jp-academy-panel p-6 text-gray-300';
        error.textContent = message;
        this.modulesContainer.appendChild(error);
        this.feedback.textContent = message;
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new JupythonLearningPage());
} else {
    new JupythonLearningPage();
}
