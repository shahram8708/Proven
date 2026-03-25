/* ========================================
   Proven — Main JavaScript
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {

    // --- Flash Message Auto-dismiss ---
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // --- Navbar Scroll Effect ---
    const navbar = document.querySelector('.navbar-proven');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 10) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }

    // --- Tooltip Init ---
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // --- Confirm Delete ---
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // --- Character Counter ---
    document.querySelectorAll('[data-char-count]').forEach(function (textarea) {
        const max = parseInt(textarea.dataset.charCount);
        const counter = document.getElementById(textarea.dataset.charCountTarget);
        if (!counter) return;
        function update() {
            const remaining = max - textarea.value.length;
            counter.textContent = remaining + ' characters remaining';
            counter.classList.toggle('text-danger', remaining < 0);
        }
        textarea.addEventListener('input', update);
        update();
    });

    // --- Smooth Scroll for Anchor Links ---
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // --- Copy to Clipboard ---
    document.querySelectorAll('[data-copy]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const text = this.dataset.copy;
            navigator.clipboard.writeText(text).then(function () {
                btn.textContent = 'Copied!';
                setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
            });
        });
    });
});

/* --- Utility: Format INR --- */
function formatINR(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN');
}

/* --- Utility: Time Ago --- */
function timeAgo(dateStr) {
    const now = new Date();
    const date = new Date(dateStr);
    const seconds = Math.floor((now - date) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return minutes + 'm ago';
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return hours + 'h ago';
    const days = Math.floor(hours / 24);
    if (days < 30) return days + 'd ago';
    const months = Math.floor(days / 30);
    return months + 'mo ago';
}
