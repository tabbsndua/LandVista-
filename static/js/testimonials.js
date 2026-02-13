/* ============================================================
   LANDVISTA ADMIN – TESTIMONIALS (REAL-TIME)
   File: static/js/admin/testimonials.js
   Purpose:
   - Live testimonials rendering
   - Add / Publish / Unpublish / Delete
   - No page refresh (SSE)
============================================================ */

/* =========================
   DOM ELEMENTS
========================= */
const grid = document.getElementById("testimonialGrid");
const modal = document.getElementById("testimonialModal");

const nameInput = document.getElementById("name");
const locationInput = document.getElementById("location");
const propertyInput = document.getElementById("property");
const ratingInput = document.getElementById("rating");
const messageInput = document.getElementById("message");

/* =========================
   SAFETY CHECK
========================= */
if (!grid) {
    console.warn("Testimonials grid not found.");
}

/* =========================
   REAL-TIME STREAM (SSE)
========================= */
const source = new EventSource("/admin/testimonials/stream");

source.onmessage = function (event) {
    try {
        const testimonials = JSON.parse(event.data);
        renderTestimonials(testimonials);
    } catch (e) {
        console.error("SSE parse error:", e);
    }
};

source.onerror = function () {
    console.warn("Testimonials stream disconnected. Retrying...");
};

/* =========================
   RENDER TESTIMONIALS
========================= */
function renderTestimonials(data) {
    if (!grid) return;

    grid.innerHTML = "";

    if (!data.length) {
        grid.innerHTML = "<p>No testimonials found.</p>";
        return;
    }

    data.forEach(t => {
        const card = document.createElement("div");
        card.className = "testimonial-card";

        card.innerHTML = `
            <div class="testimonial-header">
                <div class="avatar">${t.name ? t.name.charAt(0).toUpperCase() : "?"}</div>
                <div>
                    <h4>${escapeHTML(t.name)}</h4>
                    <small>${escapeHTML(t.location || "")}</small>
                </div>
            </div>

            <div class="rating">
                ${"★".repeat(t.rating || 0)}
            </div>

            <p class="testimonial-message">
                "${escapeHTML(t.message || "")}"
            </p>

            <div class="testimonial-meta">
                ${t.property ? `<small>Property: ${escapeHTML(t.property)}</small>` : ""}
            </div>

            <div class="testimonial-badges">
                <span class="badge ${t.status}">${t.status}</span>
                ${t.featured ? `<span class="badge featured">Featured</span>` : ""}
            </div>

            <div class="testimonial-actions">
                ${t.status !== "published" ? `
                    <button class="btn-publish" onclick="publishTestimonial('${t._id}')">
                        Publish
                    </button>` : `
                    <button class="btn-unpublish" onclick="unpublishTestimonial('${t._id}')">
                        Unpublish
                    </button>`}

                <button class="btn-delete" onclick="deleteTestimonial('${t._id}')">
                    Delete
                </button>
            </div>
        `;

        grid.appendChild(card);
    });
}

/* =========================
   ADD TESTIMONIAL
========================= */
function saveTestimonial() {
    if (!nameInput.value || !messageInput.value) {
        alert("Name and message are required.");
        return;
    }

    fetch("/admin/testimonials/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: nameInput.value.trim(),
            location: locationInput.value.trim(),
            property: propertyInput.value.trim(),
            rating: ratingInput.value,
            message: messageInput.value.trim()
        })
    })
    .then(() => {
        closeModal();
        clearForm();
    })
    .catch(err => console.error("Add testimonial error:", err));
}

/* =========================
   PUBLISH / UNPUBLISH
========================= */
function publishTestimonial(id) {
    updateTestimonial(id, { status: "published" });
}

function unpublishTestimonial(id) {
    updateTestimonial(id, { status: "draft" });
}

function updateTestimonial(id, payload) {
    fetch(`/admin/testimonials/update/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    }).catch(err => console.error("Update error:", err));
}

/* =========================
   DELETE
========================= */
function deleteTestimonial(id) {
    if (!confirm("Delete this testimonial permanently?")) return;

    fetch(`/admin/testimonials/delete/${id}`, {
        method: "DELETE"
    }).catch(err => console.error("Delete error:", err));
}

/* =========================
   MODAL CONTROLS
========================= */
function openModal() {
    modal.style.display = "flex";
}

function closeModal() {
    modal.style.display = "none";
}

window.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
});

/* =========================
   HELPERS
========================= */
function clearForm() {
    nameInput.value = "";
    locationInput.value = "";
    propertyInput.value = "";
    ratingInput.value = "5";
    messageInput.value = "";
}

function escapeHTML(str) {
    return str.replace(/[&<>"']/g, function (m) {
        return ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[m];
    });
}
