/**
 * Client API Jupython - Version 2.0
 * Gère la communication entre le frontend et le backend Django
 * 
 * Utilisation:
 *   const formations = await api.getFormations();
 *   const ranking = await api.getRanking();
 *   await api.login(username, password);
 *   await api.logout();
 */

class ApiClient {
    constructor() {
        // URL du backend relative au même domaine pour une synchronisation fiable
        this.baseURL = '/api';
        this.token = localStorage.getItem('access_token');
        this.refreshPromise = null;
    }

    /**
     * Effectue une requête HTTP générique
     * @param {string} endpoint - Route de l’API (/formations/, /ranking/, etc.)
     * @param {object} options - Options de fetch (method, body, headers, etc.)
     * @returns {Promise} Réponse JSON
     */
    async request(endpoint, options = {}) {
        const { publicRequest = false, responseType = 'json', ...requestOptions } = options;
        const url = `${this.baseURL}${endpoint}`;
        this.token = localStorage.getItem('access_token');
        if (!publicRequest && this.token && await this.shouldRefreshAccessToken()) {
            const refreshed = await this.refreshSession();
            if (!refreshed) {
                this.expireSession();
                return null;
            }
        }
        const headers = { ...(requestOptions.headers || {}) };

        // Ajouter le jeton JWT si l’utilisateur est authentifié.
        if (this.token && !publicRequest) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (!(requestOptions.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        try {
            const fetchOptions = {
                ...requestOptions,
                headers,
                // Empêcher l’envoi des cookies de session du navigateur à l’API afin que l’authentification JWT fasse autorité.
                credentials: requestOptions.credentials ?? 'omit',
            };

            let response = await fetch(url, fetchOptions);

            // Si le jeton a expiré (401), rediriger vers la connexion.
            if (response.status === 401 && !publicRequest && !endpoint.includes('/token/refresh/')) {
                const refreshed = await this.refreshSession();
                if (refreshed) {
                    headers['Authorization'] = `Bearer ${this.token}`;
                    if (endpoint === '/accounts/logout/' && requestOptions.body) {
                        const body = JSON.parse(requestOptions.body);
                        body.refresh = localStorage.getItem('refresh_token');
                        fetchOptions.body = JSON.stringify(body);
                    }
                    response = await fetch(url, fetchOptions);
                } else {
                    this.expireSession();
                    return null;
                }
            }

            // En cas d’erreur du serveur.
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                // Fournir les détails de l’erreur (utile pour le débogage du frontend).
                const errorMsg = errorData.detail || errorData.error || errorData.message || JSON.stringify(errorData) || `HTTP ${response.status}`;
                // Joindre les détails d’origine pour que le code appelant puisse les consulter.
                const err = new Error(errorMsg);
                err.data = errorData;
                throw err;
            }

            // Aucun contenu à retourner (204 : aucun contenu).
            if (response.status === 204) {
                return null;
            }

            if (responseType === 'blob') {
                return await response.blob();
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    async shouldRefreshAccessToken() {
        try {
            const payload = this.token.split('.')[1];
            const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
            return typeof decoded.exp !== 'number' || decoded.exp <= Math.floor(Date.now() / 1000) + 60;
        } catch (error) {
            console.warn('Le jeton de session ne peut pas être vérifié, renouvellement demandé.');
            return true;
        }
    }

    async restoreSession() {
        this.token = localStorage.getItem('access_token');
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return false;

        if (!this.token || await this.shouldRefreshAccessToken()) {
            if (!await this.refreshSession()) {
                this.expireSession();
                return false;
            }
        }
        return true;
    }

    async refreshSession() {
        if (this.refreshPromise) return this.refreshPromise;

        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return false;

        this.refreshPromise = (async () => {
            try {
                let response = await fetch(`${this.baseURL}/accounts/token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'omit',
                    body: JSON.stringify({ refresh }),
                });
                if ((response.status === 400 || response.status === 401)
                    && localStorage.getItem('refresh_token') !== refresh) {
                    response = await fetch(`${this.baseURL}/accounts/token/refresh/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'omit',
                        body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') }),
                    });
                }
                if (!response.ok) {
                    if (response.status === 400 || response.status === 401) return false;
                    throw new Error(`Le renouvellement de session a échoué (HTTP ${response.status}).`);
                }

                const tokens = await response.json();
                if (!tokens.access || !tokens.refresh) {
                    throw new Error('La réponse de renouvellement de session est incomplète.');
                }
                this.token = tokens.access;
                localStorage.setItem('access_token', tokens.access);
                localStorage.setItem('refresh_token', tokens.refresh);
                return true;
            } catch (error) {
                console.error('Impossible de renouveler la session:', error);
                throw error;
            } finally {
                this.refreshPromise = null;
            }
        })();
        return this.refreshPromise;
    }

    expireSession() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        this.token = null;
        const protectedPages = ['/academy/dashboard.html', '/academy/profile.html'];
        if (protectedPages.includes(window.location.pathname)) {
            window.location.href = '/academy/login.html';
        }
    }

    /**
     * ========== FORMATIONS ==========
     */

    async getFormations(filters = {}) {
        try {
            let endpoint = '/formations/';
            if (Object.keys(filters).length > 0) {
                endpoint += '?' + new URLSearchParams(filters).toString();
            }
            return await this.request(endpoint, { publicRequest: true });
        } catch (error) {
            console.error('Erreur chargement formations:', error);
            throw error;
        }
    }

    async getFormation(id) {
        return await this.request(`/formations/${id}/`);
    }

    /**
     * ========== CLASSEMENTS ==========
     */

    async getRanking(filters = {}) {
        try {
            let endpoint = '/ranking/';
            if (Object.keys(filters).length > 0) {
                endpoint += '?' + new URLSearchParams(filters).toString();
            }

            return await this.request(endpoint);
        } catch (error) {
            console.error('Erreur chargement ranking:', error);
            return [];
        }
    }

    async getPublicProfile(userId) {
        return await this.request(`/accounts/public-profile/${encodeURIComponent(userId)}/`);
    }

    async followUser(userId) {
        return await this.request(`/accounts/public-profile/${encodeURIComponent(userId)}/follow/`, {
            method: 'POST',
            body: JSON.stringify({})
        });
    }

    async unfollowUser(userId) {
        return await this.request(`/accounts/public-profile/${encodeURIComponent(userId)}/follow/`, {
            method: 'DELETE'
        });
    }

    /**
     * ========== AUTHENTIFICATION ==========
     */

    async register(userData) {
        try {
            const result = await this.request('/accounts/register/', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            // Si le backend a renvoyé des jetons, les enregistrer puis récupérer le profil.
            if (result && result.access) {
                this.token = result.access;
                localStorage.setItem('access_token', result.access);
                localStorage.setItem('refresh_token', result.refresh);
                if (result.user) {
                    localStorage.setItem('user', JSON.stringify(result.user));
                } else {
                    // Récupérer le profil pour disposer des informations utilisateur à jour.
                    try {
                        const profile = await this.getProfile();
                        if (profile) localStorage.setItem('user', JSON.stringify(profile));
                    } catch (e) {
                        // Ignorer cette erreur.
                    }
                }
            }

            return result;
        } catch (error) {
            console.error('Erreur inscription:', error);
            throw error;
        }
    }

    async login(username, password) {
        try {
            const data = await this.request('/accounts/login/', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            if (data && data.access) {
                this.token = data.access;
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                // Le point de terminaison des jetons ne renvoie généralement pas l’utilisateur ; récupérer le profil pour enregistrer le bon compte.
                try {
                    const profile = await this.getProfile();
                    if (profile) {
                        localStorage.setItem('user', JSON.stringify(profile));
                    }
                } catch (e) {
                    // Si la récupération du profil échoue, utiliser l’utilisateur éventuellement renvoyé.
                    if (data.user) {
                        localStorage.setItem('user', JSON.stringify(data.user));
                    }
                }
            }

            return data;
        } catch (error) {
            console.error('Erreur connexion:', error);
            throw error;
        }
    }

    async logout() {
        try {
            const refresh = localStorage.getItem('refresh_token');
            if (refresh) {
                await this.restoreSession();
                await this.request('/accounts/logout/', {
                    method: 'POST',
                    body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
                });
            }
        } catch (error) {
            console.error('Erreur déconnexion:', error);
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            this.token = null;
        }
    }

    async getProfile() {
        try {
            return await this.request('/accounts/profile/');
        } catch (error) {
            console.error('Erreur chargement profil:', error);
            return null;
        }
    }

    async requestPasswordReset(email) {
        return await this.request('/accounts/password/reset/', {
            method: 'POST',
            body: JSON.stringify({ email }),
            publicRequest: true,
        });
    }

    async confirmPasswordReset(uid, token, password, confirmPassword) {
        return await this.request('/accounts/password/reset/confirm/', {
            method: 'POST',
            body: JSON.stringify({ uid, token, password, confirm_password: confirmPassword }),
            publicRequest: true,
        });
    }

    async changePassword(currentPassword, password, confirmPassword) {
        const result = await this.request('/accounts/password/change/', {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                password,
                confirm_password: confirmPassword,
            }),
        });
        if (result?.access && result?.refresh) {
            this.token = result.access;
            localStorage.setItem('access_token', result.access);
            localStorage.setItem('refresh_token', result.refresh);
        }
        return result;
    }

    async updateProfile(data) {
        try {
            const isFormData = data instanceof FormData;
            return await this.request('/accounts/profile/', {
                method: 'PUT',
                body: isFormData ? data : JSON.stringify(data)
            });
        } catch (error) {
            console.error('Erreur mise à jour profil:', error);
            throw error;
        }
    }

    /**
     * ========== CONTACT ==========
     */

    async sendContact(contactData) {
        try {
            return await this.request('/contact/', {
                method: 'POST',
                body: JSON.stringify(contactData)
            });
        } catch (error) {
            console.error('Erreur envoi message:', error);
            throw error;
        }
    }

    /**
     * ========== PROJETS ==========
     */

    async getProjects(filters = {}) {
        try {
            let endpoint = '/projects/';
            if (Object.keys(filters).length > 0) {
                endpoint += '?' + new URLSearchParams(filters).toString();
            }
            return await this.request(endpoint);
        } catch (error) {
            console.error('Erreur chargement projets:', error);
            return [];
        }
    }

    /**
     * ========== INSCRIPTIONS ==========
     */

    async enrollCourse(formationId) {
        try {
            return await this.request('/enrollments/enroll/', {
                method: 'POST',
                body: JSON.stringify({ formation_id: formationId })
            });
        } catch (error) {
            console.error('Erreur inscription formation:', error);
            throw error;
        }
    }

    async updateEnrollmentStatus(enrollmentId, status) {
        return await this.request(`/enrollments/${enrollmentId}/progress/`, {
            method: 'PATCH',
            body: JSON.stringify({ status })
        });
    }

    async submitCertificate(formationId, certificateUrl, certificateFile) {
        const body = new FormData();
        body.append('formation_id', formationId);
        if (certificateUrl) body.append('certificate_url', certificateUrl);
        if (certificateFile) body.append('certificate_file', certificateFile);
        return await this.request('/certificates/submit/', {
            method: 'POST',
            body
        });
    }

    async downloadCertificate(certificateId) {
        const blob = await this.request(`/certificates/${encodeURIComponent(certificateId)}/file/`, {
            responseType: 'blob'
        });
        if (!blob) return;

        const extension = {
            'application/pdf': 'pdf',
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/webp': 'webp'
        }[blob.type] || 'file';
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `certificate-${certificateId}.${extension}`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    async submitLessonPractice(lessonId, response) {
        return await this.request(`/enrollments/lessons/${lessonId}/practice/`, {
            method: 'POST',
            body: JSON.stringify({ response })
        });
    }

    async completeLesson(lessonId) {
        return await this.request(`/enrollments/lessons/${lessonId}/progress/`, {
            method: 'POST'
        });
    }

    async reopenLesson(lessonId) {
        return await this.request(`/enrollments/lessons/${lessonId}/progress/`, {
            method: 'DELETE'
        });
    }

    async getModuleQuiz(moduleId) {
        return await this.request(`/enrollments/modules/${moduleId}/quiz/`);
    }

    async submitModuleQuiz(moduleId, answers) {
        return await this.request(`/enrollments/modules/${moduleId}/quiz/`, {
            method: 'POST',
            body: JSON.stringify({ answers })
        });
    }

    async getMyEnrollments() {
        return await this.request('/enrollments/my/');
    }

    async getMyCertificates() {
        return await this.request('/certificates/my/');
    }

    /**
     * ========== UTILITAIRES ==========
     */

    isAuthenticated() {
        return !!(localStorage.getItem('access_token') || localStorage.getItem('refresh_token'));
    }

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    getCurrentUsername() {
        const user = this.getUser();
        return user ? user.username : null;
    }
}

// Instance globale du client API.
const api = new ApiClient();
