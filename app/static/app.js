document.addEventListener('DOMContentLoaded', () => {
    // Populate user info
    document.getElementById('username').textContent = user.username;
    document.getElementById('realm').textContent = user.current_realm;
    document.getElementById('progress').textContent = user.progress_to_next;
    document.getElementById('progress-fill').style.width = user.progress_to_next + '%';

    const container = document.getElementById('habit-list-container');

    if (!habits || habits.length === 0) {
        container.innerHTML = '<p class="empty-state">No habits yet. Click ＋ to begin your cultivation.</p>';
        return;
    }

    const formatRepeatDays = (days, frequency) => {
        if (frequency !== 'weekly') return "Every day";
        const names = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
        const selected = [];
        for (let i = 0; i < 7; i++) {
            if (days & (1 << i)) selected.push(names[i]);
        }
        return selected.length === 7 ? "Every day" : selected.join(', ');
    };

    const habitHTML = habits.map(h => `
        <div class="habit-card" data-id="${h.id}">
            <div class="habit-summary">
                <input type="checkbox" class="complete-checkbox" ${h.last_completion === today ? 'checked disabled' : ''}>
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
                    <div><strong>Created</strong><p>${new Date(h.created_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p></div>
                    <div><strong>Repeat Days</strong><p>${formatRepeatDays(h.repeat_days || 127, h.frequency)}</p></div>
                    <div><strong>Progress Value</strong><p>+${h.progress_value}% per completion</p></div>
                </div>
            </div>
        </div>
    `).join('');

    container.innerHTML = `<div class="habit-list">${habitHTML}</div>`;

    // Expand/collapse
    document.querySelectorAll('.habit-summary').forEach(s => {
        s.addEventListener('click', e => {
            if (e.target.closest('.complete-checkbox')) return;
            const detail = s.nextElementSibling;
            const btn = s.querySelector('.expand-btn');
            detail.classList.toggle('hidden');
            btn.textContent = detail.classList.contains('hidden') ? '▼' : '▲';
        });
    });

    // Complete habit
    document.querySelectorAll('.complete-checkbox:not(:disabled)').forEach(cb => {
        cb.addEventListener('change', async () => {
            if (cb.checked) {
                const habitId = cb.closest('.habit-card').dataset.id;
                await fetch(`/habits/${habitId}/complete`, { method: 'POST' });
                location.reload();
            }
        });
    });

    // Modal logic (unchanged)
    const modal = document.getElementById('habit-modal');
    const addBtn = document.getElementById('add-habit-btn');
    const cancelBtn = document.getElementById('cancel-modal');
    const form = document.getElementById('habit-form');
    const freqSelect = document.getElementById('frequency');
    const repeatDiv = document.getElementById('repeat-days');

    addBtn.onclick = () => modal.classList.add('active');
    cancelBtn.onclick = () => modal.classList.remove('active');
    window.onclick = e => { if (e.target === modal) modal.classList.remove('active'); };

    freqSelect.addEventListener('change', () => {
        repeatDiv.style.display = freqSelect.value === 'weekly' ? 'block' : 'none';
    });

    form.onsubmit = async e => {
        e.preventDefault();
        const data = new FormData(form);
        const days = [...form.querySelectorAll('[name="days"]:checked')].reduce((a,c) => a + parseInt(c.value), 0);
        if (data.get('frequency') === 'weekly') data.set('repeat_days', days);

        await fetch('/habits', { method: 'POST', body: data });
        location.reload();
    };
});