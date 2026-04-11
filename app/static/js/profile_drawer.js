/* ========================================
   Proven — Profile Drawer (Discover)
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {
    const drawer = document.getElementById('profileDrawer') || document.getElementById('profile-drawer');
    const backdrop = document.getElementById('drawerBackdrop') || document.getElementById('profile-drawer-backdrop');
    if (!drawer) return;

    const drawerBody = document.getElementById('drawerContent') || drawer.querySelector('.profile-drawer-body');
    const drawerTitle = document.getElementById('drawerName');

    function openClass(el) {
        if (!el) return;
        if (el.id === 'profileDrawer' || el.id === 'drawerBackdrop') {
            el.classList.add('open');
            return;
        }
        el.classList.add('active');
    }

    function closeClass(el) {
        if (!el) return;
        if (el.id === 'profileDrawer' || el.id === 'drawerBackdrop') {
            el.classList.remove('open');
            return;
        }
        el.classList.remove('active');
    }

    function openDrawer(userId) {
        openClass(drawer);
        openClass(backdrop);
        document.body.style.overflow = 'hidden';

        if (drawerTitle) {
            drawerTitle.textContent = 'Loading...';
        }

        if (drawerBody) {
            drawerBody.innerHTML = '<div class="drawer-loading"><i class="fas fa-spinner fa-spin me-2"></i> Loading profile...</div>';
        }

        fetch('/discover/profile/' + userId, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function (res) {
            if (!res.ok) throw new Error('Failed to load profile');
            return res.json();
        })
        .then(function (data) {
            if (drawerTitle) {
                drawerTitle.textContent = data.full_name || data.username || 'Profile';
            }

            if (drawerBody) {
                const evidence = Array.isArray(data.evidence) ? data.evidence : [];
                const skills = Array.isArray(data.skills) ? data.skills : [];
                const lists = Array.isArray(window.DISCOVER_TALENT_LISTS) ? window.DISCOVER_TALENT_LISTS : [];
                const location = data.location || 'Location not specified';
                const domain = data.primary_domain || 'Professional';
                const summary = data.professional_summary || 'No professional summary provided yet.';
                const openToOpportunities = data.open_to_opportunities ? 'Open to opportunities' : 'Not currently open';

                let html = '<div class="d-flex gap-4 mb-3">';
                html += '<div><strong>' + evidence.length + '</strong> <small class="text-muted">Evidence</small></div>';
                html += '<div><strong>' + skills.length + '</strong> <small class="text-muted">Skills</small></div>';
                html += '<div><strong>' + Math.round(data.profile_strength || 0) + '</strong> <small class="text-muted">Score</small></div>';
                html += '</div>';

                html += '<p class="small mb-2"><span class="badge bg-light text-dark">' + domain + '</span> <span class="text-muted ms-1"><i class="fas fa-map-marker-alt"></i> ' + location + '</span></p>';
                html += '<p class="small text-muted">' + summary + '</p>';
                html += '<p class="small text-muted"><i class="fas fa-briefcase me-1"></i>' + openToOpportunities + '</p>';

                if (skills.length > 0) {
                    html += '<h6 class="mt-3 mb-2">Top Skills</h6><div class="d-flex flex-wrap gap-1">';
                    skills.slice(0, 8).forEach(function (skill) {
                        html += '<span class="skill-tag">' + (skill.name || '') + '</span>';
                    });
                    html += '</div>';
                }

                if (evidence.length > 0) {
                    html += '<h6 class="mt-3 mb-2">Recent Evidence</h6><ul class="small text-muted ps-3 mb-3">';
                    evidence.slice(0, 3).forEach(function (item) {
                        html += '<li>' + (item.title || 'Untitled evidence') + '</li>';
                    });
                    html += '</ul>';
                }

                html += '<div class="d-flex gap-2 mt-3">';
                html += '<a href="/profile/' + data.username + '" class="btn btn-proven-primary btn-sm flex-fill">View Full Profile</a>';
                html += '<button class="btn btn-outline-primary btn-sm flex-fill" onclick="requestContact(' + data.id + ', this)">Request Contact</button>';
                html += '</div>';

                html += '<div id="drawerStatus" class="alert d-none py-2 px-3 mt-3 mb-0" role="alert"></div>';

                if (lists.length > 0) {
                    var options = lists.map(function (list) {
                        return '<option value="' + list.id + '">' + list.name + '</option>';
                    }).join('');
                    html += '<div class="mt-3">';
                    html += '<label class="form-label small fw-semibold mb-1">Save To List</label>';
                    html += '<div class="d-flex gap-2">';
                    html += '<select id="saveListSelect" class="form-select form-select-sm">' + options + '</select>';
                    html += '<button class="btn btn-outline-secondary btn-sm" onclick="addToList(' + data.id + ', this)">Save</button>';
                    html += '</div>';
                    html += '</div>';
                } else {
                    html += '<p class="small text-muted mt-3 mb-0">No talent list yet. <a href="/discover/lists">Create one</a>.</p>';
                }

                drawerBody.innerHTML = html;
            }
        })
        .catch(function () {
            if (drawerBody) {
                drawerBody.innerHTML = '<div class="text-center text-muted py-4">Failed to load profile</div>';
            }
        });
    }

    function closeDrawer() {
        closeClass(drawer);
        closeClass(backdrop);
        document.body.style.overflow = '';
    }

    if (backdrop) backdrop.addEventListener('click', closeDrawer);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeDrawer();
    });

    document.addEventListener('click', function (e) {
        const card = e.target.closest('[data-user-id]');
        if (card) {
            e.preventDefault();
            openDrawer(card.dataset.userId);
        }
    });

    window.openProfileDrawer = openDrawer;
    window.closeProfileDrawer = closeDrawer;
});

function requestContact(userId) {
    var btn = arguments.length > 1 ? arguments[1] : null;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    if (btn) {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = 'Sending...';
    }

    fetch('/discover/contact/' + userId, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(function (res) {
        const contentType = res.headers.get('content-type') || '';
        if (contentType.indexOf('application/json') !== -1) {
            return res.json().then(function (data) {
                if (!res.ok) {
                    throw new Error(data.error || data.message || 'Unable to send contact request.');
                }
                return data;
            });
        }
        if (res.redirected && res.url && res.url.indexOf('/login') !== -1) {
            window.location.href = '/login?next=' + encodeURIComponent('/discover');
            return null;
        }
        throw new Error('Unable to send contact request.');
    })
    .then(function (data) {
        if (!data) return;
        if (data.success) {
            showDrawerStatus('Contact request sent. The talent has been added to your list.', 'success');
        } else {
            showDrawerStatus(data.error || data.message || 'Unable to send contact request.', 'danger');
        }
    })
    .catch(function (err) {
        showDrawerStatus(err.message || 'Something went wrong. Please try again.', 'danger');
    })
    .finally(function () {
        if (btn) {
            btn.disabled = false;
            btn.textContent = btn.dataset.originalText || 'Request Contact';
        }
    });
}

function addToList(userId, btn) {
    const select = document.getElementById('saveListSelect');
    if (!select || !select.value) {
        showDrawerStatus('Please select a list first.', 'warning');
        return;
    }

    const listId = parseInt(select.value, 10);
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    if (btn) {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = 'Saving...';
    }

    fetch('/discover/lists/' + listId + '/add', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ talent_user_id: userId })
    })
    .then(function (res) {
        return res.json().then(function (data) {
            if (!res.ok) {
                throw new Error(data.error || 'Unable to save to list.');
            }
            return data;
        });
    })
    .then(function () {
        showDrawerStatus('Saved to list successfully.', 'success');
    })
    .catch(function (err) {
        showDrawerStatus(err.message || 'Unable to save to list.', 'warning');
    })
    .finally(function () {
        if (btn) {
            btn.disabled = false;
            btn.textContent = btn.dataset.originalText || 'Save';
        }
    });
}

function showDrawerStatus(message, level) {
    const status = document.getElementById('drawerStatus');
    if (!status) return;

    status.className = 'alert py-2 px-3 mt-3 mb-0';
    status.classList.add('alert-' + (level || 'info'));
    status.textContent = message;
}
