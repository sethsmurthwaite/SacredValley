// static/app_js/habits.js
// SACRED VALLEY — FINAL, WORKING, NO MORE DISAPPEARING HABITS

async function updateProgressBar() {
    try {
        const resp = await fetch("/api/user/progress");
        if (!resp.ok) return;
        const p = await resp.json();

        const realmEl = document.getElementById("realm");
        const progressEl = document.getElementById("progress");
        const requiredEl = document.getElementById("required_progress");
        const fill = document.getElementById("progress-fill");

        if (!realmEl || !progressEl || !requiredEl || !fill) return;

        realmEl.textContent = `${p.current_realm} → ${p.next_realm}`;
        progressEl.textContent = Number(p.progress_in_level).toLocaleString();
        requiredEl.textContent = Number(p.progress_in_level + p.needed_for_next).toLocaleString();
        fill.style.width = `${Math.min(100, p.percent_to_next)}%`;

        document.querySelector(".progress-bar").title =
            `${Number(p.progress_in_level).toLocaleString()} / ${Number(p.progress_in_level + p.needed_for_next).toLocaleString()} madra`;

        // Madra gain animation
        if (window.lastProgress !== undefined && p.total_progress > window.lastProgress) {
            const gain = p.total_progress - window.lastProgress;
            const notif = document.createElement("div");
            notif.className = "madra-gain";
            notif.textContent = `+${gain} madra!`;
            document.body.appendChild(notif);
            setTimeout(() => notif.remove(), 2200);
        }
        window.lastProgress = p.total_progress;

    } catch (err) {
        console.error("Progress update failed:", err);
    }
}

class HabitsManager {
    constructor() {
        this.modal = document.getElementById('habit-modal');
        this.addBtn = document.getElementById('add-habit-btn');
        this.cancelBtn = document.getElementById('cancel-modal');
        this.form = document.getElementById('habit-form');
        this.freqSelect = document.getElementById('frequency');
        this.repeatDiv = document.getElementById('repeat-days');
        this.container = document.getElementById('habit-list-container');

        if (!this.container) return;

        this.init();
    }

    init() {
        this.setupModal();
        this.setupFrequencyToggle();
        this.setupFormSubmit();
        this.renderHabits();           // ← This now works
        updateProgressBar();           // Initial load
        console.log("Sacred Valley: Habits tab LIVE & CORRECT");
    }

    setupModal() {
        this.addBtn.onclick = () => this.modal.classList.add('active');
        this.cancelBtn.onclick = () => this.modal.classList.remove('active');
        window.addEventListener('click', e => e.target === this.modal && this.modal.classList.remove('active'));
    }

    setupFrequencyToggle() {
        this.freqSelect.addEventListener('change', () => {
            this.repeatDiv.style.display = this.freqSelect.value === 'weekly' ? 'block' : 'none';
        });
    }

    setupFormSubmit() {
        this.form.onsubmit = async e => {
            e.preventDefault();
            const data = new FormData(this.form);
            if (data.get('frequency') === 'weekly') {
                const days = Array.from(this.form.querySelectorAll('input[name="days"]:checked'))
                    .reduce((acc, cb) => acc + parseInt(cb.value), 0);
                data.set('repeat_days', days || 1);
            }

            const resp = await fetch('/habits', { method: 'POST', body: data });
            if (resp.ok || resp.redirected) {
                this.modal.classList.remove('active');
                location.reload(); // fine for now — or later replace with live refresh
            } else {
                alert("Failed to create habit");
            }
        };
    }

    renderHabits() {
        // ← THIS IS THE ONLY CHANGE YOU NEED: use global `habits`, not `window.habits`
        if (!habits || habits.length === 0) {
            this.container.innerHTML = '<p class="empty-state">No habits yet. Click ＋ to begin your cultivation.</p>';
            updateProgressBar();
            return;
        }

        const todayStr = new Date().toISOString().split('T')[0];
        const formatRepeatDays = (days, freq) => {
            if (freq !== 'weekly') return "Every day";
            const names = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
            return names.filter((_, i) => days & (1 << i)).join(', ') || "No days";
        };

        const html = habits.map(h => `
            <div class="habit-card" data-id="${h.id}">
                <div class="habit-summary">
                    <input type="checkbox" class="complete-checkbox" ${h.last_completion === todayStr ? 'checked disabled' : ''}>
                    <div class="habit-main">
                        <h3>${h.name}</h3>
                        <div class="habit-meta">
                            <span class="tag">${h.frequency}</span>
                            <span class="progress-gain">+${h.progress_value}</span>
                            <span class="streak">🔥 ${h.streak_current || 0}</span>
                        </div>
                    </div>
                    <button class="expand-btn">▼</button>
                </div>
                <div class="habit-detail hidden">
                    <div class="detail-grid">
                        <div><strong>Description</strong><p>${h.description || "None"}</p></div>
                        <div>
                            <strong>Repeats</strong>
                            <p>
                                ${h.frequency === 'daily'
                            ? 'Daily'
                            : formatRepeatDays(h.repeat_days || 0, h.frequency)}
                            </p>
                        </div>

                        <div><strong>Current Streak</strong><p>${h.streak_current || 0} day${h.streak_current !== 1 ? 's' : ''} 🔥</p></div>
                        <div><strong>Best Streak</strong><p>${h.streak_max || 0} day${h.streak_max !== 1 ? 's' : ''} 🏆</p></div>
                        
                    </div>
                </div>
            </div>
        `).join('');

        this.container.innerHTML = `<div class="habit-list">${html}</div>`;
        this.setupHabitCompletion();
        this.setupExpandCollapse();
        updateProgressBar(); // ← always refresh progress bar after render
    }

    setupHabitCompletion() {
        // Remove old listeners
        document.querySelectorAll('.complete-checkbox').forEach(cb => {
            const newCb = cb.cloneNode(true);
            cb.parentNode.replaceChild(newCb, cb);
        });

        document.querySelectorAll('.complete-checkbox:not(:disabled)').forEach(cb => {
            cb.addEventListener('change', async () => {
                if (!cb.checked) return;
                cb.disabled = true;
                const habitId = cb.closest('.habit-card').dataset.id;

                try {
                    const resp = await fetch(`/habits/${habitId}/complete`, { method: 'POST' });
                    if (resp.ok || resp.redirected) {
                        location.reload(); // ← temporary — works perfectly for now
                        // Later you can replace with: await fetch habits data + this.renderHabits()
                    } else {
                        alert("Failed");
                        cb.checked = false;
                    }
                } catch (err) {
                    alert("Network error");
                    cb.checked = false;
                } finally {
                    cb.disabled = false;
                }
            });
        });
    }

    setupExpandCollapse() {
        document.querySelectorAll('.habit-summary').forEach(summary => {
            summary.addEventListener('click', e => {
                if (e.target.closest('.complete-checkbox') || e.target.closest('.expand-btn')) return;
                const detail = summary.nextElementSibling;
                const btn = summary.querySelector('.expand-btn');
                detail.classList.toggle('hidden');
                btn.textContent = detail.classList.contains('hidden') ? '▼' : '▲';
            });
        });

        document.querySelectorAll('.expand-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const detail = btn.closest('.habit-summary').nextElementSibling;
                detail.classList.toggle('hidden');
                btn.textContent = detail.classList.contains('hidden') ? '▼' : '▲';
            });
        });
    }
}

// Start it
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('habit-list-container')) {
        new HabitsManager();
    }
});