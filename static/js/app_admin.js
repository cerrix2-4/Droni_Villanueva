// Variabili globali
let allDrones = [];
let allPilots = [];
let allMissions = [];
let statsChart = null;

// ===== DASHBOARD KPI =====
async function loadDashboard() {
    try {
        const data = await api('/api/admin/dashboard');
        
        document.getElementById('k_in').textContent = data.missions_in_progress;
        document.getElementById('k_ok').textContent = data.missions_completed;
        document.getElementById('k_cancel').textContent = data.missions_cancelled;
        document.getElementById('k_peso').textContent = data.avg_order_weight + ' kg';
        document.getElementById('k_voto').textContent = data.avg_rating + '/10';
    } catch (error) {
        console.error('Errore caricamento dashboard:', error);
    }
}

// ===== GESTIONE DRONI =====
async function loadDrones() {
    try {
        allDrones = await api('/api/admin/drones');
        const tbody = document.getElementById('dronesTable');
        
        if (allDrones.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nessun drone trovato</td></tr>';
            return;
        }
        
        tbody.innerHTML = allDrones.map(drone => `
            <tr>
                <td>${drone.id}</td>
                <td>${drone.model}</td>
                <td>${drone.battery}%</td>
                <td>${drone.capacity}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editDrone(${drone.id})">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteDrone(${drone.id})">🗑️</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Errore caricamento droni:', error);
    }
}

function openDroneModal(drone = null) {
    const modal = document.getElementById('droneModal');
    const title = document.getElementById('droneModalTitle');
    const form = document.getElementById('droneForm');
    
    if (drone) {
        title.textContent = 'Modifica Drone';
        document.getElementById('droneId').value = drone.id;
        document.getElementById('droneModel').value = drone.model;
        document.getElementById('droneBattery').value = drone.battery;
        document.getElementById('droneCapacity').value = drone.capacity;
    } else {
        title.textContent = 'Aggiungi Drone';
        form.reset();
        document.getElementById('droneId').value = '';
    }
}

function editDrone(droneId) {
    const drone = allDrones.find(d => d.id === droneId);
    if (drone) {
        openDroneModal(drone);
        new bootstrap.Modal(document.getElementById('droneModal')).show();
    }
}

async function deleteDrone(droneId) {
    if (!confirm('Sei sicuro di voler eliminare questo drone?')) return;
    
    try {
        await api(`/api/admin/drones/${droneId}`, 'DELETE');
        alert('Drone eliminato con successo');
        loadDrones();
    } catch (error) {
        alert('Errore eliminazione drone: ' + error.message);
    }
}

document.getElementById('droneForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const droneId = document.getElementById('droneId').value;
    const model = document.getElementById('droneModel').value;
    const battery = parseInt(document.getElementById('droneBattery').value);
    const capacity = parseFloat(document.getElementById('droneCapacity').value);
    
    try {
        if (droneId) {
            await api(`/api/admin/drones/${droneId}`, 'PUT', { model, battery, capacity });
            alert('Drone aggiornato con successo');
        } else {
            await api('/api/admin/drones', 'POST', { model, battery, capacity });
            alert('Drone creato con successo');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('droneModal')).hide();
        loadDrones();
    } catch (error) {
        alert('Errore salvataggio drone: ' + error.message);
    }
});

// ===== GESTIONE PILOTI =====
async function loadPilots() {
    try {
        allPilots = await api('/api/admin/pilots');
        const tbody = document.getElementById('pilotsTable');
        
        if (allPilots.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nessun pilota trovato</td></tr>';
            return;
        }
        
        tbody.innerHTML = allPilots.map(pilot => `
            <tr>
                <td>${pilot.id}</td>
                <td>${pilot.name}</td>
                <td>${pilot.surname}</td>
                <td>${pilot.shift}</td>
                <td>${pilot.license}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editPilot(${pilot.id})">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deletePilot(${pilot.id})">🗑️</button>
                </td>
            </tr>
        `).join('');
        
        // Popola filtro piloti
        populatePilotFilter();
    } catch (error) {
        console.error('Errore caricamento piloti:', error);
    }
}

function openPilotModal(pilot = null) {
    const modal = document.getElementById('pilotModal');
    const title = document.getElementById('pilotModalTitle');
    const form = document.getElementById('pilotForm');
    
    if (pilot) {
        title.textContent = 'Modifica Pilota';
        document.getElementById('pilotId').value = pilot.id;
        document.getElementById('pilotName').value = pilot.name;
        document.getElementById('pilotSurname').value = pilot.surname;
        document.getElementById('pilotShift').value = pilot.shift;
        document.getElementById('pilotLicense').value = pilot.license;
    } else {
        title.textContent = 'Aggiungi Pilota';
        form.reset();
        document.getElementById('pilotId').value = '';
    }
}

function editPilot(pilotId) {
    const pilot = allPilots.find(p => p.id === pilotId);
    if (pilot) {
        openPilotModal(pilot);
        new bootstrap.Modal(document.getElementById('pilotModal')).show();
    }
}

async function deletePilot(pilotId) {
    if (!confirm('Sei sicuro di voler eliminare questo pilota?')) return;
    
    try {
        await api(`/api/admin/pilots/${pilotId}`, 'DELETE');
        alert('Pilota eliminato con successo');
        loadPilots();
    } catch (error) {
        alert('Errore eliminazione pilota: ' + error.message);
    }
}

document.getElementById('pilotForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const pilotId = document.getElementById('pilotId').value;
    const name = document.getElementById('pilotName').value;
    const surname = document.getElementById('pilotSurname').value;
    const shift = document.getElementById('pilotShift').value;
    const license = document.getElementById('pilotLicense').value;
    
    try {
        if (pilotId) {
            await api(`/api/admin/pilots/${pilotId}`, 'PUT', { name, surname, shift, license });
            alert('Pilota aggiornato con successo');
        } else {
            await api('/api/admin/pilots', 'POST', { name, surname, shift, license });
            alert('Pilota creato con successo');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('pilotModal')).hide();
        loadPilots();
    } catch (error) {
        alert('Errore salvataggio pilota: ' + error.message);
    }
});

// ===== GESTIONE MISSIONI =====
async function loadMissions() {
    try {
        const stato = document.getElementById('f_stato').value;
        const pilotaId = document.getElementById('f_pilota').value;
        const droneId = document.getElementById('f_drone').value;
        const dal = document.getElementById('f_dal').value;
        const al = document.getElementById('f_al').value;
        
        const params = new URLSearchParams();
        if (stato) params.append('stato', stato);
        if (pilotaId) params.append('pilota_id', pilotaId);
        if (droneId) params.append('drone_id', droneId);
        if (dal) params.append('dal', dal);
        if (al) params.append('al', al);
        
        allMissions = await api('/api/admin/missions?' + params.toString());
        const tbody = document.getElementById('missionsTable');
        
        if (allMissions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">Nessuna missione trovata</td></tr>';
            return;
        }
        
        tbody.innerHTML = allMissions.map(mission => {
            const statusClass = mission.status === 'in corso' ? 'warning' : 
                               mission.status === 'completata' ? 'success' : 'danger';
            
            return `
                <tr>
                    <td>${mission.id}</td>
                    <td>${mission.date}</td>
                    <td>${mission.time}</td>
                    <td>${mission.drone_model || 'N/A'}</td>
                    <td>${mission.pilot_name || 'N/A'}</td>
                    <td>
                        <select class="form-select form-select-sm" onchange="updateMissionStatus(${mission.id}, this.value)">
                            <option value="in corso" ${mission.status === 'in corso' ? 'selected' : ''}>In corso</option>
                            <option value="completata" ${mission.status === 'completata' ? 'selected' : ''}>Completata</option>
                            <option value="annullata" ${mission.status === 'annullata' ? 'selected' : ''}>Annullata</option>
                        </select>
                    </td>
                    <td>${mission.rating ? mission.rating + '/10' : '-'}</td>
                    <td>
                        <span class="badge bg-${statusClass}">${mission.status}</span>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Errore caricamento missioni:', error);
    }
}

async function updateMissionStatus(missionId, newStatus) {
    try {
        await api(`/api/admin/missions/${missionId}`, 'PUT', { status: newStatus });
        alert('Stato missione aggiornato');
        loadMissions();
        loadDashboard();
    } catch (error) {
        alert('Errore aggiornamento stato: ' + error.message);
        loadMissions();
    }
}

function populatePilotFilter() {
    const select = document.getElementById('f_pilota');
    select.innerHTML = '<option value="">Tutti i piloti</option>' +
        allPilots.map(p => `<option value="${p.id}">${p.name} ${p.surname}</option>`).join('');
}

function populateDroneFilter() {
    const select = document.getElementById('f_drone');
    select.innerHTML = '<option value="">Tutti i droni</option>' +
        allDrones.map(d => `<option value="${d.id}">${d.model}</option>`).join('');
}

function exportCSV() {
    if (allMissions.length === 0) {
        alert('Nessun dato da esportare');
        return;
    }
    
    const headers = ['ID', 'Data', 'Ora', 'Drone', 'Pilota', 'Stato', 'Valutazione'];
    const rows = allMissions.map(m => [
        m.id,
        m.date,
        m.time,
        m.drone_model || '',
        m.pilot_name || '',
        m.status,
        m.rating || ''
    ]);
    
    let csv = headers.join(',') + '\n';
    csv += rows.map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `missioni_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

// ===== STATISTICHE =====
async function loadStats() {
    try {
        const data = await api('/api/admin/stats');
        
        const ctx = document.getElementById('statsChart');
        
        if (statsChart) {
            statsChart.destroy();
        }
        
        statsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'In Corso',
                        data: data.in_corso,
                        backgroundColor: '#ffc107'
                    },
                    {
                        label: 'Completate',
                        data: data.completata,
                        backgroundColor: '#28a745'
                    },
                    {
                        label: 'Annullate',
                        data: data.annullata,
                        backgroundColor: '#dc3545'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Errore caricamento statistiche:', error);
    }
}

// ===== INIZIALIZZAZIONE =====
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    loadDrones();
    loadPilots();
    loadMissions();
    
    // Event listener per cambio tab
    document.getElementById('stats-tab')?.addEventListener('shown.bs.tab', () => {
        loadStats();
    });
    
    // Popola filtri droni
    setTimeout(() => {
        populateDroneFilter();
    }, 500);
});
