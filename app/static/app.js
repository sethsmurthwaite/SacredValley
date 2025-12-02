document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('habit-modal');
    const addBtn = document.getElementById('add-habit-btn');
    const cancelBtn = document.getElementById('cancel-modal');
    const form = document.getElementById('habit-form');
    const freqSelect = document.querySelector('[name="frequency"]');
    const repeatDiv = document.getElementById('repeat-days');

    // Tab switching
    document.querySelectorAll('.tab').forEach(t => {
        t.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
            t.classList.add('active');
            document.getElementById(t.dataset.tab).classList.add('active');
        });
    });

    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const isDark = document.documentElement.dataset.theme === 'dark';
        document.documentElement.dataset.theme = isDark ? 'light' : 'dark';
    });

    // Modal
    addBtn.onclick = () => modal.classList.add('active');
    cancelBtn.onclick = () => modal.classList.remove('active');
    window.onclick = e => { if (e.target === modal) modal.classList.remove('active'); };

    // Show repeat days only for weekly
    freqSelect.addEventListener('change', () => {
        repeatDiv.style.display = freqSelect.value === 'weekly' ? 'block' : 'none';
    });

    // Submit new habit
    form.onsubmit = async e => {
        e.preventDefault();
        const data = new FormData(form);
        const days = [...document.querySelectorAll('[name="days"]:checked')].reduce((a,c) => a + parseInt(c.value), 0);
        if (data.get('frequency') === 'weekly') data.set('repeat_days', days);

        await fetch('/habits', { method: 'POST', body: data });
        location.reload();
    };

    // Checkbox completion
    document.querySelectorAll('.complete-checkbox:not(:disabled)').forEach(cb => {
        cb.addEventListener('change', async () => {
            if (cb.checked) {
                const habitId = cb.closest('.habit-item').dataset.id;
                await fetch(`/habits/${habitId}/complete`, { method: 'POST' });
                location.reload();
            }
        });
    });
});