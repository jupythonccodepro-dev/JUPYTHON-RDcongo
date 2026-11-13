(() => {
    const scriptUrl = 'https://accounts.google.com/gsi/client';
    let scriptPromise;

    function loadGoogleIdentityServices() {
        if (window.google?.accounts?.id) {
            return Promise.resolve();
        }

        if (!scriptPromise) {
            scriptPromise = new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = scriptUrl;
                script.async = true;
                script.defer = true;
                script.onload = () => {
                    if (window.google?.accounts?.id) {
                        resolve();
                    } else {
                        reject(new Error('Le service Google Identity est indisponible.'));
                    }
                };
                script.onerror = () => reject(new Error('Impossible de charger le service Google Identity.'));
                document.head.appendChild(script);
            });
        }

        return scriptPromise;
    }

    window.setupGoogleAuthButton = async (container, onCredential) => {
        if (!container) return;

        const fallbackButton = container.querySelector('button');
        const status = container.parentElement.querySelector('[data-google-status]');
        const isLocalHost = ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname);

        if (window.location.protocol !== 'https:' && !isLocalHost) {
            if (fallbackButton) fallbackButton.disabled = true;
            if (status) {
                status.textContent = 'Google bloque cette adresse locale. Sur téléphone, utilise le site en HTTPS ou connecte-toi avec ton e-mail et ton mot de passe.';
            }
            return;
        }

        const clientId = (window.JUPYTHON_GOOGLE_CLIENT_ID || '').trim();

        if (!clientId || clientId.includes('YOUR_') || clientId.includes('your-')) {
            if (fallbackButton) fallbackButton.disabled = true;
            if (status) {
                status.textContent = 'Connexion Google indisponible : configurez GOOGLE_CLIENT_ID.';
            }
            return;
        }

        try {
            await loadGoogleIdentityServices();
            window.google.accounts.id.initialize({
                client_id: clientId,
                callback: onCredential,
            });
            container.replaceChildren();
            window.google.accounts.id.renderButton(container, {
                theme: 'outline',
                size: 'large',
                text: 'continue_with',
                shape: 'pill',
                width: 320,
                locale: 'fr',
            });
            if (status) status.textContent = '';
        } catch (error) {
            if (fallbackButton) fallbackButton.disabled = true;
            if (status) {
                status.textContent = 'Connexion Google momentanément indisponible.';
            }
            console.error('Impossible de configurer la connexion Google:', error);
            scriptPromise = undefined;
        }
    };
})();
