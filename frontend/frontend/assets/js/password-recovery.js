document.addEventListener('DOMContentLoaded', () => {
  const requestForm = document.querySelector('[data-password-reset-request]');
  const confirmForm = document.querySelector('[data-password-reset-confirm]');

  if (requestForm) {
    requestForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = requestForm.querySelector('button[type="submit"]');
      const feedback = requestForm.querySelector('[data-reset-feedback]');
      button.disabled = true;
      feedback.textContent = 'Envoi en cours…';
      try {
        const result = await api.requestPasswordReset(requestForm.elements.email.value.trim());
        feedback.textContent = result.message;
        requestForm.reset();
      } catch (error) {
        feedback.textContent = error.data?.email?.[0] || error.message || 'Impossible d’envoyer la demande. Réessaie plus tard.';
      } finally {
        button.disabled = false;
      }
    });
  }

  if (confirmForm) {
    const params = new URLSearchParams(window.location.search);
    const uid = params.get('uid');
    const token = params.get('token');
    const feedback = confirmForm.querySelector('[data-reset-feedback]');
    const button = confirmForm.querySelector('button[type="submit"]');
    const loginLink = document.querySelector('[data-login-link]');
    if (!uid || !token) {
      feedback.textContent = 'Ce lien est incomplet. Demande une nouvelle réinitialisation.';
      button.disabled = true;
    }
    confirmForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!uid || !token) return;
      const password = confirmForm.elements.password.value;
      const confirmation = confirmForm.elements.confirm_password.value;
      if (password !== confirmation) {
        feedback.textContent = 'Les mots de passe ne correspondent pas.';
        return;
      }
      button.disabled = true;
      feedback.textContent = 'Mise à jour en cours…';
      try {
        const result = await api.confirmPasswordReset(uid, token, password, confirmation);
        feedback.textContent = result.message;
        confirmForm.reset();
        loginLink.classList.remove('hidden');
      } catch (error) {
        feedback.textContent = error.data?.password?.[0] || error.data?.error || error.message || 'Ce lien est invalide ou a expiré.';
      } finally {
        button.disabled = false;
      }
    });
  }
});
