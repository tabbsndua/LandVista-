(() => {
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

    document.querySelectorAll('[data-open-modal]').forEach((button) => {
        button.addEventListener('click', () => openModal(button.getAttribute('data-open-modal')));
    });

    document.querySelectorAll('[data-close-modal]').forEach((button) => {
        button.addEventListener('click', () => closeModal(button.getAttribute('data-close-modal')));
    });

    document.querySelectorAll('.about-modal').forEach((modal) => {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal(modal.id);
            }
        });
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        document.querySelectorAll('.about-modal.open').forEach((modal) => closeModal(modal.id));
    });

    function feedback(id, message, success) {
        const target = document.getElementById(id);
        if (!target) return;
        target.textContent = message;
        target.style.color = success ? '#0f766e' : '#b91c1c';
    }

    async function submitInquiryForm(formId, submitId, feedbackId, closeModalId) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const submit = document.getElementById(submitId);
            const original = submit ? submit.textContent : 'Submit';

            if (submit) {
                submit.disabled = true;
                submit.textContent = 'Submitting...';
            }
            feedback(feedbackId, '', true);

            try {
                const response = await fetch('/submit-inquiry', {
                    method: 'POST',
                    body: new FormData(form)
                });
                const result = await response.json();

                if (!response.ok || !result.success) {
                    throw new Error(result.error || result.message || 'Submission failed');
                }

                form.reset();
                feedback(feedbackId, 'Request submitted successfully. Our team will contact you shortly.', true);
                if (closeModalId) {
                    setTimeout(() => closeModal(closeModalId), 1000);
                }
            } catch (error) {
                feedback(feedbackId, error.message || 'Unable to submit request', false);
            } finally {
                if (submit) {
                    submit.disabled = false;
                    submit.textContent = original;
                }
            }
        });
    }

    submitInquiryForm('aboutProfileForm', 'aboutProfileSubmit', 'aboutProfileFeedback', 'aboutProfileModal');
    submitInquiryForm('aboutConsultForm', 'aboutConsultSubmit', 'aboutConsultFeedback', 'aboutConsultModal');

    const accordion = document.getElementById('aboutAccordion');
    if (accordion) {
        const items = Array.from(accordion.querySelectorAll('.about-accordion-item'));
        items.forEach((item) => {
            item.addEventListener('click', () => {
                const panel = item.nextElementSibling;
                const wasOpen = item.classList.contains('active');

                items.forEach((other) => {
                    other.classList.remove('active');
                    const otherPanel = other.nextElementSibling;
                    if (otherPanel) {
                        otherPanel.style.display = 'none';
                    }
                });

                if (!wasOpen && panel) {
                    item.classList.add('active');
                    panel.style.display = 'block';
                }
            });
        });
    }

    const newsGrid = document.getElementById('aboutNewsGrid');
    if (newsGrid) {
        fetch('/api/news')
            .then((response) => response.json())
            .then((articles) => {
                if (!Array.isArray(articles) || !articles.length) {
                    newsGrid.innerHTML = '<p class="about-loading">New insights will appear here soon.</p>';
                    return;
                }

                newsGrid.innerHTML = articles.slice(0, 4).map((article) => {
                    const title = String(article.title || 'Untitled article');
                    const excerpt = String(article.excerpt || 'Market and investment update from LandVista.');
                    const author = String(article.author || 'LandVista Team');
                    const category = String(article.category || 'Market');
                    const slug = article.slug || article._id;
                    return `
                        <article class="about-news-card">
                            <small>${author} | ${category}</small>
                            <h3>${title}</h3>
                            <p>${excerpt.length > 125 ? `${excerpt.slice(0, 122)}...` : excerpt}</p>
                            <a href="/news/${slug}">Read more</a>
                        </article>
                    `;
                }).join('');
            })
            .catch((error) => {
                console.error('Failed to load about page articles', error);
                newsGrid.innerHTML = '<p class="about-loading">Unable to load updates right now.</p>';
            });
    }
})();
