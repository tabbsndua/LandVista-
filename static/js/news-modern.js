(() => {
    const source = window.newsPageData || { articles: [], guides: [] };

    const featuredCard = document.getElementById('newsFeaturedCard');
    const grid = document.getElementById('newsGrid');
    const resultCount = document.getElementById('newsResultCount');
    const searchInput = document.getElementById('newsSearchInput');
    const sortSelect = document.getElementById('newsSortSelect');
    const chipsWrap = document.getElementById('newsCategoryChips');
    const loadMoreBtn = document.getElementById('newsLoadMoreBtn');
    const segmented = document.getElementById('newsSegmented');
    const previewContent = document.getElementById('newsPreviewContent');

    const articleCount = document.getElementById('newsArticleCount');
    const guideCount = document.getElementById('newsGuideCount');
    const topicCount = document.getElementById('newsTopicCount');

    let selectedType = 'all';
    let selectedCategory = 'all';
    let visibleCount = 6;

    function escapeHTML(value) {
        return String(value || '').replace(/[&<>"']/g, (char) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[char]));
    }

    function toDateValue(item) {
        const raw = item.date || item.created_at || '';
        const parsed = new Date(raw);
        return Number.isNaN(parsed.getTime()) ? 0 : parsed.getTime();
    }

    function formatDate(item) {
        const raw = item.date || item.created_at;
        const parsed = new Date(raw || '');
        if (Number.isNaN(parsed.getTime())) {
            return 'Recent';
        }
        return parsed.toLocaleDateString();
    }

    function normalize(list, type) {
        if (!Array.isArray(list)) return [];
        return list.map((item) => ({
            id: item._id || item.id || '',
            type,
            title: item.title || 'Untitled',
            excerpt: item.excerpt || 'New insights from LandVista.',
            author: item.author || 'LandVista Team',
            category: item.category || (type === 'guide' ? 'Legal' : 'Market'),
            featured_image: item.featured_image || '',
            slug: item.slug || item._id || '',
            readTime: item.readTime || item.read_time || 5,
            content: item.content || item.excerpt || '',
            date: item.date || item.created_at || '',
            created_at: item.created_at || item.date || ''
        }));
    }

    let items = [
        ...normalize(source.articles, 'article'),
        ...normalize(source.guides, 'guide')
    ];

    async function hydrateFromApiIfNeeded() {
        if (items.length) {
            return;
        }
        try {
            const [newsResponse, guidesResponse] = await Promise.all([
                fetch('/api/news'),
                fetch('/api/legal-guides')
            ]);
            const [newsData, guidesData] = await Promise.all([
                newsResponse.json(),
                guidesResponse.json()
            ]);

            items = [
                ...normalize(newsData, 'article'),
                ...normalize(guidesData, 'guide')
            ];
        } catch (error) {
            console.error('Failed to hydrate news data from APIs', error);
        }
    }

    function uniqueCategories() {
        const categories = new Set(['all']);
        items.forEach((item) => categories.add(String(item.category || 'General').trim()));
        return Array.from(categories);
    }

    function categoryMarkup(category) {
        const normalized = category || 'all';
        const active = selectedCategory === normalized;
        return `<button type="button" class="news-chip ${active ? 'active' : ''}" data-category="${escapeHTML(normalized)}">${escapeHTML(normalized)}</button>`;
    }

    function renderCategoryChips() {
        if (!chipsWrap) return;
        chipsWrap.innerHTML = uniqueCategories().map(categoryMarkup).join('');
    }

    function filteredItems() {
        const q = String(searchInput?.value || '').trim().toLowerCase();
        const sortBy = sortSelect?.value || 'latest';

        const filtered = items.filter((item) => {
            const typeMatch = selectedType === 'all' || item.type === selectedType;
            const categoryMatch = selectedCategory === 'all' || String(item.category).toLowerCase() === selectedCategory.toLowerCase();
            const text = `${item.title} ${item.excerpt} ${item.author} ${item.category}`.toLowerCase();
            const queryMatch = !q || text.includes(q);
            return typeMatch && categoryMatch && queryMatch;
        });

        if (sortBy === 'oldest') {
            filtered.sort((a, b) => toDateValue(a) - toDateValue(b));
        } else if (sortBy === 'title') {
            filtered.sort((a, b) => String(a.title).localeCompare(String(b.title)));
        } else {
            filtered.sort((a, b) => toDateValue(b) - toDateValue(a));
        }

        return filtered;
    }

    function mediaMarkup(item) {
        const src = String(item.featured_image || '').trim();
        if (!src) {
            return '<div class="news-card-media-fallback">LandVista Insight</div>';
        }

        let safeSrc = src;
        if (/^https?:\/\//i.test(src)) {
            safeSrc = src;
        } else if (src.startsWith('/')) {
            safeSrc = src;
        } else if (src.startsWith('static/')) {
            safeSrc = `/${src}`;
        } else {
            safeSrc = `/static/uploads/${encodeURIComponent(src)}`;
        }
        safeSrc = escapeHTML(safeSrc);
        return `<img class="news-card-media" src="${safeSrc}" alt="${escapeHTML(item.title)}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'news-card-media-fallback',textContent:'LandVista Insight'}));">`;
    }

    function cardLink(item) {
        if (item.type === 'guide') {
            return `/legal-guides/${item.slug}`;
        }
        return `/news/${item.slug}`;
    }

    function cardMarkup(item) {
        return `
            <article class="news-card">
                ${mediaMarkup(item)}
                <div class="news-card-content">
                    <span class="news-card-type">${item.type === 'guide' ? 'Legal Guide' : 'Article'}</span>
                    <div class="news-card-meta">
                        <span>${escapeHTML(item.author)}</span>
                        <span>${escapeHTML(formatDate(item))}</span>
                        <span>${escapeHTML(String(item.readTime))} min</span>
                    </div>
                    <h3>${escapeHTML(item.title)}</h3>
                    <p>${escapeHTML(String(item.excerpt).slice(0, 140))}${String(item.excerpt).length > 140 ? '...' : ''}</p>
                    <div class="news-card-actions">
                        <a href="${cardLink(item)}">Read ${item.type === 'guide' ? 'guide' : 'article'}</a>
                        <button type="button" data-preview-id="${escapeHTML(item.id)}">Quick preview</button>
                    </div>
                </div>
            </article>
        `;
    }

    function renderFeatured(activeItems) {
        if (!featuredCard) return;
        const item = activeItems[0];

        if (!item) {
            featuredCard.innerHTML = '<p class="news-loading">No matching content for the current filter.</p>';
            return;
        }

        featuredCard.innerHTML = `
            <small>${item.type === 'guide' ? 'Legal Guide' : 'Article'} | ${escapeHTML(item.category)} | ${escapeHTML(formatDate(item))}</small>
            <h3>${escapeHTML(item.title)}</h3>
            <p>${escapeHTML(item.excerpt)}</p>
            <div class="news-featured-actions">
                <a href="${cardLink(item)}">Open full read</a>
                <button type="button" data-preview-id="${escapeHTML(item.id)}">Quick preview</button>
            </div>
        `;
    }

    function renderGrid() {
        if (!grid) return;
        const activeItems = filteredItems();
        renderFeatured(activeItems);

        const limited = activeItems.slice(0, visibleCount);
        grid.innerHTML = limited.length ? limited.map(cardMarkup).join('') : '<p class="news-loading">No content found. Try different filters.</p>';

        if (resultCount) {
            resultCount.textContent = `${activeItems.length} ${activeItems.length === 1 ? 'result' : 'results'}`;
        }

        if (loadMoreBtn) {
            loadMoreBtn.style.display = activeItems.length > visibleCount ? 'inline-block' : 'none';
        }
    }

    function renderStats() {
        const articleItems = items.filter((item) => item.type === 'article');
        const guideItems = items.filter((item) => item.type === 'guide');
        const topics = new Set(items.map((item) => item.category));

        if (articleCount) articleCount.textContent = String(articleItems.length);
        if (guideCount) guideCount.textContent = String(guideItems.length);
        if (topicCount) topicCount.textContent = String(topics.size);
    }

    function openModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    function bindModalTriggers() {
        document.querySelectorAll('[data-open-modal]').forEach((button) => {
            button.addEventListener('click', () => {
                const id = button.getAttribute('data-open-modal');
                if (id) openModal(id);
            });
        });

        document.querySelectorAll('[data-close-modal]').forEach((button) => {
            button.addEventListener('click', () => {
                const id = button.getAttribute('data-close-modal');
                if (id) closeModal(id);
            });
        });

        document.querySelectorAll('.news-modal').forEach((modal) => {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) {
                    closeModal(modal.id);
                }
            });
        });

        document.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape') return;
            document.querySelectorAll('.news-modal.open').forEach((modal) => closeModal(modal.id));
        });
    }

    function bindPreviewDelegation() {
        document.addEventListener('click', (event) => {
            const button = event.target.closest('[data-preview-id]');
            if (!button) return;

            const id = button.getAttribute('data-preview-id');
            const item = items.find((entry) => String(entry.id) === String(id));
            if (!item || !previewContent) return;

            previewContent.innerHTML = `
                <small>${item.type === 'guide' ? 'Legal Guide' : 'Article'} | ${escapeHTML(item.category)} | ${escapeHTML(formatDate(item))}</small>
                <h3>${escapeHTML(item.title)}</h3>
                <p>${escapeHTML(item.content || item.excerpt)}</p>
                <p><strong>Author:</strong> ${escapeHTML(item.author)} | <strong>Read time:</strong> ${escapeHTML(String(item.readTime))} min</p>
                <p><a href="${cardLink(item)}">Continue reading full ${item.type === 'guide' ? 'guide' : 'article'}</a></p>
            `;
            openModal('newsPreviewModal');
        });
    }

    function bindFiltering() {
        searchInput?.addEventListener('input', () => {
            visibleCount = 6;
            renderGrid();
        });

        sortSelect?.addEventListener('change', () => {
            visibleCount = 6;
            renderGrid();
        });

        segmented?.addEventListener('click', (event) => {
            const button = event.target.closest('button[data-type]');
            if (!button) return;
            selectedType = button.getAttribute('data-type') || 'all';
            segmented.querySelectorAll('button').forEach((node) => node.classList.toggle('active', node === button));
            visibleCount = 6;
            renderGrid();
        });

        chipsWrap?.addEventListener('click', (event) => {
            const chip = event.target.closest('button[data-category]');
            if (!chip) return;
            selectedCategory = chip.getAttribute('data-category') || 'all';
            chipsWrap.querySelectorAll('.news-chip').forEach((node) => node.classList.toggle('active', node === chip));
            visibleCount = 6;
            renderGrid();
        });

        loadMoreBtn?.addEventListener('click', () => {
            visibleCount += 6;
            renderGrid();
        });
    }

    async function handleNewsletterSubmit(event) {
        event.preventDefault();
        const form = event.currentTarget;
        const feedback = document.getElementById('newsNewsletterFeedback');
        const btn = document.getElementById('newsNewsletterBtn');

        if (!(form instanceof HTMLFormElement)) return;

        const email = form.querySelector('input[name="email"]')?.value?.trim();
        if (!email) return;

        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Submitting...';
        }
        if (feedback) feedback.textContent = '';

        try {
            const response = await fetch('/api/newsletter/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.message || 'Unable to subscribe');
            }

            form.reset();
            if (feedback) {
                feedback.textContent = result.message || 'Subscription successful.';
                feedback.style.color = '#0f766e';
            }
        } catch (error) {
            if (feedback) {
                feedback.textContent = error.message || 'Subscription failed';
                feedback.style.color = '#b91c1c';
            }
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'Subscribe';
            }
        }
    }

    document.getElementById('newsNewsletterForm')?.addEventListener('submit', handleNewsletterSubmit);

    bindModalTriggers();
    bindPreviewDelegation();
    bindFiltering();

    (async () => {
        await hydrateFromApiIfNeeded();
        renderCategoryChips();
        renderStats();
        renderGrid();
    })();

    function mergeIncomingData(type, payload) {
        if (!payload || !payload._id) return;
        const normalized = normalize([payload], type)[0];
        const existingIndex = items.findIndex((entry) => String(entry.id) === String(normalized.id));
        if (existingIndex >= 0) {
            items[existingIndex] = normalized;
        } else {
            items.unshift(normalized);
        }
        renderCategoryChips();
        renderStats();
        renderGrid();
    }

    function removeIncomingData(id) {
        items = items.filter((item) => String(item.id) !== String(id));
        renderCategoryChips();
        renderStats();
        renderGrid();
    }

    if (typeof io === 'function') {
        const socket = io();
        socket.on('news_added', (payload) => mergeIncomingData('article', payload));
        socket.on('news_updated', (payload) => mergeIncomingData('article', payload));
        socket.on('news_deleted', (payload) => removeIncomingData(payload?._id));

        socket.on('guide_added', (payload) => mergeIncomingData('guide', payload));
        socket.on('guide_updated', (payload) => mergeIncomingData('guide', payload));
        socket.on('guide_deleted', (payload) => removeIncomingData(payload?._id));
    }
})();
