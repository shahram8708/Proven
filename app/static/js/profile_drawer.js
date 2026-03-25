/* ========================================
   Proven — Profile Drawer (Discover)
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {
    const drawer = document.getElementById('profile-drawer');
    const backdrop = document.getElementById('profile-drawer-backdrop');
    if (!drawer) return;

    const drawerBody = drawer.querySelector('.profile-drawer-body');
    const drawerHeader = drawer.querySelector('.profile-drawer-header');

    // --- Open Drawer ---
    function openDrawer(userId) {
        drawer.classList.add('active');
        if (backdrop) backdrop.classList.add('active');
        document.body.style.overflow = 'hidden';

        if (drawerBody) {
            drawerBody.innerHTML = '<div class="drawer-loading"><i class="fas fa-spinner fa-spin me-2"></i> Loading profile...</div>';
        }

        fetch('/discover/preview/' + userId, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (drawerHeader) {
                drawerHeader.innerHTML =
                    '<button class="profile-drawer-close" aria-label="Close">&times;</button>' +
                    '<div class="d-flex align-items-center gap-3">' +
                        '<div class="avatar-circle avatar-circle-lg">' + (data.initials || '?') + '</div>' +
                        '<div>' +
                            '<h5 class="mb-0" style="color:white">' + (data.name || 'Unknown') + '</h5>' +
                            '<p class="mb-0" style="color:rgba(255,255,255,0.7)">' + (data.title || '') + '</p>' +
                        '</div>' +
                    '</div>';

                drawerHeader.querySelector('.profile-drawer-close').addEventListener('click', closeDrawer);
            }

            if (drawerBody) {
                let html = '';

                // Stats
                html += '<div class="d-flex gap-4 mb-3">';
                html += '<div><strong>' + (data.evidence_count || 0) + '</strong> <small class="text-muted">Evidence</small></div>';
                html += '<div><strong>' + (data.verified_count || 0) + '</strong> <small class="text-muted">Verified</small></div>';
                html += '<div><strong>' + (data.skills_count || 0) + '</strong> <small class="text-muted">Skills</small></div>';
                html += '</div>';

                // Bio
                if (data.bio) {
                    html += '<p class="small text-muted">' + data.bio + '</p>';
                }

                // Skills
                if (data.top_skills && data.top_skills.length > 0) {
                    html += '<h6 class="mt-3 mb-2">Top Skills</h6><div class="d-flex flex-wrap gap-1">';
                    data.top_skills.forEach(function (skill) {
                        html += '<span class="skill-tag">' + skill + '</span>';
                    });
                    html += '</div>';
                }

                // Radar chart placeholder
                if (data.radar_data) {
                    html += '<div class="mt-3"><canvas id="drawer-radar" width="250" height="250"></canvas></div>';
                }

                drawerBody.innerHTML = html;

                // Init radar chart if data
                if (data.radar_data && typeof initRadarChart === 'function') {
                    initRadarChart('drawer-radar', data.radar_data);
                }
            }

            // Footer actions
            const footer = drawer.querySelector('.profile-drawer-footer');
            if (footer) {
                footer.innerHTML =
                    '<a href="/profile/' + userId + '" class="btn btn-proven-primary flex-fill">View Full Profile</a>' +
                    '<button class="btn btn-proven-amber flex-fill" onclick="requestContact(' + userId + ')">Request Contact</button>';
            }
        })
        .catch(function () {
            if (drawerBody) {
                drawerBody.innerHTML = '<div class="text-center text-muted py-4">Failed to load profile</div>';
            }
        });
    }

    // --- Close Drawer ---
    function closeDrawer() {
        drawer.classList.remove('active');
        if (backdrop) backdrop.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (backdrop) backdrop.addEventListener('click', closeDrawer);

    // ESC key close
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeDrawer();
    });

    // --- Delegate Click on Talent Cards ---
    document.addEventListener('click', function (e) {
        const card = e.target.closest('[data-user-id]');
        if (card) {
            e.preventDefault();
            openDrawer(card.dataset.userId);
        }
    });

    // Expose for external use
    window.openProfileDrawer = openDrawer;
    window.closeProfileDrawer = closeDrawer;
});

// --- Contact Request ---
function requestContact(userId) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    fetch('/discover/contact/' + userId, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (data.success) {
            alert('Contact request sent! The talent will be notified.');
        } else {
            alert(data.message || 'Unable to send contact request.');
        }
    })
    .catch(function () {
        alert('Something went wrong. Please try again.');
    });
}
