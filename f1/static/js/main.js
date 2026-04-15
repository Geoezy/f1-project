class F1App {
    constructor() {
        this.races = [];
        this.targetDate = null;
        this.currentView = 'schedule';
        this.init();
    }

    async init() {
        // Init logic
        this.setupNavigation();

        // Load initial data (2026 for upcoming season)
        await this.loadRaces(2026);
        this.startCountdown();

        this.loadDrivers();
        this.loadConstructors();
    }

    setupNavigation() {
        // Main Nav
        document.querySelectorAll('.nav-item').forEach(btn => {
            // Click handled by onclick attribute to calls app.switchView
        });

        // Modal Close
        const modal = document.getElementById('race-modal');
        const closeBtn = document.querySelector('.close-modal');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }
        window.onclick = (event) => {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        };

        // Year Selector (Results)
        const yearSelect = document.getElementById('results-year-select');
        if (yearSelect) {
            yearSelect.addEventListener('change', (e) => {
                this.loadRaces(e.target.value);
            });
        }

        // Results Sub-tabs
        document.querySelectorAll('.results-subnav button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchResultsTab(e.target.dataset.tab);
            });
        });
    }

    switchView(viewName) {
        // Hide all views
        document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
        const target = document.getElementById(`${viewName}-view`);
        if (target) target.style.display = 'block';

        // Update Nav Active State
        document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active', 'bg-gray-800'));
        // Find button (approximate match)
        document.querySelectorAll('.nav-item').forEach(btn => {
            if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(viewName)) {
                btn.classList.add('active', 'bg-gray-800');
            }
        });

        this.currentView = viewName;
    }

    switchResultsTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.results-tab-content').forEach(el => el.style.display = 'none');

        // Show target
        const target = document.getElementById(`results-content-${tabName}`);
        if (target) target.style.display = 'block';

        // Update Buttons
        document.querySelectorAll('.results-subnav button').forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.remove('text-gray-400');
                btn.classList.add('bg-accent', 'text-white');
            } else {
                btn.classList.add('text-gray-400');
                btn.classList.remove('bg-accent', 'text-white');
            }
        });
    }

    async loadRaces(season) {
        // Toggle loading?

        try {
            const response = await fetch(`/api/races?season=${season}`);
            this.races = await response.json();

            this.renderRaces(this.races); // For Schedule View
            this.renderResults(this.races); // For Results View -> Races Tab

            // Also load standings for this season for Results View
            this.loadResultDrivers(season);
            this.loadResultTeams(season);

            this.updateNextRace();
            this.updateSeasonProgress();

        } catch (e) {
            console.error("Error loading races:", e);
        }
    }

    // --- Renderers for Results View ---

    async loadResultDrivers(season) {
        try {
            const res = await fetch(`/api/standings/drivers?season=${season}`);
            const data = await res.json();
            const tbody = document.getElementById('results-drivers-list');
            if (!tbody) return;

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center p-6 text-gray-500">No standings data available.</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(d => `
                <tr class="hover:bg-white/5 group cursor-pointer transition-colors border-b border-gray-800" onclick="app.switchView('drivers')"> 
                    <td class="p-4 font-bold text-white text-center">${d.position}</td>
                    <td class="p-4 font-bold flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full bg-gray-700 overflow-hidden border border-gray-600">
                             <img src="${d.image_url || '/static/images/driver_placeholder.png'}" 
                                  class="w-full h-full object-cover"
                                  onerror="this.src='https://placehold.co/100x100/333/FFF.png?text=Driver'">
                        </div>
                        <span class="group-hover:text-accent transition-colors">${d.driver_name}</span>
                    </td>
                    <td class="p-4 text-gray-400 uppercase font-mono text-xs">${d.country_code}</td>
                    <td class="p-4 text-gray-300">${d.constructor_name}</td>
                    <td class="p-4 text-right font-bold text-accent text-lg">${d.points}</td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); }
    }

    async loadResultTeams(season) {
        try {
            const res = await fetch(`/api/standings/constructors?season=${season}`);
            const data = await res.json();
            const tbody = document.getElementById('results-teams-list');
            if (!tbody) return;

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center p-6 text-gray-500">No standings data available.</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(t => `
                <tr class="hover:bg-white/5 cursor-pointer border-b border-gray-800" onclick="app.switchView('constructors')">
                    <td class="p-4 font-bold text-white text-center">${t.position}</td>
                    <td class="p-4 font-bold flex items-center gap-6">
                        ${t.car_image_url ? `<img src="${t.car_image_url}" class="w-24 h-8 object-contain">` : ''}
                        <span class="text-lg">${t.constructor_name}</span>
                    </td>
                    <td class="p-4 text-right font-bold text-accent text-lg">${t.points}</td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); }
    }

    renderResults(races) {
        const tbody = document.getElementById('results-list');
        if (!tbody) return;
        tbody.innerHTML = '';

        const completed = races.filter(r => r.is_completed);
        if (completed.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center p-8 text-gray-500 font-mono">NO RACES COMPLETED YET</td></tr>';
            return;
        }

        completed.forEach(r => {
            const row = document.createElement('tr');
            row.className = 'border-b border-gray-800 hover:bg-white/5 cursor-pointer transition-colors group';
            row.onclick = () => this.openRaceModal(r.id);

            row.innerHTML = `
                <td class="p-4 text-gray-500 font-mono text-xs font-bold">R${r.round}</td>
                <td class="p-4 font-bold text-white text-lg group-hover:text-accent transition-colors">${r.name.replace(' Grand Prix', '')}</td>
                <td class="p-4 text-gray-400 text-sm font-mono">${new Date(r.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</td>
                <td class="p-4 font-bold text-white flex items-center gap-2">
                     <span class="text-xs bg-gray-800 text-gray-400 px-1 rounded border border-gray-700">P1</span> ${r.winner_driver_name || '-'}
                </td>
                <td class="p-4 text-gray-400 text-sm">${r.winner_team || '-'}</td>
                <td class="p-4 text-right font-mono text-accent font-bold">${r.winner_time || '-'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // --- Schedule View Renderer ---
    renderRaces(races) {
        const list = document.getElementById('races-list');
        if (!list) return;
        list.innerHTML = '';

        // Flag Mapping
        const flagMap = {
            "Bahrain": "🇧🇭", "Saudi Arabia": "🇸🇦", "Australia": "🇦🇺", "Japan": "🇯🇵", "China": "🇨🇳",
            "Miami": "🇺🇸", "Emilia Romagna": "🇮🇹", "Monaco": "🇲🇨", "Canada": "🇨🇦", "Spain": "🇪🇸",
            "Austria": "🇦🇹", "Great Britain": "🇬🇧", "Hungary": "🇭🇺", "Belgium": "🇧🇪", "Netherlands": "🇳🇱",
            "Italy": "🇮🇹", "Azerbaijan": "🇦🇿", "Singapore": "🇸🇬", "United States": "🇺🇸", "Mexico": "🇲🇽",
            "Brazil": "🇧🇷", "Las Vegas": "🇺🇸", "Qatar": "🇶🇦", "Abu Dhabi": "🇦🇪"
        };

        races.forEach(r => {
            const card = document.createElement('div');
            card.className = `glass-panel p-0 overflow-hidden group hover:border-f1red transition-all duration-300 relative ${r.is_completed ? 'opacity-75 hover:opacity-100' : ''}`;

            let flag = '🏁';
            for (const [key, value] of Object.entries(flagMap)) {
                if (r.name.includes(key) || r.circuit.includes(key)) {
                    flag = value;
                    break;
                }
            }

            const date = new Date(r.date);
            const isPast = r.is_completed;

            card.innerHTML = `
                <div class="h-1 bg-gradient-to-r from-gray-700 to-gray-800 group-hover:from-f1red group-hover:to-orange-600 transition-all"></div>
                <div class="p-5">
                    <div class="flex justify-between items-start mb-4">
                        <div class="text-xs font-mono text-gray-500 font-bold">ROUND ${r.round}</div>
                        <div class="text-2xl">${flag}</div>
                    </div>
                    <div class="mb-4">
                         <h3 class="text-xl font-bold font-heading leading-tight mb-1 group-hover:text-white text-gray-200">${r.name.replace(' Grand Prix', '')}</h3>
                         <div class="text-sm text-gray-500 truncate">${r.circuit}</div>
                    </div>
                    
                    <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-800">
                        <div class="flex flex-col">
                             <span class="text-xs text-gray-500 uppercase font-bold text-center bg-gray-800 rounded px-2 py-0.5 mb-1">${date.toLocaleDateString(undefined, { month: 'short' })}</span>
                             <span class="text-2xl font-bold font-mono text-center">${date.getDate()}</span>
                        </div>
                        
                        ${isPast ? `
                           <button onclick="app.openRaceModal(${r.id})" class="px-2 py-1 bg-gray-800 hover:bg-white hover:text-black rounded text-xs transition-colors font-bold uppercase tracking-wider">
                               Results >
                           </button>
                        ` : `
                           <div class="text-xs text-green-500 animate-pulse font-bold uppercase tracking-wider border border-green-900 bg-green-900/20 px-2 py-1 rounded">
                               Upcoming
                           </div>
                        `}
                    </div>
                </div>
             `;
            list.appendChild(card);
        });
    }

    // --- Modal Logic ---
    async openRaceModal(raceId) {
        const modal = document.getElementById('race-modal');
        const modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = '<div class="p-10 text-center"><div class="animate-spin rounded-full h-10 w-10 border-b-2 border-f1red mx-auto mb-4"></div>Fetching Race Data...</div>';
        modal.style.display = 'flex';

        try {
            const response = await fetch(`/api/races/${raceId}`);
            const data = await response.json();

            // Fetch detailed results (classification)
            let classificationHtml = '';
            if (data.is_completed) {
                const resultsData = data.results || [];

                if (resultsData.length > 0) {
                    classificationHtml = `
                        <div class="mt-8">
                            <h4 class="text-lg font-bold mb-4 uppercase tracking-wider border-b border-gray-700 pb-2">Race Classification</h4>
                            <div class="overflow-x-auto">
                                <table class="w-full text-left text-sm">
                                    <thead>
                                        <tr class="text-gray-500 uppercase text-xs">
                                            <th class="pb-2">Pos</th>
                                            <th class="pb-2 text-center">Grid</th>
                                            <th class="pb-2">Driver</th>
                                            <th class="pb-2">Team</th>
                                            <th class="pb-2 text-center">Laps</th>
                                            <th class="pb-2 text-right">Status / Gap</th>
                                            <th class="pb-2 text-right">Pts</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-gray-800">
                                        ${resultsData.map(r => `
                                            <tr class="hover:bg-white/5">
                                                <td class="py-2 font-bold ${r.position <= 3 ? 'text-accent' : 'text-gray-400'}">${r.position}</td>
                                                <td class="py-2 text-center text-gray-500 text-xs">${r.grid}</td>
                                                <td class="py-2 font-bold">${r.driver_name}</td>
                                                <td class="py-2 text-gray-400 text-xs">${r.constructor_name}</td>
                                                <td class="py-2 text-center text-gray-500 font-mono text-xs">${r.laps}</td>
                                                <td class="py-2 text-right font-mono text-gray-400 text-xs">${r.reason !== 'Finished' ? r.reason : (r.time || '+')}</td>
                                                <td class="py-2 text-right font-bold text-white">${r.points}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                     `;
                }
            }

            modalBody.innerHTML = `
                <div class="flex flex-col md:flex-row gap-6">
                    <div class="w-full md:w-1/3">
                         <img src="${data.circuit_image || '/static/images/placeholder_circuit.png'}" 
                              class="w-full h-auto bg-white/5 rounded-lg p-2 border border-gray-700 mb-4"
                              onerror="this.src='https://placehold.co/400x300/222/FFF.png?text=Preview'">
                         
                         <div class="grid grid-cols-2 gap-4 text-center">
                              <div class="bg-gray-800 p-2 rounded">
                                  <div class="text-xs text-gray-500 uppercase">Round</div>
                                  <div class="font-bold text-xl">${data.round}</div>
                              </div>
                              <div class="bg-gray-800 p-2 rounded">
                                  <div class="text-xs text-gray-500 uppercase">Status</div>
                                  <div class="font-bold text-xl ${data.is_completed ? 'text-accent' : 'text-gray-400'}">${data.is_completed ? 'Finished' : 'Upcoming'}</div>
                              </div>
                         </div>
                    </div>
                    
                    <div class="w-full md:w-2/3">
                        <h2 class="text-3xl font-heading font-bold italic mb-1">${data.name}</h2>
                        <div class="text-xl text-gray-400 mb-6">${data.circuit}</div>
                        
                        <!-- Podium / Winner -->
                         ${data.winner_driver_name ? `
                            <div class="bg-gradient-to-r from-gray-800 to-transparent p-4 rounded-lg border-l-4 border-accent mb-6">
                                <div class="text-xs text-accent uppercase font-bold mb-1">Race Winner</div>
                                <div class="text-2xl font-bold flex items-center gap-3">
                                     ${data.winner_driver_image ? `<img src="${data.winner_driver_image}" class="w-10 h-10 rounded-full border border-gray-500">` : ''}
                                     ${data.winner_driver_name}
                                </div>
                                <div class="text-sm text-gray-400 mt-1">${data.winner_time}</div>
                            </div>
                         ` : ''}
                         
                         ${classificationHtml}
                    </div>
                </div>
            `;

        } catch (e) {
            console.error(e);
            modalBody.innerHTML = '<div class="text-red-500 p-4">Error loading details.</div>';
        }
    }

    async updateNextRace() {
        const nameEl = document.getElementById('next-race-name');
        const dateEl = document.getElementById('next-race-date');

        try {
            const response = await fetch('/api/races/next');
            if (response.ok) {
                const next = await response.json();
                nameEl.innerText = next.name;
                dateEl.innerText = new Date(next.date).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
                this.targetDate = new Date(next.date).getTime();
            } else {
                nameEl.innerText = "SEASON COMPLETED";
                dateEl.innerText = "";
                this.targetDate = null;
            }
        } catch (e) {
            console.error("Error fetching next race:", e);
            nameEl.innerText = "UNAVAILABLE";
            this.targetDate = null;
        }
    }

    startCountdown() {
        setInterval(() => {
            if (!this.targetDate) return;
            const now = new Date().getTime();
            const d = this.targetDate - now;

            if (d < 0) {
                document.getElementById('countdown').innerText = "00 : 00 : 00 : 00";
                return;
            }

            const days = Math.floor(d / (1000 * 60 * 60 * 24));
            const hours = Math.floor((d % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((d % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((d % (1000 * 60)) / 1000);

            document.getElementById('countdown').innerText =
                `${days.toString().padStart(2, '0')} : ${hours.toString().padStart(2, '0')} : ${minutes.toString().padStart(2, '0')} : ${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    updateSeasonProgress() {
        const total = this.races.length;
        if (total === 0) return;
        const completed = this.races.filter(r => r.is_completed).length;
        const pct = Math.round((completed / total) * 100);

        const bar = document.getElementById('season-progress');
        const txt = document.getElementById('season-progress-text');
        if (bar) bar.style.width = `${pct}%`;
        if (txt) txt.innerText = `${pct}% Complete`;
    }

    // --- Load Main Cards for Drivers/Teams Views ---
    async loadDrivers() {
        const grid = document.getElementById('drivers-grid');
        if (!grid) return;

        // Always load 2026 drivers for "Profile" view
        const response = await fetch('/api/standings/drivers?season=2026');
        let drivers = await response.json();

        // If 2026 empty (no results yet), fallback to 2025 but maybe label it? 
        // User wants 2026 info. I should check if API returns empty for 2026.
        if (drivers.length === 0) {
            // Load 2025? No, user wants 2026. If my ingestion didn't get drivers for 2026, 
            // I should revert to mock/seed data.
            // My app.py logic calculates from Results. If no 2026 results, it returns empty
            // UNLESS I add logic to app.py to return all drivers for 2026 even with 0 points.
            // I did that for 2025. I should do it for 2026 too.
            const res2025 = await fetch('/api/standings/drivers?season=2025');
            drivers = await res2025.json();
        }

        grid.innerHTML = drivers.map(d => `
            <div class="glass-panel p-0 overflow-hidden group relative">
                 <div class="h-64 bg-gray-800 relative overflow-hidden">
                      <img src="${d.image_url || '/static/images/driver_placeholder.png'}" 
                           class="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-110"
                           onerror="this.src='https://placehold.co/400x500/333/FFF.png?text='">
                      <div class="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-black/80 to-transparent"></div>
                      <div class="absolute bottom-4 left-4">
                           <div class="text-4xl font-bold font-heading italic text-white leading-none">${d.position > 0 ? d.position : '-'}</div>
                           <div class="text-xs text-gray-400 uppercase">Season 2026</div>
                      </div>
                 </div>
                 <div class="p-5 relative">
                      <div class="absolute top-0 right-4 transform -translate-y-1/2 w-12 h-8 rounded border border-gray-600 overflow-hidden shadow-lg">
                           <div class="w-full h-full bg-gray-700 flex items-center justify-center text-xs font-bold">${d.country_code}</div>
                      </div>
                      
                      <h3 class="text-2xl font-bold mb-1">${d.driver_name}</h3>
                      <div class="text-accent font-bold uppercase text-sm tracking-wider mb-4">${d.constructor_name}</div>
                      
                      <div class="grid grid-cols-2 gap-4 border-t border-gray-700 pt-4">
                           <div>
                               <div class="text-xs text-gray-500 uppercase">Points</div>
                               <div class="font-bold text-xl">${d.points}</div>
                           </div>
                           <div>
                               <div class="text-xs text-gray-500 uppercase">Podiums</div>
                               <div class="font-bold text-xl">${d.podiums || 0}</div>
                           </div>
                      </div>
                 </div>
            </div>
        `).join('');
    }

    async loadConstructors() {
        const grid = document.getElementById('teams-grid');
        if (!grid) return;

        let response = await fetch('/api/standings/constructors?season=2026');
        let teams = await response.json();

        if (teams.length === 0) {
            response = await fetch('/api/standings/constructors?season=2025');
            teams = await response.json();
        }

        grid.innerHTML = teams.map(t => `
            <div class="glass-panel p-0 overflow-hidden group">
                 <div class="h-40 bg-cardbg p-4 flex items-center justify-center relative overflow-hidden">
                      <img src="${t.car_image_url || ''}" 
                           class="w-full h-full object-contain transition-transform duration-500 group-hover:scale-110"
                           onerror="this.src='https://placehold.co/400x200/333/FFF.png?text=F1+Car'">
                 </div>
                 <div class="p-6">
                      <div class="flex justify-between items-center mb-2">
                           <h3 class="text-2xl font-bold">${t.constructor_name}</h3>
                           <span class="text-3xl font-heading text-gray-600 font-bold">${t.position > 0 ? t.position : '-'}</span>
                      </div>
                      <div class="space-y-2">
                           <div class="flex justify-between border-b border-gray-800 pb-2">
                               <span class="text-gray-400 text-sm">Points</span>
                               <span class="font-bold text-accent">${t.points}</span>
                           </div>
                           <div class="flex justify-between border-b border-gray-800 pb-2">
                               <span class="text-gray-400 text-sm">Base</span>
                               <span class="text-right text-xs">${t.base || 'Unknown'}</span>
                           </div>
                      </div>
                      ${t.sponsors ? `
                      <div class="mt-4">
                           <div class="text-xs text-gray-500 uppercase tracking-widest mb-1">Key Partners</div>
                           <div class="text-xs text-gray-400 truncate">${t.sponsors}</div>
                      </div>` : ''}
                 </div>
            </div>
        `).join('');
    }
}

// Init
window.app = new F1App();
