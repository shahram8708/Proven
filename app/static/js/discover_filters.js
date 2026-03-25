/* ========================================
   Proven — Discover Search & Filters
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('discover-filters');
    if (!filterForm) return;

    const resultsContainer = document.getElementById('search-results');
    const resultsCount = document.getElementById('results-count');
    const loadingIndicator = document.getElementById('search-loading');

    // --- AJAX Search ---
    function performSearch() {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData);

        if (loadingIndicator) loadingIndicator.classList.remove('d-none');

        fetch('/discover/search?' + params.toString(), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (resultsContainer) resultsContainer.innerHTML = data.html;
            if (resultsCount) resultsCount.textContent = data.total + ' results';
            if (loadingIndicator) loadingIndicator.classList.add('d-none');
            updateActiveFilters(formData);
        })
        .catch(function () {
            if (loadingIndicator) loadingIndicator.classList.add('d-none');
        });
    }

    // --- Filter Change Listeners ---
    filterForm.querySelectorAll('select, input[type="checkbox"]').forEach(function (el) {
        el.addEventListener('change', performSearch);
    });

    // --- Debounced Text Search ---
    let searchTimer = null;
    const searchInput = filterForm.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            if (searchTimer) clearTimeout(searchTimer);
            searchTimer = setTimeout(performSearch, 400);
        });
    }

    // --- Active Filters Display ---
    function updateActiveFilters(formData) {
        const container = document.getElementById('active-filters');
        if (!container) return;
        container.innerHTML = '';

        for (const [key, value] of formData.entries()) {
            if (!value || key === 'q' || key === 'page') continue;
            const tag = document.createElement('span');
            tag.classList.add('active-filter-tag');
            tag.innerHTML = value + ' <span class="remove-filter" data-field="' + key + '">&times;</span>';
            container.appendChild(tag);
        }

        container.querySelectorAll('.remove-filter').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const field = this.dataset.field;
                const input = filterForm.querySelector('[name="' + field + '"]');
                if (input) {
                    if (input.type === 'checkbox') input.checked = false;
                    else input.value = '';
                    performSearch();
                }
            });
        });
    }

    // --- Clear All Filters ---
    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            filterForm.reset();
            performSearch();
        });
    }

    // --- Form Submit Prevention ---
    filterForm.addEventListener('submit', function (e) {
        e.preventDefault();
        performSearch();
    });
});
