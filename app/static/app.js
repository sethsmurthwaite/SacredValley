// static/app.js
// Global dashboard script — theme toggle + shared logic

document.addEventListener('DOMContentLoaded', () => {
    console.log('Sacred Valley dashboard loaded');

    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');
    const html = document.documentElement;

    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcons(savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = html.getAttribute('data-theme');
        const newTheme = current === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcons(newTheme);

        // Subtle bounce
        themeToggle.style.transform = 'scale(0.9)';
        setTimeout(() => themeToggle.style.transform = '', 150);
    });

    function updateThemeIcons(theme) {
        if (theme === 'dark') {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        } else {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }
    }


    // === Populate user info globally (used by habits.js, etc.) ===
    const usernameEl = document.getElementById('username');
    const realmEl = document.getElementById('realm');
    const progressEl = document.getElementById('progress');
    const progressFill = document.getElementById('progress-fill');

    if (usernameEl && user?.username) {
        usernameEl.textContent = user.username;
    }
    if (realmEl && user?.current_realm) {
        realmEl.textContent = user.current_realm;
    }
    if (progressEl && user?.progress_to_next != null) {
        const progress = Math.round(user.progress_to_next);
        progressEl.textContent = progress;
        progressFill.style.width = progress + '%';
    }
});