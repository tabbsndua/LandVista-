(() => {
    const data = window.propertyDetailData || {};
    const stage = document.getElementById('pdStage');
    const thumbsWrap = document.getElementById('pdThumbs');
    const prevBtn = document.getElementById('pdPrev');
    const nextBtn = document.getElementById('pdNext');
    const expandBtn = document.getElementById('pdExpand');
    const similarGrid = document.getElementById('pdSimilarGrid');
    const faqAccordion = document.getElementById('pdFaqAccordion');

    const inlineMedia = Array.isArray(data.media) ? data.media.filter(Boolean) : [];
    const thumbMedia = Array.from(document.querySelectorAll('#pdThumbs .pd-thumb'))
        .map((thumb) => thumb.getAttribute('data-media') || '')
        .filter(Boolean);
    const mediaList = inlineMedia.length ? inlineMedia : thumbMedia;
    let currentIndex = 0;

    function escapeHTML(value) {
        return String(value || '').replace(/[&<>"']/g, (char) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[char]));
    }

    function money(value) {
        const n = Number(value || 0);
        return `KSh ${Number.isFinite(n) ? n.toLocaleString() : '0'}`;
    }

    function mediaSrc(name) {
        return `/static/uploads/${encodeURIComponent(name || '')}`;
    }

    function isVideo(name) {
        return /\.(mp4|webm|mov)$/i.test(String(name || ''));
    }

    function renderStage(index) {
        if (!stage || !mediaList.length) return;
        currentIndex = (index + mediaList.length) % mediaList.length;
        const item = mediaList[currentIndex];

        const mediaMarkup = isVideo(item)
            ? `<video controls preload="metadata"><source src="${mediaSrc(item)}"></video>`
            : `<img id="pdMainMedia" src="${mediaSrc(item)}" alt="${escapeHTML(data.title || 'Property media')}">`;

        stage.querySelectorAll('img,video,.pd-placeholder-media').forEach((el) => el.remove());
        stage.insertAdjacentHTML('afterbegin', mediaMarkup);

        thumbsWrap?.querySelectorAll('.pd-thumb').forEach((thumb, i) => {
            thumb.classList.toggle('active', i === currentIndex);
        });
    }

    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    function setupMediaViewer() {
        if (!mediaList.length) {
            prevBtn?.setAttribute('disabled', 'disabled');
            nextBtn?.setAttribute('disabled', 'disabled');
            expandBtn?.setAttribute('disabled', 'disabled');
            return;
        }

        thumbsWrap?.addEventListener('click', (event) => {
            const thumb = event.target.closest('.pd-thumb');
            if (!thumb) return;
            const idx = Number(thumb.dataset.index || 0);
            renderStage(idx);
        });

        prevBtn?.addEventListener('click', () => renderStage(currentIndex - 1));
        nextBtn?.addEventListener('click', () => renderStage(currentIndex + 1));

        expandBtn?.addEventListener('click', () => {
            const modalContent = document.getElementById('pdMediaModalContent');
            if (!modalContent) return;
            const item = mediaList[currentIndex] || '';
            modalContent.innerHTML = isVideo(item)
                ? `<video controls autoplay preload="metadata"><source src="${mediaSrc(item)}"></video>`
                : `<img src="${mediaSrc(item)}" alt="${escapeHTML(data.title || 'Property media')}">`;
            openModal('pdMediaModal');
        });

        renderStage(0);
    }

    function showFeedback(elementId, message, success) {
        const target = document.getElementById(elementId);
        if (!target) return;
        target.textContent = message;
        target.style.color = success ? '#0f766e' : '#b91c1c';
    }

    async function submitForm(form, endpoint, submitButtonId, feedbackId, successText) {
        const button = document.getElementById(submitButtonId);
        if (button) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Submitting...';
        }

        showFeedback(feedbackId, '', true);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: new FormData(form)
            });
            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || result.message || 'Unable to submit form');
            }

            form.reset();
            showFeedback(feedbackId, successText, true);
            return true;
        } catch (error) {
            showFeedback(feedbackId, error.message || 'Submission failed', false);
            return false;
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = button.dataset.originalText || 'Submit';
            }
        }
    }

    function setupForms() {
        const quickInquiryForm = document.getElementById('pdQuickInquiryForm');
        const visitForm = document.getElementById('pdVisitForm');
        const brochureForm = document.getElementById('pdBrochureForm');

        quickInquiryForm?.addEventListener('submit', async (event) => {
            event.preventDefault();
            await submitForm(
                quickInquiryForm,
                '/submit-inquiry',
                'pdInquirySubmit',
                'pdQuickInquiryFeedback',
                'Inquiry submitted. Our advisor will contact you shortly.'
            );
        });

        visitForm?.addEventListener('submit', async (event) => {
            event.preventDefault();
            const ok = await submitForm(
                visitForm,
                '/submit-site-visit',
                'pdVisitSubmit',
                'pdVisitFeedback',
                'Site visit request sent successfully.'
            );
            if (ok) {
                setTimeout(() => closeModal('pdVisitModal'), 900);
            }
        });

        brochureForm?.addEventListener('submit', async (event) => {
            event.preventDefault();
            const ok = await submitForm(
                brochureForm,
                '/submit-inquiry',
                'pdBrochureSubmit',
                'pdBrochureFeedback',
                'Request received. We will share the brochure shortly.'
            );
            if (ok) {
                setTimeout(() => closeModal('pdInquiryModal'), 900);
            }
        });
    }

    function setupModals() {
        document.querySelectorAll('[data-open-modal]').forEach((trigger) => {
            trigger.addEventListener('click', () => {
                const modalId = trigger.getAttribute('data-open-modal');
                if (modalId) openModal(modalId);
            });
        });

        document.querySelectorAll('[data-close-modal]').forEach((trigger) => {
            trigger.addEventListener('click', () => {
                const modalId = trigger.getAttribute('data-close-modal');
                if (modalId) closeModal(modalId);
            });
        });

        document.querySelectorAll('.pd-modal').forEach((modal) => {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) {
                    closeModal(modal.id);
                }
            });
        });

        document.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape') return;
            document.querySelectorAll('.pd-modal.open').forEach((modal) => {
                closeModal(modal.id);
            });
        });
    }

    function setupCalculator() {
        const range = document.getElementById('pdDownPaymentRange');
        const label = document.getElementById('pdDownPaymentLabel');
        const downAmount = document.getElementById('pdDownAmount');
        const balanceAmount = document.getElementById('pdBalanceAmount');
        const installmentAmount = document.getElementById('pdInstallmentAmount');

        if (!range || !label || !downAmount || !balanceAmount || !installmentAmount) {
            return;
        }

        const total = Number(data.price || 0);

        const update = () => {
            const pct = Number(range.value || 30);
            const down = Math.round((pct / 100) * total);
            const balance = Math.max(0, total - down);
            const installment = Math.round(balance / 12);

            label.textContent = `${pct}%`;
            downAmount.textContent = money(down);
            balanceAmount.textContent = money(balance);
            installmentAmount.textContent = money(installment);
        };

        range.addEventListener('input', update);
        update();
    }

    function setupCopyLink() {
        const copyBtn = document.getElementById('pdCopyLinkBtn');
        copyBtn?.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(window.location.href);
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Link Copied';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-link"></i> Copy Link';
                }, 1500);
            } catch (error) {
                console.warn('Clipboard copy failed', error);
            }
        });
    }

    function setupFaqAccordion() {
        if (!faqAccordion) return;
        const items = Array.from(faqAccordion.querySelectorAll('.pd-accordion-item'));

        items.forEach((item) => {
            item.addEventListener('click', () => {
                const panel = item.nextElementSibling;
                if (!panel) return;

                const isOpen = item.classList.contains('active');
                items.forEach((other) => {
                    other.classList.remove('active');
                    const otherPanel = other.nextElementSibling;
                    if (otherPanel) otherPanel.style.display = 'none';
                });

                if (!isOpen) {
                    item.classList.add('active');
                    panel.style.display = 'block';
                }
            });
        });
    }

    async function loadSimilarProperties() {
        if (!similarGrid) return;
        try {
            const response = await fetch('/api/properties');
            const properties = await response.json();
            if (!Array.isArray(properties)) {
                throw new Error('Invalid property payload');
            }

            const location = String(data.location || '').toLowerCase();
            const county = String(data.county || '').toLowerCase();

            const filtered = properties
                .filter((item) => String(item._id) !== String(data.id))
                .filter((item) => String(item.status || '').toLowerCase() !== 'draft')
                .sort((a, b) => {
                    const scoreA = Number(String(a.location || '').toLowerCase().includes(location)) + Number(String(a.county || '').toLowerCase().includes(county));
                    const scoreB = Number(String(b.location || '').toLowerCase().includes(location)) + Number(String(b.county || '').toLowerCase().includes(county));
                    return scoreB - scoreA;
                })
                .slice(0, 6);

            if (!filtered.length) {
                similarGrid.innerHTML = '<p class="pd-loading">More opportunities will be available soon.</p>';
                return;
            }

            similarGrid.innerHTML = filtered.map((item) => {
                const media = Array.isArray(item.media) ? item.media[0] : item.media;
                const mediaMarkup = media
                    ? `<img src="${mediaSrc(media)}" alt="${escapeHTML(item.title || 'Property')}" loading="lazy">`
                    : '<div class="media-fallback">LandVista Listing</div>';

                return `
                    <article class="pd-similar-card">
                        ${mediaMarkup}
                        <div class="pd-similar-content">
                            <h4>${escapeHTML(item.title || 'Untitled')}</h4>
                            <p>${escapeHTML(item.location || 'Kenya')}</p>
                            <strong>${money(item.price || 0)}</strong>
                            <a href="/properties/${escapeHTML(item._id)}">View details</a>
                        </div>
                    </article>
                `;
            }).join('');
        } catch (error) {
            console.error('Failed to load similar properties', error);
            similarGrid.innerHTML = '<p class="pd-loading">Unable to load similar properties right now.</p>';
        }
    }

    setupMediaViewer();
    setupModals();
    setupForms();
    setupCalculator();
    setupCopyLink();
    setupFaqAccordion();
    loadSimilarProperties();
})();
