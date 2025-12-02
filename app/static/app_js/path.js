document.addEventListener("DOMContentLoaded", () => {
    console.log("Sacred Path: Daily Cultivation Grid Active");

    const grid = document.getElementById("contribution-grid");
    if (!grid) return;

    const today = new Date();
    const contributions = {}; // Will be filled from API later

    // Dummy data for now (replace with real API call later)
    for (let i = 0; i < 364; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const key = date.toISOString().split('T')[0];
        contributions[key] = Math.floor(Math.random() * 5);
    }

    // === CLEAR GRID + WRAP IN A PROPER LAYOUT ===
    grid.innerHTML = ''; // safety
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(52, 10px)'; // ~52 weeks
    grid.style.gridAutoRows = '10px';
    grid.style.gap = '3px';

    // Create a wrapper that includes both labels + grid
    const wrapper = document.createElement('div');
    wrapper.className = 'contribution-wrapper';
    wrapper.style.display = 'grid';
    wrapper.style.gridTemplateColumns = 'auto 1fr'; // labels column + grid
    wrapper.style.gap = '0 12px';
    wrapper.style.alignItems = 'center';

    // Day labels column (Mon, Wed, Fri only — 7 rows, we use rows 1,3,5)
    const labelsCol = document.createElement('div');
    labelsCol.style.display = 'grid';
    labelsCol.style.gridTemplateRows = 'repeat(7, 1fr)';
    labelsCol.style.fontSize = '0.65rem';
    labelsCol.style.opacity = '0.7';
    labelsCol.style.textAlign = 'right';
    labelsCol.style.height = 'fit-content';
    labelsCol.style.alignSelf = 'center';

    const dayLabels = ['', 'Mon', '', 'Wed', '', 'Fri', '']; // 7 rows, only 1,3,5 have text
    dayLabels.forEach(label => {
        const span = document.createElement('span');
        span.textContent = label;
        labelsCol.appendChild(span);
    });

    // Generate the actual contribution squares
    for (let i = 363; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const key = date.toISOString().split('T')[0];
        const level = contributions[key] || 0;

        const day = document.createElement("div");
        day.className = `contribution-day level-${level}`;
        day.dataset.date = key;
        day.title = `${level} completion${level !== 1 ? 's' : ''} on ${date.toLocaleDateString()}`;

        // Tooltip logic (unchanged)
        day.addEventListener("mouseenter", (e) => {
            let tooltip = document.querySelector(".tooltip");
            if (!tooltip) {
                tooltip = document.createElement("div");
                tooltip.className = "tooltip";
                document.body.appendChild(tooltip);
            }
            tooltip.textContent = `${level} completion${level !== 1 ? 's' : ''} • ${date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}`;
            tooltip.classList.add("visible");

            const rect = day.getBoundingClientRect();
            tooltip.style.top = (rect.top - 40 + window.scrollY) + "px";
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + window.scrollX) + "px";
        });

        day.addEventListener("mouseleave", () => {
            const tooltip = document.querySelector(".tooltip");
            if (tooltip) tooltip.classList.remove("visible");
        });

        grid.appendChild(day);
    }

    // === FINAL ASSEMBLY ===
    wrapper.appendChild(labelsCol);
    wrapper.appendChild(grid);
    grid.parentNode.replaceChild(wrapper, grid); // swap in the new wrapper

    console.log("Sacred Path grid rendered with proper day labels inside container");
});