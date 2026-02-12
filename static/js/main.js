class F1App {
    constructor() {
        this.currentView = 'races';
        this.currentSeason = 2026;
        this.races = [];
        this.drivers = [];
        this.constructors = [];
        this.charts = {};

        // Expose for inline handlers
        window.app = this;

        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadView('races');
        this.initMasonry(); // Just keeps resizing logic separation
        await this.updateHero();

        // Refresh every minute for countdown
        setInterval(() => this.updateCountdown(), 60000);
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.switchView(view);

                // Update active class
                document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Season Select
        const seasonSelect = document.getElementById('season-select');
        seasonSelect.addEventListener('change', (e) => {
            this.currentSeason = e.target.value;
            this.loadView(this.currentView);
        });

        // Modal Close
        document.querySelector('.close-modal').addEventListener('click', () => {
            document.getElementById('race-modal').style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target == document.getElementById('race-modal')) {
                document.getElementById('race-modal').style.display = 'none';
            }
        });

        // Window Resize for Masonry
        window.addEventListener('resize', this.debounce(() => this.resizeAllMasonryItems(), 200));
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    switchView(view) {
        this.currentView = view;
        document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
        document.getElementById(`${view}-view`).style.display = 'block';

        this.loadView(view);
    }

    async loadView(view) {
        if (view === 'races') {
            await this.loadRaces();
        } else if (view === 'drivers') {
            await this.loadDriverStandings();
        } else if (view === 'constructors') {
            await this.loadConstructorStandings();
        }
    }

    getTeamClass(teamName) {
        if (!teamName) return '';
        // Normalize: "Red Bull" -> "Red_Bull", "Aston Martin" -> "Aston_Martin"
        const safeName = teamName.replace(/ /g, '_');
        // Handle "RB" vs "Red Bull" carefully if needed, or just rely on CSS
        // Our CSS has .team-border-Red_Bull, .team-border-McLaren etc.
        return `team-border-${safeName}`;
    }

    async loadRaces() {
        const container = document.getElementById('races-list');
        container.innerHTML = '<div class="loading">Loading races...</div>';

        try {
            const response = await fetch(`/api/races?season=${this.currentSeason}`);
            this.races = await response.json();

            container.innerHTML = '';

            if (this.races.length === 0) {
                container.innerHTML = '<div class="no-data">No races found for this season.</div>';
                return;
            }

            this.races.forEach(race => {
                const card = document.createElement('div');
                card.className = 'race-card';
                // Apply winner team border if completed
                if (race.is_completed && race.winner_team) {
                    const teamClass = this.getTeamClass(race.winner_team);
                    if (teamClass) card.classList.add(teamClass);
                }

                card.onclick = () => this.openRaceDetails(race.id);

                // Status Logic
                let statusClass = 'status-upcoming';
                let statusText = 'Upcoming';
                if (race.is_completed) {
                    statusClass = 'status-completed';
                    statusText = 'Completed';
                }

                // Image Fallback
                const imgUrl = race.circuit_image || 'https://via.placeholder.com/400x200?text=No+Image';

                card.innerHTML = `
                    <div class="card-image-container">
                        <img src="${imgUrl}" alt="${race.circuit}" loading="lazy" onload="window.app.resizeMasonryItem(this.parentElement.parentElement)">
                        <div class="status-badge ${statusClass}">${statusText}</div>
                    </div>
                    <div class="card-content">
                        <div class="race-round">Round ${race.round}</div>
                        <h3 class="race-title">${race.name}</h3>
                        <div class="race-date">
                            <span>📅</span> ${new Date(race.date).toLocaleDateString()}
                        </div>
                         <div class="race-circuit">
                            <span>📍</span> ${race.circuit}
                        </div>
                        ${race.winner_team ? `<div class="mt-2 text-sm text-secondary">Winner: <span class="font-bold text-white">${race.winner_team}</span></div>` : ''}
                    </div>
                `;
                container.appendChild(card);
            });

            // Trigger Masonry Layout
            this.resizeAllMasonryItems();

        } catch (e) {
            console.error(e);
            container.innerHTML = '<div class="error">Failed to load races.</div>';
        }
    }

    async loadDriverStandings() {
        try {
            const response = await fetch(`/api/standings/drivers?season=${this.currentSeason}`);
            const standings = await response.json();

            // Champion Highlight Logic
            const championContainer = document.getElementById('champion-highlight-container');
            // We need to inject this container if it doesn't exist, or just use a known spot
            // I'll assume I inject it before the chart if not present

            let champEl = document.getElementById('champion-highlight');
            if (!champEl) {
                // Create it before chart
                const chartCanvas = document.getElementById('driversChart');
                if (chartCanvas && chartCanvas.parentElement) {
                    champEl = document.createElement('div');
                    champEl.id = 'champion-highlight';
                    chartCanvas.parentElement.parentElement.insertBefore(champEl, chartCanvas.parentElement);
                }
            }

            if (champEl) {
                champEl.innerHTML = ''; // Clear previous
                if (standings.length > 0) {
                    // Check if season is decisive (e.g. all 24 races done or just show leader)
                    // User said "Season Champion Highlight", implying show the winner.
                    // Even if mid-season, showing the leader as "Current Leader" or "Champion" if over.
                    // Simple logic: Show #1 as highlight.
                    const leader = standings[0];
                    // Only show specific visual if points > 0
                    if (leader.points > 0) {
                        const teamClass = this.getTeamClass(leader.constructor_name);
                        champEl.innerHTML = `
                            <div class="champion-card ${teamClass}">
                                <div class="champion-crown">👑</div>
                                <div>
                                    <h3 class="text-secondary text-sm uppercase">Season Leader</h3>
                                    <h2 class="text-3xl font-heading mb-1">${leader.driver_name}</h2>
                                    <div class="text-accent text-xl">${leader.constructor_name}</div>
                                    <div class="mt-2 font-bold">${leader.points} Pts | ${leader.wins} Wins</div>
                                </div>
                            </div>
                         `;
                    }
                }
            }

            const tbody = document.querySelector('#driver-standings-table tbody');
            tbody.innerHTML = '';

            const labels = [];
            const dataPoints = [];

            standings.forEach(s => {
                const tr = document.createElement('tr');
                tr.className = 'standing-row';
                const teamClass = this.getTeamClass(s.constructor_name);
                if (teamClass) tr.classList.add(teamClass);

                tr.innerHTML = `
                    <td class="pos-cell text-center font-bold">${s.position}</td>
                    <td class="font-bold">${s.driver_name}</td>
                    <td class="text-gray-400">${s.constructor_name}</td>
                    <td class="text-right">${s.wins}</td>
                    <td class="text-right font-bold text-accent">${s.points}</td>
                `;
                tbody.appendChild(tr);

                // Top 10 for chart
                if (s.position <= 10) {
                    labels.push(s.driver_name.split(' ').pop()); // Last name
                    dataPoints.push(s.points);
                }
            });

            this.renderChart('driversChart', labels, dataPoints, 'Driver Points');

        } catch (e) {
            console.error(e);
        }
    }

    async loadConstructorStandings() {
        try {
            const response = await fetch(`/api/standings/constructors?season=${this.currentSeason}`);
            const standings = await response.json();

            const tbody = document.querySelector('#constructor-standings-table tbody');
            tbody.innerHTML = '';

            const labels = [];
            const dataPoints = [];

            standings.forEach(s => {
                const tr = document.createElement('tr');
                tr.className = 'standing-row';
                const teamClass = this.getTeamClass(s.constructor_name);
                if (teamClass) tr.classList.add(teamClass);

                tr.innerHTML = `
                    <td class="pos-cell text-center font-bold">${s.position}</td>
                    <td class="font-bold">${s.constructor_name}</td>
                    <td class="text-right">${s.wins}</td>
                    <td class="text-right font-bold text-accent">${s.points}</td>
                `;
                tbody.appendChild(tr);

                labels.push(s.constructor_name);
                dataPoints.push(s.points);
            });

            this.renderChart('constructorsChart', labels, dataPoints, 'Constructor Points');

        } catch (e) {
            console.error(e);
        }
    }

    // --- Hero Section ---
    async updateHero() {
        // Fetch races for 2026 (or 2025 if user selects it, but usually next race is future)
        // Let's assume Next Race is generally in the future relative to "now".
        // We can fetch 2026 schedule to find the first uncompleted race.
        try {
            const resp = await fetch('/api/races?season=2026');
            const races2026 = await resp.json();

            // Find first uncompleted
            const nextRace = races2026.find(r => !r.is_completed) || races2026[0];

            if (nextRace) {
                document.getElementById('next-race-name').innerText = nextRace.name;
                document.getElementById('next-race-date').innerText = new Date(nextRace.date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

                this.targetDate = new Date(nextRace.date); // Midnight on that day
                this.updateCountdown();
            }

            // Render Mini Chart (Top 5 Drivers from PREVIOUS season or current if started)
            // For now, let's load 2025 standings for context
            const stResp = await fetch('/api/standings/drivers?season=2025');
            const standings = await stResp.json();
            const top5 = standings.slice(0, 5);

            const ctx = document.getElementById('miniChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: top5.map(s => s.driver_name.split(' ').pop()),
                    datasets: [{
                        data: top5.map(s => s.points),
                        backgroundColor: ['#ff1e00', '#ffffff', '#a0a0b0', '#555', '#222'],
                        borderWidth: 0
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });

        } catch (e) {
            console.log("Hero update error", e);
        }
    }

    updateCountdown() {
        if (!this.targetDate) return;

        const now = new Date();
        const diff = this.targetDate - now;

        if (diff <= 0) {
            document.getElementById('days').innerText = "00";
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        document.getElementById('days').innerText = days.toString().padStart(2, '0');
        document.getElementById('hours').innerText = hours.toString().padStart(2, '0');
        document.getElementById('mins').innerText = mins.toString().padStart(2, '0');
    }

    // --- Modal ---
    async openRaceDetails(raceId) {
        const modal = document.getElementById('race-modal');
        const modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = '<div class="loading">Loading details...</div>';
        modal.style.display = 'flex';

        try {
            const response = await fetch(`/api/races/${raceId}`);
            const data = await response.json();

            let resultsHtml = '';
            if (data.results && data.results.length > 0) {
                resultsHtml = `
                    <table class="data-table">
                        <thead>
                            <tr><th>Pos</th><th>Driver</th><th>Team</th><th>Time/Gap</th><th>Pts</th></tr>
                        </thead>
                        <tbody>
                            ${data.results.map(r => `
                                <tr>
                                    <td>${r.position}</td>
                                    <td>${r.driver_name}</td>
                                    <td>${r.constructor_name}</td>
                                    <td>${r.time}</td>
                                    <td class="font-bold">${r.points}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } else {
                resultsHtml = '<div class="p-4 text-center">No results available yet.</div>';
            }

            modalBody.innerHTML = `
                <h2 class="mb-2">${data.name}</h2>
                <div class="mb-2 text-accent">${data.circuit}</div>
                <img src="${data.circuit_image}" class="full-width mb-2" style="border-radius: 8px; max-height: 300px; object-fit: contain;">
                ${resultsHtml}
            `;

        } catch (e) {
            modalBody.innerHTML = '<div class="error">Error loading details.</div>';
        }
    }

    // --- Charts ---
    renderChart(canvasId, labels, data, label) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = document.getElementById(canvasId).getContext('2d');
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: 'rgba(255, 30, 0, 0.6)',
                    borderColor: 'rgba(255, 30, 0, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#aaa' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#aaa' }
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });
    }

    // --- Masonry Logic ---
    resizeMasonryItem(item) {
        const grid = document.getElementsByClassName('masonry-grid')[0];
        if (!grid) return;

        const rowHeight = parseInt(window.getComputedStyle(grid).getPropertyValue('grid-auto-rows'));
        const rowGap = parseInt(window.getComputedStyle(grid).getPropertyValue('gap'));

        const rowSpan = Math.ceil((item.querySelector('.card-content').getBoundingClientRect().height + item.querySelector('.card-image-container').getBoundingClientRect().height + rowGap) / (rowHeight + rowGap));

        item.style.gridRowEnd = 'span ' + (rowSpan);
    }

    resizeAllMasonryItems() {
        const allItems = document.getElementsByClassName('race-card');
        for (let i = 0; i < allItems.length; i++) {
            this.resizeMasonryItem(allItems[i]);
        }
    }

    initMasonry() {
        // Expose to window for onload events in HTML
        window.app = this;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new F1App();
});
