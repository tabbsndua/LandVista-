(() => {
    const grid = document.getElementById("propertiesGrid");
    const noResults = document.getElementById("noResultsMessage");
    const resultsCounter = document.getElementById("resultsCounter");
    const locationInput = document.getElementById("locationFilter");
    const availabilitySelect = document.getElementById("availabilityFilter");
    const priceSelect = document.getElementById("priceFilter");
    const sortSelect = document.getElementById("sortFilter");
    const maxBudgetRange = document.getElementById("maxBudgetRange");
    const maxBudgetValue = document.getElementById("maxBudgetValue");
    const activeFilterTags = document.getElementById("activeFilterTags");
    const applyBtn = document.getElementById("applyFiltersBtn");
    const resetBtn = document.getElementById("resetFiltersBtn");
    const noResultResetBtn = document.getElementById("noResultResetBtn");
    const chips = document.querySelectorAll(".chip");
    const viewButtons = document.querySelectorAll(".view-btn");
    const quickViewModal = document.getElementById("quickViewModal");
    const quickViewContent = document.getElementById("quickViewContent");
    const quickCloseBtn = document.getElementById("quickCloseBtn");

    let allProperties = [];
    let filteredProperties = [];
    let refreshTimer = null;
    let isFetching = false;

    function normalizeMedia(media) {
        if (!media) return "";
        if (Array.isArray(media) && media.length) return media[0];
        if (typeof media === "string") return media;
        return "";
    }

    function escapeHTML(value) {
        return String(value || "").replace(/[&<>"']/g, (char) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[char]));
    }

    function parseInitialCards() {
        if (!grid) return [];
        return Array.from(grid.querySelectorAll(".property-card")).map((card) => ({
            _id: card.dataset.propertyId || "",
            title: card.dataset.propertyTitle || "",
            location: card.dataset.propertyLocation || "",
            area: card.dataset.propertyArea || "",
            price: Number(card.dataset.propertyPrice || 0),
            status: card.dataset.propertyStatus || "available",
            description: card.dataset.propertyDescription || "",
            media: (() => {
                const image = card.querySelector(".property-media img");
                if (!image) return "";
                const src = image.getAttribute("src") || "";
                const marker = "/static/uploads/";
                const idx = src.indexOf(marker);
                return idx >= 0 ? decodeURIComponent(src.slice(idx + marker.length)) : "";
            })()
        }));
    }

    function mediaMarkup(property) {
        const media = normalizeMedia(property.media);
        if (!media) {
            return `<img loading="lazy" src="/static/images/placeholder.jpg" alt="${escapeHTML(property.title)}">`;
        }

        const src = `/static/uploads/${encodeURIComponent(media)}`;
        if (/\.(mp4|webm|mov)$/i.test(media)) {
            return `<video muted preload="metadata" playsinline><source src="${src}"></video>`;
        }
        return `<img loading="lazy" src="${src}" alt="${escapeHTML(property.title)}">`;
    }

    function statusLabel(status) {
        return String(status || "").toLowerCase() === "sold" ? "Sold" : "Available";
    }

    function buildPropertyCard(property) {
        const id = escapeHTML(property._id || "");
        const title = escapeHTML(property.title || "Untitled Property");
        const location = escapeHTML(property.location || "Kenya");
        const area = escapeHTML(property.area || "Plot available");
        const description = escapeHTML((property.description || "Prime verified property in a strategic growth location.").slice(0, 110));
        const price = Number(property.price || 0);
        const displayPrice = `KSh ${price.toLocaleString()}`;
        const statusRaw = String(property.status || "available").toLowerCase();
        const status = statusRaw === "sold" ? "sold" : "available";

        return `
            <article class="property-card" data-property-id="${id}" data-property-title="${title}" data-property-location="${location}" data-property-area="${area}" data-property-price="${price}" data-property-status="${status}" data-property-description="${description}">
                <div class="property-media">
                    ${mediaMarkup(property)}
                    <span class="status-badge ${status}">${statusLabel(status)}</span>
                </div>
                <div class="property-content">
                    <h3>${title}</h3>
                    <p class="property-location"><i class="fas fa-map-pin"></i> ${location}</p>
                    <p class="property-desc">${description}...</p>
                    <div class="property-meta">
                        <span>${area}</span>
                        <strong>${displayPrice}</strong>
                    </div>
                    <div class="property-actions">
                        <button class="card-btn ghost quick-view-btn" type="button" data-quick-view="${id}">Quick View</button>
                        <a class="card-btn solid" href="/properties/${id}">Details</a>
                    </div>
                </div>
            </article>
        `;
    }

    function updateResultsCounter(count) {
        if (!resultsCounter) return;
        resultsCounter.textContent = `${count} ${count === 1 ? "property" : "properties"}`;
    }

    function renderProperties(properties) {
        if (!grid) return;

        if (!properties.length) {
            grid.innerHTML = "";
            if (noResults) noResults.style.display = "block";
            updateResultsCounter(0);
            return;
        }

        grid.innerHTML = properties.map(buildPropertyCard).join("");
        if (noResults) noResults.style.display = "none";
        updateResultsCounter(properties.length);
    }

    function applyFilters() {
        const keyword = (locationInput?.value || "").trim().toLowerCase();
        const status = (availabilitySelect?.value || "available").toLowerCase();
        const priceRange = priceSelect?.value || "";
        const sortBy = sortSelect?.value || "latest";
        const maxBudget = Number(maxBudgetRange?.value || 10000000);

        filteredProperties = allProperties.filter((property) => {
            const title = String(property.title || "").toLowerCase();
            const location = String(property.location || "").toLowerCase();
            const normalizedStatus = String(property.status || "available").toLowerCase();
            const propertyStatus = normalizedStatus === "sold" ? "sold" : "available";
            const price = Number(property.price || 0);

            const keywordMatch = !keyword || title.includes(keyword) || location.includes(keyword);
            const statusMatch = status === "all" || propertyStatus === status;

            let priceMatch = true;
            if (priceRange === "0-500000") priceMatch = price >= 0 && price <= 500000;
            if (priceRange === "500000-1000000") priceMatch = price > 500000 && price <= 1000000;
            if (priceRange === "1000000-5000000") priceMatch = price > 1000000 && price <= 5000000;
            if (priceRange === "5000000+") priceMatch = price > 5000000;
            if (price > maxBudget) priceMatch = false;

            return keywordMatch && statusMatch && priceMatch;
        });

        if (sortBy === "price_low_high") {
            filteredProperties.sort((a, b) => Number(a.price || 0) - Number(b.price || 0));
        } else if (sortBy === "price_high_low") {
            filteredProperties.sort((a, b) => Number(b.price || 0) - Number(a.price || 0));
        } else if (sortBy === "title_az") {
            filteredProperties.sort((a, b) => String(a.title || "").localeCompare(String(b.title || "")));
        } else {
            filteredProperties.sort((a, b) => String(b._id || "").localeCompare(String(a._id || "")));
        }

        renderProperties(filteredProperties);
        updateActiveFilterTags(keyword, status, priceRange, maxBudget);
    }

    function updateActiveFilterTags(keyword, status, priceRange, maxBudget) {
        if (!activeFilterTags) return;
        const tags = [];
        if (keyword) tags.push(`Keyword: ${keyword}`);
        if (status && status !== "all") tags.push(`Status: ${status}`);
        if (priceRange) tags.push(`Range: ${priceRange.replace("-", " to ")}`);
        if (Number.isFinite(maxBudget) && maxBudget < 10000000) {
            tags.push(`Max budget: KSh ${maxBudget.toLocaleString()}`);
        }

        activeFilterTags.innerHTML = tags.map((item) => `<span class="tag">${escapeHTML(item)}</span>`).join("");
    }

    async function fetchProperties() {
        if (isFetching) return;
        isFetching = true;
        try {
            const response = await fetch("/api/properties");
            const data = await response.json();
            if (!Array.isArray(data)) {
                return;
            }
            allProperties = data;
            applyFilters();
        } catch (error) {
            console.error("Failed to fetch properties:", error);
        } finally {
            isFetching = false;
        }
    }

    function openQuickView(propertyId) {
        if (!quickViewModal || !quickViewContent) return;
        const property = allProperties.find((item) => String(item._id) === String(propertyId));
        if (!property) return;

        const title = escapeHTML(property.title || "Untitled Property");
        const location = escapeHTML(property.location || "Kenya");
        const area = escapeHTML(property.area || "Plot available");
        const price = `KSh ${Number(property.price || 0).toLocaleString()}`;
        const status = statusLabel(property.status);
        const description = escapeHTML(property.description || "Verified listing with strategic location and growth potential.");
        const waText = encodeURIComponent(`Hello, I am interested in ${property.title || "this property"} at ${property.location || "your listing"}.`);

        quickViewContent.innerHTML = `
            <div class="quick-view-content">
                <h3>${title}</h3>
                <p><i class="fas fa-map-pin"></i> ${location}</p>
                <p>${description}</p>
                <div class="quick-view-meta">
                    <div><span>Price</span><strong>${price}</strong></div>
                    <div><span>Area</span><strong>${area}</strong></div>
                    <div><span>Status</span><strong>${status}</strong></div>
                </div>
                <div class="quick-view-links">
                    <a class="details-link" href="/properties/${escapeHTML(property._id)}">Open details</a>
                    <a class="wa-link" target="_blank" rel="noopener noreferrer" href="https://wa.me/254784666927?text=${waText}">WhatsApp</a>
                </div>
            </div>
        `;

        quickViewModal.classList.add("open");
        quickViewModal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function closeQuickView() {
        if (!quickViewModal) return;
        quickViewModal.classList.remove("open");
        quickViewModal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    }

    function syncChips(status) {
        chips.forEach((chip) => {
            chip.classList.toggle("active", chip.dataset.chipStatus === status);
        });
    }

    function setView(view) {
        if (!grid) return;
        const normalized = view === "list" ? "list" : "grid";
        grid.classList.toggle("list-view", normalized === "list");
        grid.classList.toggle("grid-view", normalized !== "list");
        viewButtons.forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.view === normalized);
        });
    }

    function setupEvents() {
        applyBtn?.addEventListener("click", applyFilters);
        resetBtn?.addEventListener("click", () => {
            if (locationInput) locationInput.value = "";
            if (availabilitySelect) availabilitySelect.value = "available";
            if (priceSelect) priceSelect.value = "";
            if (sortSelect) sortSelect.value = "latest";
            if (maxBudgetRange) maxBudgetRange.value = "10000000";
            if (maxBudgetValue) maxBudgetValue.textContent = "Any budget";
            syncChips("available");
            applyFilters();
        });
        noResultResetBtn?.addEventListener("click", () => resetBtn?.click());

        locationInput?.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                applyFilters();
            }
        });

        availabilitySelect?.addEventListener("change", () => {
            syncChips(availabilitySelect.value);
            applyFilters();
        });

        priceSelect?.addEventListener("change", applyFilters);
        sortSelect?.addEventListener("change", applyFilters);
        maxBudgetRange?.addEventListener("input", () => {
            const maxBudget = Number(maxBudgetRange.value || 10000000);
            if (maxBudgetValue) {
                maxBudgetValue.textContent = maxBudget >= 10000000 ? "Any budget" : `Up to KSh ${maxBudget.toLocaleString()}`;
            }
            applyFilters();
        });

        chips.forEach((chip) => {
            chip.addEventListener("click", () => {
                const status = chip.dataset.chipStatus || "available";
                if (availabilitySelect) availabilitySelect.value = status;
                syncChips(status);
                applyFilters();
            });
        });

        viewButtons.forEach((btn) => {
            btn.addEventListener("click", () => setView(btn.dataset.view));
        });

        grid?.addEventListener("click", (event) => {
            const btn = event.target.closest(".quick-view-btn");
            if (!btn) return;
            openQuickView(btn.dataset.quickView || "");
        });

        quickCloseBtn?.addEventListener("click", closeQuickView);
        quickViewModal?.addEventListener("click", (event) => {
            if (event.target === quickViewModal) {
                closeQuickView();
            }
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && quickViewModal?.classList.contains("open")) {
                closeQuickView();
            }
        });
    }

    function setupRealtime() {
        if (typeof io !== "function") return;
        const socket = io();
        ["property_created", "property_updated", "property_deleted"].forEach((eventName) => {
            socket.on(eventName, fetchProperties);
        });
    }

    function setupRefreshLoop() {
        if (refreshTimer) {
            clearInterval(refreshTimer);
            refreshTimer = null;
        }
        if (document.hidden) {
            return;
        }
        refreshTimer = setInterval(fetchProperties, 45000);
    }

    document.addEventListener("visibilitychange", setupRefreshLoop);

    allProperties = parseInitialCards();
    filteredProperties = [...allProperties];
    if (maxBudgetValue && maxBudgetRange) {
        maxBudgetValue.textContent = Number(maxBudgetRange.value) >= 10000000 ? "Any budget" : `Up to KSh ${Number(maxBudgetRange.value).toLocaleString()}`;
    }
    syncChips((availabilitySelect?.value || "available").toLowerCase());
    setView("grid");
    setupEvents();
    setupRealtime();
    fetchProperties();
    applyFilters();
    setupRefreshLoop();
})();
