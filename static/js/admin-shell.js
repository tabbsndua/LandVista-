(() => {
    const shell = document.querySelector('.admin-shell');
    const sidebar = document.getElementById('adminSidebar');
    const overlay = document.getElementById('adminOverlay');
    const openBtn = document.getElementById('adminMenuToggle');
    const closeBtn = document.getElementById('sidebarClose');

    if (!shell || !sidebar) {
        return;
    }

    function setSidebar(open) {
        shell.classList.toggle('sidebar-open', open);
        if (openBtn) {
            openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
        }
    }

    function closeSidebar() {
        setSidebar(false);
    }

    function openSidebar() {
        setSidebar(true);
    }

    openBtn?.addEventListener('click', () => {
        const isOpen = shell.classList.contains('sidebar-open');
        setSidebar(!isOpen);
    });

    closeBtn?.addEventListener('click', closeSidebar);
    overlay?.addEventListener('click', closeSidebar);

    window.addEventListener('resize', () => {
        if (window.innerWidth > 960) {
            closeSidebar();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeSidebar();
        }
    });

    const commandPalette = document.createElement('div');
    commandPalette.className = 'admin-command-palette';
    commandPalette.setAttribute('aria-hidden', 'true');
    commandPalette.innerHTML = `
        <div class="admin-command-backdrop"></div>
        <div class="admin-command-panel" role="dialog" aria-modal="true" aria-label="Quick actions">
            <div class="admin-command-head">
                <i class="fas fa-magnifying-glass"></i>
                <input type="text" id="adminCommandInput" placeholder="Search admin actions (e.g. payments, properties, inquiries)">
                <button type="button" id="adminCommandClose" aria-label="Close quick actions"><i class="fas fa-times"></i></button>
            </div>
            <div class="admin-command-list" id="adminCommandList"></div>
        </div>
    `;
    document.body.appendChild(commandPalette);

    const commandStyles = document.createElement('style');
    commandStyles.textContent = `
        .admin-command-palette { position: fixed; inset: 0; z-index: 2200; opacity: 0; pointer-events: none; transition: opacity .2s ease; }
        .admin-command-palette.open { opacity: 1; pointer-events: auto; }
        .admin-command-backdrop { position: absolute; inset: 0; background: rgba(3, 19, 13, 0.66); }
        .admin-command-panel { position: relative; width: min(92vw, 720px); margin: 10vh auto 0; border-radius: 16px; border: 1px solid #d6e3df; background: #ffffff; box-shadow: 0 30px 70px rgba(6, 31, 22, 0.25); overflow: hidden; }
        .admin-command-head { display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #e5efec; padding: 12px; }
        .admin-command-head i { color: #6b7d76; }
        #adminCommandInput { flex: 1; border: none; outline: none; font: inherit; font-size: 15px; }
        #adminCommandClose { border: 1px solid #dbe7e3; background: #fff; width: 30px; height: 30px; border-radius: 8px; cursor: pointer; }
        .admin-command-list { max-height: min(65vh, 520px); overflow: auto; display: grid; gap: 2px; padding: 8px; }
        .admin-command-item { display: flex; align-items: center; justify-content: space-between; gap: 10px; border-radius: 10px; padding: 10px; text-decoration: none; color: #132c23; border: 1px solid transparent; }
        .admin-command-item:hover { background: #f4faf7; border-color: #d3e3dd; }
        .admin-command-item small { color: #688078; }
    `;
    document.head.appendChild(commandStyles);

    const commandInput = document.getElementById('adminCommandInput');
    const commandList = document.getElementById('adminCommandList');
    const commandClose = document.getElementById('adminCommandClose');

    const actions = [
        { label: 'Dashboard', hint: 'Realtime KPIs', href: '/admin', icon: 'fa-chart-line' },
        { label: 'Properties', hint: 'Manage inventory', href: '/admin/properties', icon: 'fa-building' },
        { label: 'Clients', hint: 'Client records', href: '/admin/clients', icon: 'fa-users' },
        { label: 'Inquiries', hint: 'Leads and follow-up', href: '/admin/inquiries', icon: 'fa-envelope-open-text' },
        { label: 'Site Visits', hint: 'Bookings and tours', href: '/admin/site-visits', icon: 'fa-calendar-check' },
        { label: 'Payments', hint: 'Paystack activity', href: '/admin/payments', icon: 'fa-credit-card' },
        { label: 'News & Blogs', hint: 'Content publishing', href: '/admin/news', icon: 'fa-newspaper' },
        { label: 'Legal Guides', hint: 'Legal content', href: '/admin/legal-guides', icon: 'fa-scale-balanced' },
        { label: 'Testimonials', hint: 'Social proof', href: '/admin/testimonials', icon: 'fa-comment-dots' },
        { label: 'Public Website', hint: 'Open live site', href: '/home', icon: 'fa-globe' }
    ];

    function renderActionList(filter = '') {
        const query = filter.trim().toLowerCase();
        const filtered = actions.filter((action) => {
            if (!query) return true;
            return action.label.toLowerCase().includes(query) || action.hint.toLowerCase().includes(query);
        });

        commandList.innerHTML = filtered.map((action) => `
            <a class="admin-command-item" href="${action.href}">
                <span><i class="fas ${action.icon}"></i> ${action.label}</span>
                <small>${action.hint}</small>
            </a>
        `).join('') || '<div class="admin-command-item"><span>No matching actions</span></div>';
    }

    function openPalette() {
        renderActionList('');
        commandPalette.classList.add('open');
        commandPalette.setAttribute('aria-hidden', 'false');
        setTimeout(() => commandInput?.focus(), 40);
    }

    function closePalette() {
        commandPalette.classList.remove('open');
        commandPalette.setAttribute('aria-hidden', 'true');
        if (commandInput) commandInput.value = '';
    }

    commandClose?.addEventListener('click', closePalette);
    commandPalette.querySelector('.admin-command-backdrop')?.addEventListener('click', closePalette);
    commandInput?.addEventListener('input', () => renderActionList(commandInput.value));

    document.addEventListener('keydown', (event) => {
        const isMac = navigator.platform.toLowerCase().includes('mac');
        const paletteShortcut = (isMac ? event.metaKey : event.ctrlKey) && event.key.toLowerCase() === 'k';

        if (paletteShortcut) {
            event.preventDefault();
            if (commandPalette.classList.contains('open')) {
                closePalette();
            } else {
                openPalette();
            }
        }

        if (event.key === 'Escape' && commandPalette.classList.contains('open')) {
            closePalette();
        }
    });

    renderActionList('');
})();
