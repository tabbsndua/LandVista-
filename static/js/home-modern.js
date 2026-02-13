(() => {
    const landGrid = document.getElementById("landGrid");
    const testimonialsTrack = document.getElementById("testimonialsTrack");
    const testimonialsPrev = document.getElementById("testimonialsPrev");
    const testimonialsNext = document.getElementById("testimonialsNext");
    const testimonialsCount = document.getElementById("testimonialsCount");
    const testimonialsTotal = document.getElementById("testimonialsTotal");
    const testimonialsControls = testimonialsPrev && testimonialsNext ? testimonialsPrev.closest(".testimonials-controls") : null;
    const newsletterForm = document.getElementById("newsletterForm");
    const hero = document.querySelector(".modern-hero");
    const orbA = document.querySelector(".hero-gradient-orb-a");
    const orbB = document.querySelector(".hero-gradient-orb-b");
    const calculatorForm = document.getElementById("roiCalculatorForm");
    const calculatorResult = document.getElementById("calculatorResult");
    const consultationForm = document.getElementById("consultationForm");
    const consultationFeedback = document.getElementById("consultationFeedback");
    const consultationModal = document.getElementById("consultationModal");
    const modalOpeners = document.querySelectorAll("[data-modal-open]");
    const modalClosers = document.querySelectorAll("[data-modal-close]");

    let testimonialIndex = 0;
    let testimonialTimer = null;
    let refreshInterval = null;
    let isFetchingProperties = false;
    let isFetchingTestimonials = false;

    function escapeHTML(value) {
        const str = String(value || "");
        return str.replace(/[&<>"']/g, (char) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[char]));
    }

    function firstMedia(media) {
        if (!media) {
            return "";
        }
        if (Array.isArray(media)) {
            return media.length ? media[0] : "";
        }
        return media;
    }

    function isVideo(fileName) {
        return /\.(mp4|webm|mov)$/i.test(fileName || "");
    }

    function mediaMarkup(media, title) {
        const file = firstMedia(media);
        if (!file) {
            return `<img loading="lazy" src="/static/images/placeholder.jpg" alt="${escapeHTML(title)}">`;
        }

        const src = `/static/uploads/${encodeURIComponent(file)}`;
        if (isVideo(file)) {
            return `<video muted autoplay loop playsinline preload="metadata"><source src="${src}"></video>`;
        }
        return `<img loading="lazy" src="${src}" alt="${escapeHTML(title)}">`;
    }

    function priceMarkup(price) {
        const amount = Number(price);
        if (Number.isFinite(amount) && amount > 0) {
            return `KES ${amount.toLocaleString()}`;
        }
        return "Contact us";
    }

    function renderPropertyCard(property) {
        const title = escapeHTML(property.title || "Land Listing");
        const location = escapeHTML(property.location || "Kenya");
        const area = escapeHTML(property.area || "Plot available");
        const description = escapeHTML((property.description || "Prime verified land opportunity with high growth potential.").slice(0, 95));
        const whatsAppText = encodeURIComponent(`Hello I am interested in ${property.title || "this land"} at ${property.location || "your listing"}.`);

        return `
            <article class="modern-land-card glass-card reveal is-visible">
                <div class="modern-land-media">
                    ${mediaMarkup(property.media, title)}
                </div>
                <div class="modern-land-body">
                    <h3>${title}</h3>
                    <p class="land-location"><i class="fas fa-map-pin"></i> ${location}</p>
                    <p class="land-excerpt">${description}...</p>
                    <div class="land-meta">
                        <span>${area}</span>
                        <strong>${priceMarkup(property.price)}</strong>
                    </div>
                    <div class="land-actions">
                        <a href="https://wa.me/254784666927?text=${whatsAppText}" target="_blank" rel="noopener noreferrer">WhatsApp</a>
                        <a href="/properties/${escapeHTML(property._id)}">View Details</a>
                    </div>
                </div>
            </article>
        `;
    }

    function renderTestimonialCard(testimonial) {
        const rating = Math.max(1, Math.min(5, Number(testimonial.rating || 5)));
        const stars = Array.from({ length: rating }).map(() => `<i class="fas fa-star"></i>`).join("");
        const name = escapeHTML(testimonial.name || "Client");
        const location = escapeHTML(testimonial.location || "Kenya");
        const body = escapeHTML(testimonial.testimonial || "LandVista made the buying process clear and stress-free.");
        const avatar = name ? name.charAt(0).toUpperCase() : "?";

        return `
            <article class="modern-testimonial-card glass-card">
                <div class="testimonial-stars">${stars}</div>
                <p class="testimonial-text">"${body}"</p>
                <div class="testimonial-person">
                    <span>${avatar}</span>
                    <div>
                        <strong>${name}</strong>
                        <small>${location}</small>
                    </div>
                </div>
            </article>
        `;
    }

    async function loadProperties() {
        if (!landGrid || isFetchingProperties) {
            return;
        }

        isFetchingProperties = true;
        try {
            const response = await fetch("/api/properties?limit=4");
            const data = await response.json();
            const properties = (Array.isArray(data) ? data : []).slice(0, 3);
            if (!properties.length) {
                return;
            }
            landGrid.innerHTML = properties.map(renderPropertyCard).join("");
        } catch (error) {
            console.error("Failed to load properties:", error);
        } finally {
            isFetchingProperties = false;
        }
    }

    function updateTestimonialSlide(index) {
        if (!testimonialsTrack) {
            return;
        }
        const cards = testimonialsTrack.querySelectorAll(".modern-testimonial-card");
        if (!cards.length) {
            return;
        }
        testimonialIndex = (index + cards.length) % cards.length;
        testimonialsTrack.style.transform = `translateX(-${testimonialIndex * 100}%)`;
        if (testimonialsCount) {
            testimonialsCount.textContent = String(testimonialIndex + 1);
        }
    }

    function startTestimonialAutoSlide() {
        if (testimonialTimer) {
            clearInterval(testimonialTimer);
        }
        const cards = testimonialsTrack ? testimonialsTrack.querySelectorAll(".modern-testimonial-card") : [];
        if (!cards || cards.length <= 1) {
            return;
        }
        testimonialTimer = setInterval(() => {
            updateTestimonialSlide(testimonialIndex + 1);
        }, 6000);
    }

    function syncTestimonialControls() {
        const cards = testimonialsTrack ? testimonialsTrack.querySelectorAll(".modern-testimonial-card") : [];
        const total = cards ? cards.length : 0;

        if (testimonialsTotal) {
            testimonialsTotal.textContent = String(total);
        }

        if (!testimonialsControls) {
            return;
        }

        testimonialsControls.style.display = total > 1 ? "flex" : "none";
    }

    async function loadTestimonials() {
        if (!testimonialsTrack || isFetchingTestimonials) {
            return;
        }

        isFetchingTestimonials = true;
        try {
            const response = await fetch("/api/testimonials");
            const data = await response.json();
            const testimonials = Array.isArray(data) ? data : [];
            if (!testimonials.length) {
                return;
            }

            testimonialsTrack.innerHTML = testimonials.map(renderTestimonialCard).join("");
            testimonialIndex = 0;
            updateTestimonialSlide(0);
            syncTestimonialControls();
            startTestimonialAutoSlide();
        } catch (error) {
            console.error("Failed to load testimonials:", error);
        } finally {
            isFetchingTestimonials = false;
        }
    }

    function setupRevealAnimations() {
        const revealItems = document.querySelectorAll(".reveal");
        if (!revealItems.length) {
            return;
        }

        revealItems.forEach((element) => {
            const delay = element.dataset.revealDelay;
            if (delay) {
                element.style.transitionDelay = `${delay}ms`;
            }
        });

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }
                entry.target.classList.add("is-visible");
                obs.unobserve(entry.target);
            });
        }, { threshold: 0.18 });

        revealItems.forEach((item) => observer.observe(item));
    }

    function setupCounters() {
        const counterElements = document.querySelectorAll("[data-counter-target]");
        if (!counterElements.length) {
            return;
        }

        const animateCounter = (element) => {
            const target = Number(element.dataset.counterTarget || 0);
            if (!Number.isFinite(target) || target <= 0) {
                return;
            }

            const baseText = element.textContent || "";
            const hasPercent = baseText.includes("%");
            const hasCurrency = baseText.toLowerCase().includes("ksh");
            const start = 0;
            const duration = 1000;
            const startTime = performance.now();

            function tick(now) {
                const progress = Math.min((now - startTime) / duration, 1);
                const value = Math.floor(start + (target - start) * progress);

                if (hasCurrency) {
                    element.textContent = `KSh ${value.toLocaleString()}+`;
                } else if (hasPercent) {
                    element.textContent = `${value}%`;
                } else {
                    element.textContent = `${value}+`;
                }

                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            }

            requestAnimationFrame(tick);
        };

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }
                animateCounter(entry.target);
                obs.unobserve(entry.target);
            });
        }, { threshold: 0.5 });

        counterElements.forEach((counter) => observer.observe(counter));
    }

    function setupHeroParallax() {
        if (!hero || !orbA || !orbB) {
            return;
        }

        let ticking = false;

        function onScroll() {
            if (ticking) {
                return;
            }
            ticking = true;

            requestAnimationFrame(() => {
                const y = window.scrollY;
                orbA.style.transform = `translate3d(${y * -0.03}px, ${y * 0.05}px, 0)`;
                orbB.style.transform = `translate3d(${y * 0.04}px, ${y * -0.04}px, 0)`;
                ticking = false;
            });
        }

        window.addEventListener("scroll", onScroll, { passive: true });
    }

    function setupTestimonialButtons() {
        if (testimonialsPrev) {
            testimonialsPrev.addEventListener("click", () => {
                updateTestimonialSlide(testimonialIndex - 1);
                startTestimonialAutoSlide();
            });
        }

        if (testimonialsNext) {
            testimonialsNext.addEventListener("click", () => {
                updateTestimonialSlide(testimonialIndex + 1);
                startTestimonialAutoSlide();
            });
        }
    }

    function setupFaqAccordion() {
        document.querySelectorAll(".faq-toggle").forEach((btn) => {
            btn.addEventListener("click", () => {
                const item = btn.closest(".faq-item");
                if (!item) return;
                item.classList.toggle("open");
            });
        });
    }

    function setupModal() {
        if (!consultationModal) {
            return;
        }

        function closeModal() {
            consultationModal.classList.remove("open");
            consultationModal.setAttribute("aria-hidden", "true");
            document.body.style.overflow = "";
        }

        function openModal() {
            consultationModal.classList.add("open");
            consultationModal.setAttribute("aria-hidden", "false");
            document.body.style.overflow = "hidden";
        }

        modalOpeners.forEach((btn) => {
            btn.addEventListener("click", () => {
                const target = btn.getAttribute("data-modal-open");
                if (target === "consultationModal") {
                    openModal();
                }
            });
        });

        modalClosers.forEach((btn) => {
            btn.addEventListener("click", () => {
                const target = btn.getAttribute("data-modal-close");
                if (target === "consultationModal") {
                    closeModal();
                }
            });
        });

        consultationModal.addEventListener("click", (event) => {
            if (event.target === consultationModal) {
                closeModal();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && consultationModal.classList.contains("open")) {
                closeModal();
            }
        });
    }

    function setupConsultationForm() {
        if (!consultationForm || !consultationFeedback) {
            return;
        }

        consultationForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            consultationFeedback.textContent = "";
            consultationFeedback.className = "consult-feedback";

            const formData = new FormData(consultationForm);
            const submitBtn = consultationForm.querySelector("button[type='submit']");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = "Submitting...";
            }

            try {
                const response = await fetch("/inquiries/add", {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: formData
                });
                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.error || "Unable to submit request");
                }

                consultationForm.reset();
                consultationFeedback.textContent = "Request submitted successfully. Our advisor will contact you shortly.";
                consultationFeedback.classList.add("success");
            } catch (error) {
                consultationFeedback.textContent = error.message || "Unable to submit request right now.";
                consultationFeedback.classList.add("error");
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Submit Request";
                }
            }
        });
    }

    function setupCalculator() {
        if (!calculatorForm || !calculatorResult) {
            return;
        }

        function renderResult() {
            const budget = Number(document.getElementById("calcBudget")?.value || 0);
            const growth = Number(document.getElementById("calcGrowth")?.value || 0);
            const years = Number(document.getElementById("calcYears")?.value || 0);
            const projected = budget > 0 ? budget * Math.pow(1 + growth / 100, years) : 0;
            calculatorResult.textContent = `Projected value: KES ${Math.round(projected).toLocaleString()}`;
        }

        calculatorForm.addEventListener("submit", (event) => {
            event.preventDefault();
            renderResult();
        });

        calculatorForm.querySelectorAll("input").forEach((input) => {
            input.addEventListener("input", renderResult);
        });

        renderResult();
    }

    function setupNewsletter() {
        if (!newsletterForm) {
            return;
        }

        const successMsg = document.getElementById("newsletterSuccess");
        const successText = document.getElementById("newsletterSuccessText");
        const errorMsg = document.getElementById("newsletterError");
        const errorText = document.getElementById("newsletterErrorText");
        const submitBtn = newsletterForm.querySelector(".newsletter-btn");

        newsletterForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            if (!submitBtn) {
                return;
            }

            const emailInput = newsletterForm.querySelector('input[name="email"]');
            const email = emailInput ? emailInput.value.trim() : "";
            if (!email) {
                return;
            }

            if (successMsg) {
                successMsg.style.display = "none";
            }
            if (errorMsg) {
                errorMsg.style.display = "none";
            }

            submitBtn.disabled = true;
            submitBtn.textContent = "Subscribing...";

            try {
                const response = await fetch("/api/newsletter/subscribe", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email })
                });
                const data = await response.json();

                if (data.success) {
                    newsletterForm.reset();
                    if (successText) {
                        successText.textContent = data.message || "Subscription successful. Check your inbox for confirmation.";
                    }
                    if (successMsg) {
                        successMsg.style.display = "flex";
                    }
                } else {
                    if (errorText) {
                        errorText.textContent = data.message || "Could not subscribe right now. Try again.";
                    }
                    if (errorMsg) {
                        errorMsg.style.display = "flex";
                    }
                }
            } catch (error) {
                if (errorText) {
                    errorText.textContent = "Network error while subscribing. Please try again.";
                }
                if (errorMsg) {
                    errorMsg.style.display = "flex";
                }
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = "Subscribe";
            }
        });
    }

    function setupRealtimeRefresh() {
        if (typeof io !== "function") {
            return;
        }

        const socket = io();
        const propertyEvents = ["property_created", "property_updated", "property_deleted"];
        const testimonialEvents = ["testimonial_added", "testimonial_updated", "testimonial_deleted"];

        propertyEvents.forEach((eventName) => {
            socket.on(eventName, () => loadProperties());
        });

        testimonialEvents.forEach((eventName) => {
            socket.on(eventName, () => loadTestimonials());
        });
    }

    function scheduleRefreshLoop() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }

        if (document.hidden) {
            return;
        }

        refreshInterval = setInterval(() => {
            loadProperties();
            loadTestimonials();
        }, 30000);
    }

    document.addEventListener("visibilitychange", scheduleRefreshLoop);

    loadProperties();
    loadTestimonials();
    setupRevealAnimations();
    setupCounters();
    setupHeroParallax();
    setupTestimonialButtons();
    setupFaqAccordion();
    setupModal();
    setupConsultationForm();
    setupCalculator();
    setupNewsletter();
    setupRealtimeRefresh();
    scheduleRefreshLoop();
})();
