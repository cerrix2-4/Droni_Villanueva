// API Wrapper con gestione errori
async function api(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(endpoint, options);
    const result = await response.json();
    
    if (!response.ok) {
        throw new Error(result.error || 'Errore nella richiesta');
    }
    
    return result;
}

// Funzioni autenticazione
async function register(name, email, password) {
    return await api('/api/auth/register', 'POST', { name, email, password });
}

async function login(email, password) {
    return await api('/api/auth/login', 'POST', { email, password });
}

async function logout() {
    await api('/api/auth/logout', 'POST');
    window.location.href = '/';
}

async function getCurrentUser() {
    try {
        return await api('/api/auth/me');
    } catch {
        return null;
    }
}

// Aggiorna navbar con info utente
async function updateNavbar() {
    const user = await getCurrentUser();
    const userInfo = document.getElementById('userInfo');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (user) {
        userInfo.textContent = `👤 ${user.name} (${user.role === 'admin' ? 'Admin' : 'Cliente'})`;
        logoutBtn.style.display = 'block';
    } else {
        userInfo.textContent = '';
        logoutBtn.style.display = 'none';
    }
}

// Event listener logout
document.addEventListener('DOMContentLoaded', () => {
    updateNavbar();
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});
