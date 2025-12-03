document.addEventListener("DOMContentLoaded", () => {
    if (typeof Chart === 'undefined') {
        console.error("Chart.js not loaded! Make sure CDN is in <head>");
        alert("Error: Chart.js failed to load. Check console.");
        return;
    }

    console.log("Sacred Path Analytics: Initializing... 🌌");

    const gridContainer = document.getElementById("contribution-grid");
    const lineCtx = document.getElementById("line-chart");
    const barCtx = document.getElementById("bar-chart");
    const rangeButtons = document.querySelectorAll(".range-btn");

    if (!gridContainer || !lineCtx || !barCtx) {
        console.error("Missing required elements!");
        return;
    }

    let currentRange = "week";
    let lineChart = null;
    let barChart = null;

    const generateData = (range) => {
        const today = new Date();
        let days = range === "week" ? 7 : range === "month" ? 30 : 365;

        const contributions = {};
        const dailyMadra = [];
        const completionsByDay = { Sun: 0, Mon: 0, Tue: 0, Wed: 0, Thu: 0, Fri: 0, Sat: 0 };
        let totalMadra = 0;
        let totalCompletions = 0;
        let currentStreak = 0;
        let longestStreak = 0;
        let streak = 0;

        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const key = date.toISOString().split('T')[0];
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });

            const completions = i === 0 ? 0 : Math.floor(Math.random() * 6);
            const madra = completions * (12 + Math.random() * 10);

            contributions[key] = completions;
            dailyMadra.push({ date: key, madra: Math.round(madra) });
            completionsByDay[dayName] += completions;

            totalMadra += madra;
            totalCompletions += completions;

            if (completions > 0) {
                streak++;
                longestStreak = Math.max(longestStreak, streak);
            } else if (i < days - 1) {
                streak = 0;
            }
        }
        currentStreak = streak;

        return { contributions, dailyMadra, completionsByDay, stats: { totalMadra, totalCompletions, currentStreak, longestStreak } };
    };

    const renderHeatmap = (contributions) => {
        const today = new Date();
        gridContainer.innerHTML = '';
        const isYear = currentRange === "year";
        gridContainer.style.gridTemplateColumns = isYear ? 'repeat(52, 10px)' : 'repeat(7, 10px)';
        gridContainer.style.gap = '3px';

        const wrapper = document.createElement('div');
        wrapper.style.display = 'grid';
        wrapper.style.gridTemplateColumns = isYear ? 'auto 1fr' : '1fr';
        wrapper.style.gap = '0 12px';
        wrapper.style.alignItems = 'center';

        if (isYear) {
            const labels = document.createElement('div');
            labels.style.display = 'grid';
            labels.style.gridTemplateRows = 'repeat(7, 1fr)';
            labels.style.fontSize = '0.65rem';
            labels.style.opacity = '0.7';
            labels.style.textAlign = 'right';
            ['','Mon','','Wed','','Fri',''].forEach(t => {
                const s = document.createElement('span'); s.textContent = t; labels.appendChild(s);
            });
            wrapper.appendChild(labels);
        }

        const daysCount = isYear ? 364 : currentRange === "month" ? 29 : 6;
        for (let i = daysCount; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const key = date.toISOString().split('T')[0];
            const level = contributions[key] || 0;

            const day = document.createElement("div");
            day.className = "contribution-day";
            day.dataset.level = level;
            day.dataset.date = key;

            day.addEventListener("mouseenter", () => {
                let tooltip = document.querySelector(".tooltip") || (() => {
                    const t = document.createElement("div"); t.className = "tooltip"; document.body.appendChild(t); return t;
                })();
                tooltip.textContent = `${level} completion${level !== 1 ? 's' : ''} on ${date.toLocaleDateString()}`;
                tooltip.classList.add("visible");
                const rect = day.getBoundingClientRect();
                tooltip.style.top = (rect.top - 40 + window.scrollY) + "px";
                tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + window.scrollX) + "px";
            });
            day.addEventListener("mouseleave", () => document.querySelector(".tooltip")?.classList.remove("visible"));

            gridContainer.appendChild(day);
        }

        wrapper.appendChild(gridContainer);
        gridContainer.replaceWith(wrapper);
    };

    const renderCharts = (data) => {
        const { dailyMadra, completionsByDay, stats } = data;

        if (lineChart) lineChart.destroy();
        lineChart = new Chart(lineCtx, {
            type: 'line',
            data: { labels: dailyMadra.map(d => new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
                datasets: [{ label: 'Madra', data: dailyMadra.map(d => d.madra), borderColor: '#50fa7b', backgroundColor: 'rgba(80,250,123,0.2)', tension: 0.4, fill: true, pointBackgroundColor: '#50fa7b', pointRadius: 5 }]
            },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
        });

        if (barChart) barChart.destroy();
        barChart = new Chart(barCtx, {
            type: 'bar',
            data: { labels: Object.keys(completionsByDay), datasets: [{ data: Object.values(completionsByDay), backgroundColor: '#4169e1', borderRadius: 8 }] },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
        });

        document.getElementById("total-madra").textContent = Math.round(stats.totalMadra).toLocaleString();
        document.getElementById("longest-streak").textContent = stats.longestStreak + " days";
        document.getElementById("current-streak").textContent = stats.currentStreak + " days";
        document.getElementById("total-completions").textContent = stats.totalCompletions.toLocaleString();
    };

    const updateAll = () => {
        const data = generateData(currentRange);
        renderHeatmap(data.contributions);
        renderCharts(data);
        const last = Object.keys(data.contributions).reverse().find(d => data.contributions[d] > 0);
        const daysAgo = last ? Math.floor((Date.now() - new Date(last)) / 86400000) : 999;
        document.querySelector(".heatmap-footer small").textContent =
            daysAgo === 0 ? "Today" : daysAgo === 1 ? "Yesterday" : `${daysAgo} days ago`;
    };

    rangeButtons.forEach(btn => btn.addEventListener("click", () => {
        rangeButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentRange = btn.dataset.range;
        updateAll();
    }));

    updateAll();
    console.log("Sacred Path Analytics: Fully Activated! 🔥🌀");
});