// static/app_js/habits.js
// All JavaScript for the Habits tab — clean, modular, and auto-initializing

class HabitsManager {
    constructor() {
        this.modal = document.getElementById('habit-modal');
        this.addBtn = document.getElementById('add-habit-btn');
        this.cancelBtn = document.getElementById('cancel-modal');
        this.form = document.getElementById('habit-form');
        this.freqSelect = document.getElementById('frequency');
        this.repeatDiv = document.getElementById('repeat-days');
        this.container = document.getElementById('habit-list-container');

        if (!this.modal || !this.addBtn) {
            console.warn("Habits tab not fully loaded yet. Will retry...");
            return;
        }

        this.init();
    }

    init() {
        this.setupModal();
        this.setupFrequencyToggle();
        this.setupFormSubmit();
        this.renderHabits();
        this.setupHabitCompletion();
        this.setupExpandCollapse();

        console.log("Sacred Valley: Habits tab initialized 🚀");
    }

    setupModal() {
        this.addBtn.onclick = () => this.modal.classList.add('active');
        this.cancelBtn.onclick = () => this.modal.classList.remove('active');
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) this.modal.classList.remove('active');
        });
    }

    setupFrequencyToggle() {
        this.freqSelect.addEventListener('change', () => {
            this.repeatDiv.style.display = this.freqSelect.value === 'weekly' ? 'block' : 'none';
        });
    }

    setupFormSubmit() {
        this.form.onsubmit = async (e) => {
            e.preventDefault();
            const data = new FormData(this.form);

            // Handle repeat_days properly
            if (data.get('frequency') === 'weekly') {
                const days = Array.from(this.form.querySelectorAll('input[name="days"]:checked'))
                    .reduce((sum, cb) => sum + parseInt(cb.value), 0);
                data.set('repeat_days', days || 1);
            }
            // else: hidden input already has 127

            try {
                const resp = await fetch('/habits', {
                    method: 'POST',
                    body: data
                });

                if (resp.ok || resp.redirected) {
                    this.modal.classList.remove('active');
                    location.reload();
                } else {
                    const text = await resp.text();
                    alert("Failed to create habit. Check console.");
                    console.error("Habit creation failed:", text);
                }
            } catch (err) {
                alert("Network error");
                console.error(err);
            }
        };
    }

    renderHabits() {
        if (!habits || habits.length === 0) {
            this.container.innerHTML = '<p class="empty-state">No habits yet. Click ＋ to begin your cultivation.</p>';
            return;
        }

        const formatRepeatDays = (days, freq) => {
            if (freq !== 'weekly') return "Every day";
            const names = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
            const selected = names.filter((_, i) => days & (1 << i));
            return selected.length === 7 ? "Every day" : selected.join(', ');
        };

        const todayStr = new Date().toISOString().split('T')[0];

        const html = habits.map(h => `
            <div class="habit-card" data-id="${h.id}">
                <div class="habit-summary">
                    <input type="checkbox" class="complete-checkbox" ${h.last_completion === todayStr ? 'checked disabled' : ''}>
                    <div class="habit-main">
                        <h3>${h.name}</h3>
                        <div class="habit-meta">
                            <span class="tag">${h.frequency}</span>
                            <span class="progress-gain">+${h.progress_value}%</span>
                            <span class="streak">Streak ${h.streak_current}</span>
                        </div>
                    </div>
                    <button class="expand-btn">▼</button>
                </div>
                <div class="habit-detail hidden">
                    <div class="detail-grid">
                        <div><strong>Description</strong><p>${h.description || "No description"}</p></div>
                        <div><strong>Frequency</strong><p>${h.frequency.charAt(0).toUpperCase() + h.frequency.slice(1)}</p></div>
                        <div><strong>Created</strong><p>${new Date(h.created_at).toLocaleDateString()}</p></div>
                        <div><strong>Repeat Days</strong><p>${formatRepeatDays(h.repeat_days || 127, h.frequency)}</p></div>
                        <div><strong>Progress Value</strong><p>+${h.progress_value}% per completion</p></div>
                    </div>
                </div>
            </div>
        `).join('');

        this.container.innerHTML = `<div class="habit-list">${html}</div>`;
    }

    setupHabitCompletion() {
        document.querySelectorAll('.complete-checkbox:not(:disabled)').forEach(cb => {
            cb.addEventListener('change', async () => {
                if (cb.checked) {
                    const habitId = cb.closest('.habit-card').dataset.id;
                    await fetch(`/habits/${habitId}/complete`, { method: 'POST' });
                    location.reload();
                }
            });
        });
    }

    setupExpandCollapse() {
        document.querySelectorAll('.habit-summary').forEach(summary => {
            summary.addEventListener('click', (e) => {
                if (e.target.closest('.complete-checkbox') || e.target.closest('.expand-btn')) return;
                const detail = summary.nextElementSibling;
                const btn = summary.querySelector('.expand-btn');
                detail.classList.toggle('hidden');
                btn.textContent = detail.classList.contains('hidden') ? '▼' : '▲';
            });
        });

        // Expand button specifically
        document.querySelectorAll('.expand-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const detail = btn.closest('.habit-summary').nextElementSibling;
                detail.classList.toggle('hidden');
                btn.textContent = detail.classList.contains('hidden') ? '▼' : '▲';
            });
        });
    }
}

// Auto-initialize when script loads (works with HTMX, tabs, etc.)
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('habit-list-container')) {
        new HabitsManager();
    }
});

// Re-init if content swapped (HTMX, AJAX tabs, etc.)
document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.detail.target.id === 'habit-list-container' || e.detail.target.querySelector('#habit-list-container')) {
        new HabitsManager();
    }
});