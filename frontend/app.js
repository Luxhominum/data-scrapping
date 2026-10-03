/**
 * PETA UMKM — Apify Platform Client & Console Controller
 */

document.addEventListener("DOMContentLoaded", () => {
    // State
    let actorsList = [];
    let runsList = [];
    let activeActor = null;
    let map = null;
    let markersLayer = null;
    let pollInterval = null;

    // View Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.apify-view');
    const viewTitle = document.getElementById('current-view-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetViewId = item.getAttribute('data-view');
            navItems.forEach(n => n.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));
            
            item.classList.add('active');
            const targetView = document.getElementById(targetViewId);
            if (targetView) targetView.classList.add('active');

            if (targetViewId === 'store-view') viewTitle.innerText = 'ACTOR STORE · MODULAR SCRAPERS';
            else if (targetViewId === 'runs-view') {
                viewTitle.innerText = 'RUNS & EXECUTION HISTORY';
                loadRuns();
            }
            else if (targetViewId === 'datasets-view') {
                viewTitle.innerText = 'DATASETS & STORAGE SYSTEM';
                loadDatasetsDropdown();
            }
            else if (targetViewId === 'map-view') {
                viewTitle.innerText = 'SPATIAL GEOLOCATION INTELLIGENCE';
                if (!map) initMap();
                loadMapEntities();
            }
            else if (targetViewId === 'api-view') viewTitle.innerText = 'APIFY REST API V2 & DEVELOPER DOCS';
        });
    });

    // Initialize Map
    function initMap() {
        map = L.map('umkm-map', {
            zoomControl: true,
            attributionControl: false
        }).setView([-7.25, 110.5], 7);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd'
        }).addTo(map);

        markersLayer = L.layerGroup().addTo(map);

        map.on('mousemove', (e) => {
            document.getElementById('hud-coordinates').innerText = `LAT: ${e.latlng.lat.toFixed(4)} | LNG: ${e.latlng.lng.toFixed(4)} | ZOOM: ${map.getZoom()}`;
        });
    }

    async function loadMapEntities() {
        if (!markersLayer) return;
        markersLayer.clearLayers();
        try {
            const res = await fetch('/api/umkm');
            const data = await res.json();
            const validCoords = [];

            data.forEach(u => {
                if (u.latitude && u.longitude && u.latitude !== 0.0) {
                    const icon = L.divIcon({
                        className: 'custom-leaflet-marker',
                        html: `<div style="background:#10B981; width:12px; height:12px; border-radius:50%; border:2px solid #FFF; box-shadow:0 0 8px #10B981;"></div>`,
                        iconSize: [12, 12],
                        iconAnchor: [6, 6]
                    });
                    const marker = L.marker([u.latitude, u.longitude], { icon: icon });
                    marker.bindPopup(`
                        <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:160px; color:#18181B;">
                            <strong style="font-size:12px;">${u.name}</strong><br>
                            <span style="font-size:10px; color:#71717A;">${u.city} · ${u.category}</span>
                            ${u.whatsapp ? `<br><a href="https://wa.me/${u.whatsapp}" target="_blank" style="font-size:10px; color:#10B981; font-weight:700;">Chat WhatsApp</a>` : ''}
                        </div>
                    `);
                    markersLayer.addLayer(marker);
                    validCoords.push([u.latitude, u.longitude]);
                }
            });

            if (validCoords.length > 0 && map) {
                map.fitBounds(L.latLngBounds(validCoords), { padding: [50, 50], maxZoom: 12 });
            }
        } catch (e) {
            console.error("Error loading map entities:", e);
        }
    }

    // Load Stats
    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('stat-total-umkm').innerText = data.total_umkm;
        } catch (e) {
            console.error("Error loading stats:", e);
        }
    }

    // 1. Actor Store: Load and Render Actors
    async function loadActorsStore() {
        try {
            const res = await fetch('/api/v2/acts');
            const json = await res.json();
            actorsList = json.data || [];
            document.getElementById('stat-total-actors').innerText = actorsList.length;

            const container = document.getElementById('actors-store-container');
            container.innerHTML = actorsList.map(actor => `
                <div class="actor-card">
                    <div>
                        <div class="actor-header">
                            <div class="actor-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                            </div>
                            <span class="actor-category-badge">${actor.category}</span>
                        </div>
                        <h3 class="actor-title">${actor.name}</h3>
                        <p class="actor-desc">${actor.description}</p>
                    </div>
                    <div>
                        <div class="actor-meta-row font-mono">
                            <span>ID: ${actor.actor_id}</span>
                            <span>v${actor.version}</span>
                        </div>
                        <button class="btn btn-primary btn-block" style="margin-top: 0.85rem;" onclick="window.openLaunchModal('${actor.actor_id}')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                            Launch Actor
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            console.error("Error loading actors:", e);
        }
    }

    // Launch Modal & Dynamic Schema Generator
    window.openLaunchModal = function(actorId) {
        const actor = actorsList.find(a => a.actor_id === actorId);
        if (!actor) return;

        activeActor = actor;
        document.getElementById('modal-actor-name').innerText = `Launch: ${actor.name}`;
        document.getElementById('modal-actor-id').innerText = actor.actor_id;
        document.getElementById('modal-actor-desc').innerText = actor.description;

        const fieldsContainer = document.getElementById('dynamic-schema-fields');
        const schema = actor.input_schema || {};

        fieldsContainer.innerHTML = Object.entries(schema).map(([key, field]) => {
            const isTextarea = field.type === 'string' && key.includes('urls');
            const inputHtml = isTextarea ? `
                <textarea id="field-${key}" name="${key}" class="text-input font-mono" rows="3" ${field.required ? 'required' : ''}>${field.default || ''}</textarea>
            ` : `
                <input type="${field.type === 'integer' ? 'number' : 'text'}" id="field-${key}" name="${key}" value="${field.default !== undefined ? field.default : ''}" class="text-input" ${field.required ? 'required' : ''}>
            `;

            return `
                <div class="form-group">
                    <label for="field-${key}">${field.title || key} ${field.required ? '<span style="color:var(--accent-emerald)">*</span>' : ''}</label>
                    ${inputHtml}
                    ${field.description ? `<span class="form-helper">${field.description}</span>` : ''}
                </div>
            `;
        }).join('');

        document.getElementById('launch-actor-modal').classList.add('show');
    };

    document.getElementById('btn-close-launch').addEventListener('click', () => {
        document.getElementById('launch-actor-modal').classList.remove('show');
    });

    // Handle Launch Form Submit
    document.getElementById('launch-actor-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!activeActor) return;

        const formData = {};
        const schema = activeActor.input_schema || {};
        for (const key of Object.keys(schema)) {
            const input = document.getElementById(`field-${key}`);
            if (input) {
                formData[key] = input.value;
            }
        }

        const webhookUrl = document.getElementById('input-webhook-url').value.trim();
        const submitBtn = document.getElementById('btn-submit-actor-run');
        submitBtn.disabled = true;
        submitBtn.innerText = "Triggering Run...";

        try {
            const res = await fetch(`/api/v2/acts/${activeActor.actor_id}/runs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input: formData, webhook_url: webhookUrl })
            });
            const data = await res.json();
            
            document.getElementById('launch-actor-modal').classList.remove('show');
            alert(`Execution started! Run ID: ${data.data.run_id}`);
            
            // Switch to Runs tab
            document.querySelector('[data-view="runs-view"]').click();
        } catch (err) {
            alert('Failed to trigger run: ' + err.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Start Execution Run`;
        }
    });

    // 2. Runs & History: Load & Polling
    async function loadRuns() {
        try {
            const res = await fetch('/api/v2/actor-runs');
            const json = await res.json();
            runsList = json.data || [];
            document.getElementById('stat-total-runs').innerText = runsList.length;

            const tbody = document.getElementById('runs-table-body');
            if (runsList.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding:2rem;">Belum ada riwayat eksekusi. Jalankan Actor dari Store!</td></tr>`;
                return;
            }

            tbody.innerHTML = runsList.map(r => `
                <tr>
                    <td class="font-mono" style="font-weight:700; color:var(--text-primary);">${r.run_id}</td>
                    <td>${r.actor_name}</td>
                    <td><span class="status-badge status-${r.status}">${r.status}</span></td>
                    <td class="font-mono text-muted" style="font-size:0.75rem;">${r.started_at ? new Date(r.started_at).toLocaleTimeString() : '-'}</td>
                    <td class="font-mono">${r.duration_sec ? r.duration_sec + 's' : 'Running...'}</td>
                    <td class="font-mono font-bold">${r.item_count || 0}</td>
                    <td>
                        <div style="display:flex; gap:0.4rem;">
                            <button class="btn btn-outline" style="font-size:0.65rem; padding:0.25rem 0.5rem;" onclick="window.viewRunLogs('${r.run_id}')">Logs</button>
                            <button class="btn btn-primary" style="font-size:0.65rem; padding:0.25rem 0.5rem;" onclick="window.viewDataset('${r.dataset_id}')">Dataset</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error("Error loading runs:", e);
        }
    }

    // Live Logs Viewer
    window.viewRunLogs = async function(runId) {
        document.getElementById('logs-run-id').innerText = runId;
        const viewer = document.getElementById('run-logs-viewer');
        viewer.innerText = "Loading live logs...";
        document.getElementById('logs-modal').classList.add('show');

        try {
            const res = await fetch(`/api/v2/actor-runs/${runId}/logs`);
            const logsText = await res.text();
            viewer.innerText = logsText || "No logs recorded.";
            viewer.scrollTop = viewer.scrollHeight;
        } catch (e) {
            viewer.innerText = "Error fetching logs: " + e.message;
        }
    };

    document.getElementById('btn-close-logs').addEventListener('click', () => {
        document.getElementById('logs-modal').classList.remove('show');
    });

    // 3. Datasets & Storage
    async function loadDatasetsDropdown() {
        try {
            const res = await fetch('/api/v2/actor-runs');
            const json = await res.json();
            const runs = json.data || [];
            const select = document.getElementById('select-dataset');

            if (runs.length === 0) {
                select.innerHTML = `<option value="">Belum ada dataset</option>`;
                return;
            }

            select.innerHTML = runs.map(r => `
                <option value="${r.dataset_id}">${r.dataset_id} — ${r.actor_name} (${r.item_count || 0} items)</option>
            `).join('');

            if (runs.length > 0) {
                window.viewDataset(runs[0].dataset_id);
            }
        } catch (e) {
            console.error("Error loading datasets dropdown:", e);
        }
    }

    document.getElementById('select-dataset').addEventListener('change', (e) => {
        const datasetId = e.target.value;
        if (datasetId) window.viewDataset(datasetId);
    });

    window.viewDataset = async function(datasetId) {
        document.querySelector('[data-view="datasets-view"]').click();
        const select = document.getElementById('select-dataset');
        select.value = datasetId;

        document.getElementById('dataset-preview-title').innerText = `DATASET: ${datasetId}`;
        document.getElementById('btn-dl-json').onclick = () => window.open(`/api/v2/datasets/${datasetId}/items`, '_blank');
        document.getElementById('btn-dl-csv').onclick = () => window.open(`/api/v2/datasets/${datasetId}/csv`, '_blank');
        document.getElementById('btn-dl-excel').onclick = () => window.open(`/api/v2/datasets/${datasetId}/excel`, '_blank');

        try {
            const res = await fetch(`/api/v2/datasets/${datasetId}/items`);
            const items = await res.json();
            document.getElementById('dataset-items-count').innerText = `${items.length} items`;

            const thead = document.getElementById('dataset-table-head');
            const tbody = document.getElementById('dataset-table-body');

            if (!items || items.length === 0) {
                thead.innerHTML = '';
                tbody.innerHTML = `<tr><td style="text-align:center; color:var(--text-muted); padding:2rem;">Dataset kosong atau sedang diproses.</td></tr>`;
                return;
            }

            const keys = Object.keys(items[0]);
            thead.innerHTML = `<tr>${keys.map(k => `<th>${k.toUpperCase()}</th>`).join('')}</tr>`;
            tbody.innerHTML = items.map(row => `
                <tr>${keys.map(k => `<td class="font-mono" style="font-size:0.75rem;">${row[k] !== undefined ? String(row[k]) : '-'}</td>`).join('')}</tr>
            `).join('');
        } catch (e) {
            console.error("Error previewing dataset:", e);
        }
    };

    // Reset DB Handler
    document.getElementById('btn-purge-db').addEventListener('click', async () => {
        if (!confirm("Reset database dan bersihkan riwayat scraping?")) return;
        try {
            await fetch('/api/purge', { method: 'POST' });
            alert("Database berhasil dibersihkan!");
            loadStats();
            loadRuns();
            if (map) loadMapEntities();
        } catch (e) {
            alert("Error: " + e.message);
        }
    });

    // Auto-polling for active runs
    pollInterval = setInterval(() => {
        const activeRunsView = document.getElementById('runs-view').classList.contains('active');
        if (activeRunsView) {
            loadRuns();
        }
    }, 4000);

    // Initial Start
    loadStats();
    loadActorsStore();
    loadRuns();
});
