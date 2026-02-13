(() => {
    const ids = {
        totalProperties: document.getElementById('total-properties'),
        activeClients: document.getElementById('active-clients'),
        totalTestimonials: document.getElementById('total-testimonials'),
        totalSales: document.getElementById('total-sales'),
        pageViews: document.getElementById('page-views'),
        propertiesSold: document.getElementById('properties-sold'),
        conversionRate: document.getElementById('conversion-rate'),
        conversionRateBar: document.getElementById('conversion-rate-bar'),
        engagementScore: document.getElementById('engagement-score'),
        engagementScoreBar: document.getElementById('engagement-score-bar'),
        contentHealth: document.getElementById('content-health'),
        contentHealthBar: document.getElementById('content-health-bar'),
        liveStatus: document.getElementById('liveStatus'),
        recentInquiriesList: document.getElementById('recent-inquiries-list'),
        recentPropertiesList: document.getElementById('recent-properties-list'),
        latestNewsList: document.getElementById('latest-news-list'),
        latestGuidesList: document.getElementById('latest-guides-list')
    };

    function escapeHTML(value) {
        return String(value || '').replace(/[&<>"']/g, (char) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[char]));
    }

    function formatNumber(value) {
        const parsed = Number(value || 0);
        if (!Number.isFinite(parsed)) {
            return '0';
        }
        return parsed.toLocaleString();
    }

    function updateMetric(element, nextValue) {
        if (!element) return;
        const current = String(element.textContent || '').trim();
        const target = String(nextValue);
        if (current === target) return;

        element.textContent = target;
        element.classList.remove('metric-updated');
        void element.offsetWidth;
        element.classList.add('metric-updated');
    }

    function percent(numerator, denominator) {
        if (!denominator || denominator <= 0) return 0;
        return Math.min(100, Math.max(0, Math.round((numerator / denominator) * 100)));
    }

    function updateSignals(data) {
        const totalProperties = Number(data.total_properties || 0);
        const propertiesSold = Number(data.properties_sold || 0);
        const activeClients = Number(data.active_clients || 0);
        const pageViews = Number(data.page_views || 0);
        const newsCount = Array.isArray(data.latest_news) ? data.latest_news.length : 0;
        const guidesCount = Array.isArray(data.latest_guides) ? data.latest_guides.length : 0;

        const conversion = percent(propertiesSold, totalProperties || 1);
        const engagement = Math.min(100, Math.round(((activeClients * 1.5) + (pageViews / 25))));
        const content = Math.min(100, Math.round(((newsCount * 12) + (guidesCount * 14))));

        updateMetric(ids.conversionRate, `${conversion}%`);
        updateMetric(ids.engagementScore, `${engagement}%`);
        updateMetric(ids.contentHealth, `${content}%`);

        if (ids.conversionRateBar) ids.conversionRateBar.style.width = `${conversion}%`;
        if (ids.engagementScoreBar) ids.engagementScoreBar.style.width = `${engagement}%`;
        if (ids.contentHealthBar) ids.contentHealthBar.style.width = `${content}%`;
    }

    function renderInquiries(items) {
        if (!ids.recentInquiriesList) return;
        if (!Array.isArray(items) || !items.length) {
            ids.recentInquiriesList.innerHTML = '<p class="empty-text">No inquiries yet.</p>';
            return;
        }

        ids.recentInquiriesList.innerHTML = items.slice(0, 4).map((item) => `
            <div class="stream-row">
                <div>
                    <strong>${escapeHTML(item.name || 'Lead')}</strong>
                    <p>${escapeHTML(item.email || 'No email')}</p>
                    <small>${escapeHTML(item.property_title || item.property || 'General inquiry')}</small>
                </div>
                <span class="tag">${escapeHTML((item.status || 'new').toUpperCase())}</span>
            </div>
        `).join('');
    }

    function renderProperties(items) {
        if (!ids.recentPropertiesList) return;
        if (!Array.isArray(items) || !items.length) {
            ids.recentPropertiesList.innerHTML = '<p class="empty-text">No properties added yet.</p>';
            return;
        }

        ids.recentPropertiesList.innerHTML = items.slice(0, 4).map((item) => {
            const status = String(item.status || 'available').toLowerCase();
            return `
                <div class="stream-row">
                    <div>
                        <strong>${escapeHTML(item.title || 'Untitled property')}</strong>
                        <p>${escapeHTML(item.location || 'Kenya')}</p>
                        <small>KSh ${formatNumber(item.price || 0)}</small>
                    </div>
                    <span class="tag ${status === 'sold' ? 'sold' : ''}">${escapeHTML(status.toUpperCase())}</span>
                </div>
            `;
        }).join('');
    }

    function renderContentList(target, items, emptyMessage) {
        if (!target) return;
        if (!Array.isArray(items) || !items.length) {
            target.innerHTML = `<p class="empty-text">${escapeHTML(emptyMessage)}</p>`;
            return;
        }

        target.innerHTML = items.slice(0, 5).map((item) => `
            <div class="stream-row compact">
                <div>
                    <strong>${escapeHTML(item.title || 'Untitled')}</strong>
                    <small>${escapeHTML(item.author || 'Team')} | ${escapeHTML(item.category || 'General')}</small>
                </div>
                <span class="tag">${escapeHTML((item.status || 'published').toUpperCase())}</span>
            </div>
        `).join('');
    }

    function setLiveStatus(ok) {
        if (!ids.liveStatus) return;
        if (ok) {
            ids.liveStatus.textContent = `Live sync active - ${new Date().toLocaleTimeString()}`;
            ids.liveStatus.style.color = '#0f766e';
            return;
        }
        ids.liveStatus.textContent = 'Connection issue - retrying';
        ids.liveStatus.style.color = '#b91c1c';
    }

    async function refreshDashboard() {
        try {
            const response = await fetch('/admin/dashboard-data', { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            updateMetric(ids.totalProperties, formatNumber(data.total_properties));
            updateMetric(ids.activeClients, formatNumber(data.active_clients));
            updateMetric(ids.totalTestimonials, formatNumber(data.total_testimonials));
            updateMetric(ids.totalSales, formatNumber(data.total_sales));
            updateMetric(ids.pageViews, formatNumber(data.page_views));
            updateMetric(ids.propertiesSold, formatNumber(data.properties_sold));

            renderInquiries(data.recent_inquiries);
            renderProperties(data.recent_properties);
            renderContentList(ids.latestNewsList, data.latest_news, 'No published news yet.');
            renderContentList(ids.latestGuidesList, data.latest_guides, 'No legal guides yet.');
            updateSignals(data);
            setLiveStatus(true);
        } catch (error) {
            console.error('Dashboard refresh error:', error);
            setLiveStatus(false);
        }
    }

    refreshDashboard();
    setInterval(refreshDashboard, 10000);
})();
