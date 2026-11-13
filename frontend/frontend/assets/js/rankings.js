async function loadMemberDirectory() {
    const tbody = document.querySelector('[data-member-directory]');
    if (!tbody) return;

    try {
        const members = await api.request('/ranking/');
        const maxRows = Number(tbody.dataset.limit) || members.length;
        const dark = tbody.dataset.memberDirectory === 'dark';
        tbody.replaceChildren();

        if (!members.length) {
            const row = document.createElement('tr');
            const message = document.createElement('td');
            message.colSpan = 3;
            message.className = 'px-6 py-8 text-center text-gray-400';
            message.textContent = 'Aucun profil public pour le moment.';
            row.appendChild(message);
            tbody.appendChild(row);
            return;
        }

        members.slice(0, maxRows).forEach((member) => {
            const row = document.createElement('tr');
            row.className = dark ? 'border-b border-gray-700 hover:bg-gray-700/30' : 'border-b border-gray-200 hover:bg-orange-50/50';

            const identityCell = document.createElement('td');
            identityCell.className = 'px-6 py-5';
            const identity = document.createElement('div');
            identity.className = 'flex items-center gap-3';
            const image = document.createElement('img');
            image.className = 'w-12 h-12 rounded-full object-cover';
            image.alt = '';
            if (member.avatar) {
                image.src = member.avatar;
            } else {
                image.classList.add('hidden');
            }
            const initials = document.createElement('span');
            initials.className = `w-12 h-12 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold${member.avatar ? ' hidden' : ''}`;
            initials.textContent = member.display_name.split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase();
            image.addEventListener('error', () => {
                image.classList.add('hidden');
                initials.classList.remove('hidden');
            });
            const name = document.createElement('span');
            name.className = dark ? 'font-semibold text-white' : 'font-bold text-gray-900';
            name.textContent = member.display_name;
            identity.append(image, initials, name);
            identityCell.appendChild(identity);

            const bioCell = document.createElement('td');
            bioCell.className = `px-6 py-5 ${dark ? 'text-gray-300' : 'text-gray-600'}`;
            bioCell.textContent = member.bio || 'Aucune biographie.';

            const actionCell = document.createElement('td');
            actionCell.className = 'px-6 py-5 text-right';
            const profileLink = document.createElement('a');
            profileLink.href = `/academy/member.html?id=${encodeURIComponent(member.id)}`;
            profileLink.className = 'text-orange-500 hover:text-orange-600 font-semibold';
            profileLink.textContent = 'Voir le profil';
            actionCell.appendChild(profileLink);

            row.append(identityCell, bioCell, actionCell);
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Erreur chargement des profils publics:', error);
        tbody.replaceChildren();
        const row = document.createElement('tr');
        const message = document.createElement('td');
        message.colSpan = 3;
        message.className = 'px-6 py-8 text-center text-red-400';
        message.textContent = 'Impossible de charger les profils. Réessaie plus tard.';
        row.appendChild(message);
        tbody.appendChild(row);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadMemberDirectory);
} else {
    loadMemberDirectory();
}
