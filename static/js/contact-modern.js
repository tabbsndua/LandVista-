(() => {
    const contactForm = document.getElementById("contactForm");
    const contactSubmitBtn = document.getElementById("contactSubmitBtn");
    const contactSuccess = document.getElementById("contactSuccess");
    const contactError = document.getElementById("contactError");

    const visitModal = document.getElementById("visitModal");
    const openVisitModalBtn = document.getElementById("openVisitModalBtn");
    const visitCloseBtn = document.getElementById("visitCloseBtn");
    const visitCancelBtn = document.getElementById("visitCancelBtn");
    const visitForm = document.getElementById("visitForm");
    const visitSubmitBtn = document.getElementById("visitSubmitBtn");
    const visitSuccess = document.getElementById("visitSuccess");
    const visitError = document.getElementById("visitError");

    function showAlert(target, message) {
        if (!target) return;
        target.textContent = message;
        target.style.display = "block";
    }

    function hideAlert(target) {
        if (!target) return;
        target.style.display = "none";
        target.textContent = "";
    }

    function closeVisitModal() {
        if (!visitModal) return;
        visitModal.classList.remove("open");
        visitModal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    }

    function openVisitModal() {
        if (!visitModal) return;
        visitModal.classList.add("open");
        visitModal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    contactForm?.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideAlert(contactSuccess);
        hideAlert(contactError);

        if (contactSubmitBtn) {
            contactSubmitBtn.disabled = true;
            contactSubmitBtn.textContent = "Sending...";
        }

        try {
            const formData = new FormData(contactForm);
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
                throw new Error(data.error || "Failed to submit inquiry");
            }

            contactForm.reset();
            showAlert(contactSuccess, "Your inquiry was submitted successfully. Our team will contact you soon.");
        } catch (error) {
            showAlert(contactError, `${error.message}. Please try again.`);
        } finally {
            if (contactSubmitBtn) {
                contactSubmitBtn.disabled = false;
                contactSubmitBtn.textContent = "Send Inquiry";
            }
        }
    });

    openVisitModalBtn?.addEventListener("click", openVisitModal);
    visitCloseBtn?.addEventListener("click", closeVisitModal);
    visitCancelBtn?.addEventListener("click", closeVisitModal);
    visitModal?.addEventListener("click", (event) => {
        if (event.target === visitModal) {
            closeVisitModal();
        }
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && visitModal?.classList.contains("open")) {
            closeVisitModal();
        }
    });

    visitForm?.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideAlert(visitSuccess);
        hideAlert(visitError);

        if (visitSubmitBtn) {
            visitSubmitBtn.disabled = true;
            visitSubmitBtn.textContent = "Scheduling...";
        }

        try {
            const formData = new FormData(visitForm);
            const payload = new FormData();
            payload.append("name", String(formData.get("name") || "").trim());
            payload.append("email", String(formData.get("email") || "").trim());
            payload.append("phone", String(formData.get("phone") || "").trim());
            payload.append("property_id", "");
            payload.append("property_title", String(formData.get("property_title") || "Contact Booking").trim());

            const date = String(formData.get("visit_date") || "").trim();
            const time = String(formData.get("visit_time") || "").trim();
            payload.append("visit_date", time ? `${date} ${time}` : date);
            payload.append("notes", String(formData.get("notes") || "").trim());

            const response = await fetch("/submit-site-visit", {
                method: "POST",
                body: payload
            });
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || data.error || "Failed to schedule visit");
            }

            visitForm.reset();
            showAlert(visitSuccess, data.message || "Site visit scheduled. We have sent confirmation details.");
            setTimeout(closeVisitModal, 1200);
        } catch (error) {
            showAlert(visitError, `${error.message}. Please try again.`);
        } finally {
            if (visitSubmitBtn) {
                visitSubmitBtn.disabled = false;
                visitSubmitBtn.textContent = "Schedule Visit";
            }
        }
    });
})();
