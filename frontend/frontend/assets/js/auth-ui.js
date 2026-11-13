(() => {
    function setVisible(element, visible) {
        if (visible) {
            element.style.display = '';
        } else {
            element.style.display = 'none';
        }
    }

    function getUser() {
        try {
            return api.getUser();
        } catch (error) {
            console.warn('Les informations locales du profil sont illisibles:', error);
            return null;
        }
    }

    function createAccountMenu(container, user) {
        const details = document.createElement('details');
        details.className = 'jp-account-menu';
        details.dataset.accountMenu = '';

        const summary = document.createElement('summary');
        summary.className = 'jp-account-trigger';
        summary.setAttribute('aria-label', 'Ouvrir le menu du compte');
        const avatar = document.createElement('span');
        avatar.className = 'jp-account-avatar';
        avatar.setAttribute('aria-hidden', 'true');
        const initials = document.createElement('span');
        initials.className = 'jp-account-avatar-fallback';
        initials.textContent = (user?.first_name || user?.username || 'M').trim().slice(0, 1).toUpperCase();
        const image = document.createElement('img');
        image.className = 'jp-account-avatar-image';
        image.alt = '';
        image.hidden = true;
        avatar.append(initials, image);
        const name = document.createElement('span');
        name.className = 'jp-account-name';
        name.dataset.navUserName = '';
        name.textContent = user?.first_name || user?.username || 'Mon compte';
        const chevron = document.createElement('span');
        chevron.className = 'jp-account-chevron';
        chevron.setAttribute('aria-hidden', 'true');
        summary.append(avatar, name, chevron);

        const menu = document.createElement('div');
        menu.className = 'jp-account-dropdown';
        const links = [
            { href: '/academy/dashboard.html', label: 'Mon espace' },
            { href: '/academy/profile.html', label: 'Mon profil' },
            { href: '/academy/login.html', label: 'Déconnexion', action: 'logout' },
        ];
        links.forEach(({ href, label, action }) => {
            const link = document.createElement('a');
            link.href = href;
            link.textContent = label;
            if (action) link.dataset.action = action;
            menu.appendChild(link);
        });
        details.append(summary, menu);
        container.insertAdjacentElement('afterend', details);
        updateAccountAvatar(avatar, user);
        return details;
    }

    function updateAccountAvatar(avatar, user) {
        const initials = avatar.querySelector('.jp-account-avatar-fallback');
        const image = avatar.querySelector('.jp-account-avatar-image');
        const displayName = user?.first_name || user?.username || 'M';
        initials.textContent = displayName.trim().slice(0, 1).toUpperCase();
        image.hidden = true;
        image.onerror = () => {
            image.hidden = true;
            initials.hidden = false;
        };

        if (user?.avatar) {
            image.src = new URL(user.avatar, window.location.origin).href;
            image.onload = () => {
                image.hidden = false;
                initials.hidden = true;
            };
        } else {
            image.removeAttribute('src');
            initials.hidden = false;
        }
    }

    function updateNavigation() {
        const isAuth = api.isAuthenticated();
        const user = getUser();
        const currentPath = window.location.pathname === '/'
            ? '/index.html'
            : window.location.pathname;

        document.querySelectorAll('[data-role="auth"]').forEach((element) => {
            setVisible(element, isAuth);
        });
        document.querySelectorAll('[data-role="guest"]').forEach((element) => {
            setVisible(element, !isAuth);
        });
        document.querySelectorAll('[data-role="admin"]').forEach((element) => {
            setVisible(element, !!(isAuth && user?.is_staff));
        });

        document.querySelectorAll('header nav a').forEach((link) => {
            const destination = new URL(link.href, window.location.origin);
            const isCurrent = destination.origin === window.location.origin
                && destination.pathname === currentPath;
            if (isCurrent) {
                link.setAttribute('aria-current', 'page');
                link.classList.add('jp-nav-active');
                link.classList.remove('bg-orange-500', 'text-white', 'shadow', 'font-semibold');
            } else {
                link.removeAttribute('aria-current');
                link.classList.remove('jp-nav-active');
            }
        });

        document.querySelectorAll('[data-nav-user-name]').forEach((element) => {
            element.textContent = user?.first_name || user?.username || 'Mon compte';
        });
        document.querySelectorAll('.jp-account-avatar').forEach((element) => {
            updateAccountAvatar(element, user);
        });
        document.querySelectorAll('[data-user-name]').forEach((element) => {
            if (user) {
                element.textContent = `Bienvenue, ${user.first_name || user.username || 'utilisateur'} !`;
            }
        });
        document.querySelectorAll('[data-user-email]').forEach((element) => {
            if (user?.email) element.textContent = user.email;
        });

        document.querySelectorAll('header nav').forEach((nav) => {
            const hasRoleBasedAccountLink = nav.querySelector('[data-role="auth"], [data-role="guest"]');
            if (hasRoleBasedAccountLink && !nav.nextElementSibling?.matches('[data-account-menu]')) {
                createAccountMenu(nav, user);
            }
        });
        document.querySelectorAll('[data-account-menu]').forEach((element) => {
            setVisible(element, isAuth);
        });
        document.querySelectorAll('.jp-account-dropdown a').forEach((link) => {
            const destination = new URL(link.href, window.location.origin);
            if (destination.origin === window.location.origin && destination.pathname === currentPath) {
                link.setAttribute('aria-current', 'page');
            } else {
                link.removeAttribute('aria-current');
            }
        });
    }

    async function initialize() {
        if (localStorage.getItem('refresh_token')) {
            try {
                await api.restoreSession();
            } catch (error) {
                console.warn('La session est conservée mais ne peut pas être vérifiée pour le moment:', error);
            }
        }
        updateNavigation();
    }

    document.addEventListener('DOMContentLoaded', initialize);
    window.addEventListener('storage', (event) => {
        if (['access_token', 'refresh_token', 'user'].includes(event.key)) {
            updateNavigation();
        }
    });
    window.addEventListener('jupython:auth-changed', updateNavigation);

    document.addEventListener('click', async (event) => {
        const logoutLink = event.target.closest('[data-action="logout"]');
        if (!logoutLink) return;

        event.preventDefault();
        logoutLink.setAttribute('aria-busy', 'true');
        try {
            await api.logout();
            updateNavigation();
            if (['/academy/dashboard.html', '/academy/profile.html', '/academy/learn.html']
                .includes(window.location.pathname)) {
                window.location.href = '/academy/login.html';
            }
        } catch (error) {
            console.error('La déconnexion a échoué:', error);
            logoutLink.removeAttribute('aria-busy');
        }
    });
})();
