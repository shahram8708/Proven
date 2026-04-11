/* ========================================
   Proven — Discover Search & Filters
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('searchFilters') || document.getElementById('discover-filters');
    if (!filterForm) return;

    const loadingIndicator = document.getElementById('search-loading');
    let submitTimer = null;

    function performSearch() {
        if (loadingIndicator) loadingIndicator.classList.remove('d-none');
        filterForm.requestSubmit();
    }

    function performSearchDebounced(delayMs) {
        if (submitTimer) clearTimeout(submitTimer);
        submitTimer = setTimeout(performSearch, delayMs);
    }

    filterForm.querySelectorAll('select, input[type="checkbox"], input[type="number"]').forEach(function (el) {
        el.addEventListener('change', function () {
            performSearchDebounced(150);
        });
    });

    filterForm.querySelectorAll('input[name="keyword"], input[name="skills"], input[name="region"], input[name="country"]').forEach(function (input) {
        input.addEventListener('input', function () {
            performSearchDebounced(400);
        });
    });

    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            filterForm.reset();
            performSearchDebounced(50);
        });
    }

    // Keep regular GET submit behavior for explicit Search button clicks.
});
