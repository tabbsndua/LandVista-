(() => {
    const navbar = document.querySelector(".navbar");
    const navToggle = document.getElementById("navToggle");
    const siteNav = document.getElementById("siteNav");
    const dropdown = siteNav ? siteNav.querySelector(".nav-dropdown") : null;
    const dropdownToggle = dropdown ? dropdown.querySelector(".dropdown-toggle") : null;

    function updateNavbarState() {
        if (!navbar) {
            return;
        }
        navbar.classList.toggle("scrolled", window.scrollY > 12);
    }

    function closeMobileNav() {
        if (!navbar || !siteNav || !navToggle) {
            return;
        }
        navbar.classList.remove("nav-open");
        navToggle.setAttribute("aria-expanded", "false");
        if (dropdown) {
            dropdown.classList.remove("open");
        }
    }

    if (navToggle && navbar && siteNav) {
        navToggle.addEventListener("click", () => {
            const isOpen = navbar.classList.toggle("nav-open");
            navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
            if (!isOpen && dropdown) {
                dropdown.classList.remove("open");
            }
        });

        document.addEventListener("click", (event) => {
            if (!navbar.classList.contains("nav-open")) {
                return;
            }
            if (!navbar.contains(event.target)) {
                closeMobileNav();
            }
        });

        siteNav.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                if (window.innerWidth <= 992) {
                    closeMobileNav();
                }
            });
        });
    }

    if (dropdown && dropdownToggle) {
        dropdownToggle.addEventListener("click", (event) => {
            if (window.innerWidth > 992) {
                return;
            }
            event.preventDefault();
            dropdown.classList.toggle("open");
        });
    }

    updateNavbarState();
    window.addEventListener("scroll", updateNavbarState, { passive: true });
    window.addEventListener("resize", () => {
        if (window.innerWidth > 992) {
            closeMobileNav();
        }
    });
})();
