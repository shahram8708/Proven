/* ========================================
   Proven — Evidence Form (Multi-step)
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {
    // Match template IDs/classes from evidence/new.html
    const form = document.getElementById('evidenceForm');
    if (!form) return;

    const steps = document.querySelectorAll('.evidence-step');
    const stepDots = document.querySelectorAll('.step-indicator');
    const stepLines = document.querySelectorAll('.step-line');
    const prevBtn = document.getElementById('prevStep');
    const nextBtn = document.getElementById('nextStep');
    const submitBtn = document.getElementById('submitEvidence');
    let currentStep = 0;

    function showStep(index) {
        steps.forEach(function (step, i) {
            step.style.display = i === index ? 'block' : 'none';
        });

        // Update step indicators
        stepDots.forEach(function (dot, i) {
            dot.classList.remove('active', 'completed');
            if (i < index) dot.classList.add('completed');
            else if (i === index) dot.classList.add('active');
        });
        stepLines.forEach(function (line, i) {
            line.classList.toggle('completed', i < index);
        });

        // Button visibility
        if (prevBtn) prevBtn.style.display = index === 0 ? 'none' : 'inline-block';
        if (nextBtn) nextBtn.style.display = index === steps.length - 1 ? 'none' : 'inline-block';
        if (submitBtn) submitBtn.style.display = index === steps.length - 1 ? 'inline-block' : 'none';

        currentStep = index;
        updateTips(index);
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            if (currentStep < steps.length - 1) {
                showStep(currentStep + 1);
                autoSaveDraft();
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            if (currentStep > 0) {
                showStep(currentStep - 1);
            }
        });
    }

    showStep(0);

    // --- Auto-save Draft ---
    let autoSaveTimer = null;
    const autoSaveIndicator = document.getElementById('autosaveStatus');

    function autoSaveDraft() {
        if (autoSaveTimer) clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(function () {
            const formData = new FormData(form);
            formData.append('auto_save', 'true');

            fetch(form.dataset.saveDraftUrl || '/evidence/save-draft', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                },
                credentials: 'same-origin'
            }).then(function (res) {
                if (res.ok && autoSaveIndicator) {
                    autoSaveIndicator.textContent = 'Draft saved';
                    autoSaveIndicator.classList.remove('d-none');
                    setTimeout(function () {
                        autoSaveIndicator.classList.add('d-none');
                    }, 3000);
                }
            }).catch(function () {
                // Silent fail on auto-save
            });
        }, 2000);
    }

    // Auto-save on input changes
    form.querySelectorAll('input, textarea, select').forEach(function (el) {
        el.addEventListener('change', autoSaveDraft);
    });

    // --- Step Tips ---
    const tips = {
        0: 'Choose the evidence type that best represents what you want to showcase.',
        1: 'A clear title and summary help verifiers and employers understand your work.',
        2: 'Describe the specific situation and challenge you faced.',
        3: 'Detail what you actually did — be specific about your actions.',
        4: 'Quantify your results wherever possible. Numbers make evidence compelling.',
        5: 'Supporting files add credibility. Redact any confidential information.'
    };

    function updateTips(stepIndex) {
        const tipsEl = document.getElementById('step-tips');
        if (tipsEl && tips[stepIndex]) {
            tipsEl.textContent = tips[stepIndex];
        }
    }

    // --- Character counters (live)
    document.querySelectorAll('.char-count').forEach(function (counter) {
        const targetId = counter.dataset.target;
        const field = document.getElementById(targetId) || form.querySelector('[name="' + targetId + '"]');
        if (!field) return;

        const syncCount = function () {
            counter.textContent = field.value.length.toString();
        };

        field.addEventListener('input', syncCount);
        syncCount();
    });

    // --- Character Counters ---
    form.querySelectorAll('[data-maxlength]').forEach(function (field) {
        const max = parseInt(field.dataset.maxlength);
        const counterId = field.id + '-counter';
        let counter = document.getElementById(counterId);
        if (!counter) {
            counter = document.createElement('small');
            counter.id = counterId;
            counter.classList.add('text-muted');
            field.parentNode.appendChild(counter);
        }
        function update() {
            const remaining = max - field.value.length;
            counter.textContent = remaining + '/' + max + ' characters';
            counter.classList.toggle('text-danger', remaining < 50);
        }
        field.addEventListener('input', update);
        update();
    });

    // --- File Upload Preview ---
    const fileInput = document.getElementById('evidence_files');
    const fileList = document.getElementById('file-list');
    if (fileInput && fileList) {
        fileInput.addEventListener('change', function () {
            fileList.innerHTML = '';
            Array.from(this.files).forEach(function (file) {
                const item = document.createElement('div');
                item.classList.add('d-flex', 'align-items-center', 'gap-2', 'mb-1', 'small');
                item.innerHTML = '<i class="fas fa-file text-muted"></i> ' +
                    '<span>' + file.name + '</span>' +
                    '<span class="text-muted">(' + (file.size / 1024).toFixed(1) + ' KB)</span>';
                fileList.appendChild(item);
            });
        });
    }
});
