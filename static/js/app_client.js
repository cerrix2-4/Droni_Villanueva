// Variabili globali
let map = null;
let trackingInterval = null;
let currentMissionId = null;
let polyline = null;
let marker = null;

// Carica ordini del cliente
async function loadOrders() {
    try {
        const orders = await api('/api/orders');
        const ordersList = document.getElementById('ordersList');
        
        if (orders.length === 0) {
            ordersList.innerHTML = '<p class="text-center text-muted py-3">Nessun ordine trovato</p>';
            return;
        }
        
        ordersList.innerHTML = orders.map(order => {
            const statusClass = order.status === 'in corso' ? 'warning' : 
                               order.status === 'completata' ? 'success' : 
                               order.status === 'annullata' ? 'danger' : 'secondary';
            
            return `
                <div class="card mb-2 cursor-pointer" onclick="selectOrder(${order.id})">
                    <div class="card-body">
                        <h6 class="card-title">Ordine #${order.id}</h6>
                        <p class="mb-1"><small><strong>Tipo:</strong> ${order.type}</small></p>
                        <p class="mb-1"><small><strong>Peso:</strong> ${order.total_weight} kg</small></p>
                        <p class="mb-1"><small><strong>Indirizzo:</strong> ${order.address}</small></p>
                        <span class="badge bg-${statusClass}">${order.status || 'in attesa'}</span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Errore caricamento ordini:', error);
        document.getElementById('ordersList').innerHTML = 
            '<p class="text-center text-danger py-3">Errore caricamento ordini</p>';
    }
}

// Seleziona e mostra dettaglio ordine
async function selectOrder(orderId) {
    try {
        // Ferma tracking precedente
        stopTracking();
        
        const data = await api(`/api/orders/${orderId}`);
        
        // Nascondi placeholder
        document.getElementById('selectOrderPlaceholder').classList.add('d-none');
        
        // Mostra dettaglio
        const orderDetail = document.getElementById('orderDetail');
        orderDetail.classList.remove('d-none');
        
        document.getElementById('detailOrderId').textContent = data.order.id;
        document.getElementById('detailType').textContent = data.order.type;
        document.getElementById('detailWeight').textContent = data.order.total_weight;
        document.getElementById('detailAddress').textContent = data.order.address;
        
        const statusBadge = document.getElementById('detailStatus');
        const status = data.mission ? data.mission.status : 'in attesa';
        statusBadge.textContent = status;
        statusBadge.className = 'badge bg-' + (
            status === 'in corso' ? 'warning' : 
            status === 'completata' ? 'success' : 
            status === 'annullata' ? 'danger' : 'secondary'
        );
        
        // Prodotti
        const productsDiv = document.getElementById('detailProducts');
        if (data.products.length > 0) {
            productsDiv.innerHTML = '<ul class="list-group">' + 
                data.products.map(p => `
                    <li class="list-group-item d-flex justify-content-between">
                        <span>${p.name} (x${p.quantity})</span>
                        <span class="text-muted">${p.weight} kg</span>
                    </li>
                `).join('') + '</ul>';
        } else {
            productsDiv.innerHTML = '<p class="text-muted">Nessun prodotto</p>';
        }
        
        // Missione
        const missionDiv = document.getElementById('detailMission');
        if (data.mission) {
            missionDiv.innerHTML = `
                <div class="alert alert-info">
                    <p class="mb-1"><strong>Drone:</strong> ${data.mission.drone || 'Non assegnato'}</p>
                    <p class="mb-0"><strong>Pilota:</strong> ${data.mission.pilot || 'Non assegnato'}</p>
                </div>
            `;
            
            // Se missione in corso, mostra mappa
            if (data.mission.status === 'in corso' && data.order.mission_id) {
                currentMissionId = data.order.mission_id;
                showMap();
                startTracking(data.order.mission_id);
            } else {
                hideMap();
            }
            
            // Se missione completata, mostra form valutazione
            if (data.mission.status === 'completata') {
                await loadMissionRating(data.order.mission_id);
            } else {
                document.getElementById('ratingForm').classList.add('d-none');
            }
        } else {
            missionDiv.innerHTML = '<p class="text-muted">Nessuna missione assegnata</p>';
            hideMap();
            document.getElementById('ratingForm').classList.add('d-none');
        }
    } catch (error) {
        console.error('Errore dettaglio ordine:', error);
        alert('Errore nel caricamento del dettaglio');
    }
}

// Mostra mappa
function showMap() {
    document.getElementById('mapContainer').classList.remove('d-none');
    
    if (!map) {
        map = L.map('map').setView([45.4642, 9.1900], 13);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }
    
    setTimeout(() => map.invalidateSize(), 100);
}

// Nascondi mappa
function hideMap() {
    document.getElementById('mapContainer').classList.add('d-none');
    stopTracking();
}

// Avvia tracking GPS
function startTracking(missionId) {
    stopTracking();
    
    // Prima chiamata immediata
    updateTrack(missionId);
    
    // Polling ogni 3 secondi
    trackingInterval = setInterval(() => updateTrack(missionId), 3000);
}

// Ferma tracking
function stopTracking() {
    if (trackingInterval) {
        clearInterval(trackingInterval);
        trackingInterval = null;
    }
    
    // Pulisci mappa
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null;
    }
    if (marker) {
        map.removeLayer(marker);
        marker = null;
    }
}

// Aggiorna traccia sulla mappa
async function updateTrack(missionId) {
    try {
        const tracks = await api(`/api/missions/${missionId}/tracks`);
        
        if (tracks.length === 0) return;
        
        // Rimuovi traccia precedente
        if (polyline) map.removeLayer(polyline);
        if (marker) map.removeLayer(marker);
        
        // Converti in coordinate Leaflet
        const latLngs = tracks.map(t => [t.lat, t.lng]);
        
        // Disegna polyline
        polyline = L.polyline(latLngs, { color: 'blue', weight: 3 }).addTo(map);
        
        // Marker sull'ultimo punto
        const lastPoint = tracks[tracks.length - 1];
        marker = L.marker([lastPoint.lat, lastPoint.lng])
            .addTo(map)
            .bindPopup(`🚁 Drone<br>Ultimo aggiornamento: ${lastPoint.timestamp}`);
        
        // Zoom su traccia
        map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
    } catch (error) {
        console.error('Errore aggiornamento traccia:', error);
    }
}

// Carica valutazione missione
async function loadMissionRating(missionId) {
    try {
        const mission = await api(`/api/missions/${missionId}`);
        
        const ratingForm = document.getElementById('ratingForm');
        
        if (mission.rating) {
            // Missione già valutata
            ratingForm.innerHTML = `
                <div class="card-header bg-warning">
                    <h5 class="mb-0">⭐ Valutazione Inviata</h5>
                </div>
                <div class="card-body">
                    <p><strong>Voto:</strong> ${mission.rating}/10</p>
                    <p><strong>Commento:</strong> ${mission.comment || 'Nessun commento'}</p>
                </div>
            `;
            ratingForm.classList.remove('d-none');
        } else {
            // Mostra form per valutare
            ratingForm.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Errore caricamento valutazione:', error);
    }
}

// Submit valutazione
document.getElementById('submitRatingForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const rating = document.getElementById('rating').value;
    const comment = document.getElementById('comment').value;
    
    if (!currentMissionId) return;
    
    try {
        await api(`/api/missions/${currentMissionId}/rating`, 'POST', { rating, comment });
        
        alert('Valutazione inviata con successo!');
        document.getElementById('ratingForm').classList.add('d-none');
        
        // Ricarica dettaglio
        const orderId = document.getElementById('detailOrderId').textContent;
        selectOrder(parseInt(orderId));
    } catch (error) {
        alert('Errore invio valutazione: ' + error.message);
    }
});

// Inizializzazione
document.addEventListener('DOMContentLoaded', () => {
    loadOrders();
});
